import re
from typing import List, Optional, Tuple

from api.text_processing.objects import Block, TextBlock, Header, Chapter, Section


class BlockMerger:
    def __init__(self):
        self._block_end_word_wrap_regex = r"(?<=[A-Za-zА-Яа-я])-\n*$"
        self._word_wrap_regex = r"(?<=[A-Za-zА-Яа-я])-\n(?=[a-zа-я]+)"
        self._chapter_num = r"^(Глава|ГЛАВА)\s\d+"
        self._section_num = r"^\d+\.+(\d+\.*)+\s+"
        self._chapter_header_regex = r""

    def process(self, blocks: List[TextBlock]):
        blocks.sort(key=lambda block: [-block.page, block.bbox[1]])
        blocks.reverse()
        merged_blocks = self._merge_word_wraps(blocks)
        merged_blocks = self.find_headers(merged_blocks)
        merged_blocks = self.structure_by_headers(merged_blocks)
        return merged_blocks

    def _merge_word_wraps(self, blocks: List[TextBlock]):
        merge_with_next = False
        ids_to_merge = []
        for block in blocks:

            if block.type == "text":
                if merge_with_next:
                    ids_to_merge[-1].append(block.id)
                    merge_with_next = False
                if re.search(self._block_end_word_wrap_regex, block.text):
                    merge_with_next = True
                    ids_to_merge.append([block.id])

        return self.merge(blocks, ids_to_merge)

    def _create_text_block_from(self, block: TextBlock, text: str) -> TextBlock:
        return TextBlock(
            metadata=block.metadata,
            page=block.page,
            bbox=block.bbox,
            text=text
        )

    def find_headers(self, blocks: List[TextBlock]):
        header_blocks = []
        blocks_to_add = []
        for block in blocks:
            if block.type == "header":
                block.type = "page_header"
            if block.type == "text":
                if "\n" in block.text and block.text.find("\n") != len(block.text) - 1:
                    parts = block.text.split("\n", 1)
                    block.text = parts[0]
                    new_block = self._create_text_block_from(block, parts[1])
                    i = blocks.index(block)
                    blocks.insert(i + 1, new_block)
                    blocks_to_add.append(new_block)

                chapter = re.search(self._chapter_num, block.text)
                section = re.search(self._section_num, block.text)
                contents = re.search(r"О\s*Г\s*Л\s*А\s*В\s*Л\s*Е\s*Н\s*И\s*Е\s*|Оглавление|Содержание|СОДЕРЖАНИЕ",
                                     block.text)

                if chapter:
                    header_blocks.append(
                        Header(
                            id=block.id,
                            metadata=block.metadata,
                            page=block.page,
                            bbox=block.bbox,
                            text=block.text,
                            type="chapter_header"
                        )
                    )
                if section:
                    header_blocks.append(
                        Header(
                            id=block.id,
                            metadata=block.metadata,
                            page=block.page,
                            bbox=block.bbox,
                            text=block.text,
                            type="section_header"
                        )
                    )
                if contents:
                    header_blocks.append(
                        Header(
                            id=block.id,
                            metadata=block.metadata,
                            page=block.page,
                            bbox=block.bbox,
                            text=block.text,
                            type="contents_header"
                        )
                    )
        header_blocks_ids = [header.id for header in header_blocks]
        blocks = [block for block in blocks if block.type != "page_header"]
        for i, block in enumerate(blocks):
            if block.id in header_blocks_ids:
                header_block = next(h for h in header_blocks if h.id == block.id)
                blocks[i] = header_block

        return blocks

    def structure_by_headers(self, blocks: List[TextBlock]) -> List[Chapter]:
        chapters: List[Chapter] = []
        current_chapter: Optional[Chapter] = None
        section_stack: List[Tuple[Section, str]] = []  # кортеж (секция, номер_секции)

        def get_section_level(header_text: str) -> str:
            # Извлекаем номер секции (например, из "1.2.3. Название" получаем "1.2.3")
            match = re.match(r'(^\d+\.+(\d+\.*)+)', header_text.strip())
            return match.group(1) if match else ""

        def is_subsection(parent_num: str, child_num: str) -> bool:
            # Проверяем, является ли child_num подсекцией parent_num
            # Например: "1.1.1." является подсекцией "1.1."
            if not parent_num.endswith("."):
                parent_num += "."
            return child_num.startswith(parent_num)

        for block in blocks:
            if block.type == "chapter_header":
                current_chapter = Chapter(title=block.text)
                chapters.append(current_chapter)
                section_stack.clear()

            elif block.type == "section_header":
                if current_chapter is None:
                    current_chapter = Chapter(title="")
                    chapters.append(current_chapter)

                section_number = get_section_level(block.text)
                new_section = Section(title=block.text)

                # Очищаем стек от секций, которые не являются родительскими для текущей
                while section_stack and not is_subsection(section_stack[-1][1], section_number):
                    section_stack.pop()

                if not section_stack:
                    # Это секция верхнего уровня
                    current_chapter.content.append(new_section)
                else:
                    # Это подсекция
                    parent_section = section_stack[-1][0]
                    parent_section.sections.append(new_section)

                section_stack.append((new_section, section_number))

            else:
                # Обработка обычных блоков
                if current_chapter is None:
                    current_chapter = Chapter(title="")
                    chapters.append(current_chapter)

                if section_stack:
                    # Добавляем блок в последнюю активную секцию
                    section_stack[-1][0].blocks.append(block)
                else:
                    # Добавляем блок напрямую в главу
                    current_chapter.content.append(block)

        return chapters

    def merge(self, blocks: List[TextBlock], ids_to_merge):
        blocks_to_remove = []
        for merge_group in ids_to_merge:
            merged_block = self._find_block_by_id(blocks, merge_group[0])
            for block_id in merge_group[1:]:
                block = self._find_block_by_id(blocks, block_id)
                merged_block.text += block.text
                blocks_to_remove.append(block)
            merged_block.text = re.sub(self._word_wrap_regex, "", merged_block.text)

        blocks = [block for block in blocks if block not in blocks_to_remove]

        return blocks

    def _find_block_by_id(self, blocks, block_id):
        for block in blocks:
            if block.id == block_id:
                return block
        return None
