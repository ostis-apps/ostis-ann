from typing import List, Union
from api.text_processing.objects import Document as BaseDocument, Chapter, Section, Block, TextBlock
from langchain_core.documents import Document as LangChainDocument

class ChapterSplitter:
    def __init__(self):
        pass

    def _extract_text_from_blocks(self, blocks: List[Block]) -> str:
        """Извлекает и объединяет текст из списка блоков"""
        texts = []
        for block in blocks:
            if isinstance(block, TextBlock):
                text = block.text.strip()
                if text:  # добавляем только непустые тексты
                    texts.append(text)
        return "\n".join(texts)

    def _process_section(self, section: Section, chapter_title: str, parent_sections: List[str] = None) -> List[LangChainDocument]:
        """Обрабатывает секцию и её подсекции"""
        documents = []
        if parent_sections is None:
            parent_sections = []

        # Собираем путь секций
        current_path = parent_sections + [section.title]
        section_path = " > ".join(current_path)

        # Собираем весь текст секции
        all_section_text = []

        # Добавляем заголовок секции
        if section.title:
            all_section_text.append(f"# {section.title}")

        # Добавляем текст из блоков
        section_text = self._extract_text_from_blocks(section.blocks)
        if section_text:
            all_section_text.append(section_text)

        # Если есть текст в секции, создаем документ
        if all_section_text:
            metadata = {
                "chapter": chapter_title,
                "section_path": section_path,
                "section_title": section.title,
                "section_id": section.id,
                "level": len(current_path)
            }

            documents.append(LangChainDocument(
                page_content="\n\n".join(all_section_text),
                metadata=metadata
            ))

        # Обрабатываем подсекции
        for subsection in section.sections:
            documents.extend(self._process_section(subsection, chapter_title, current_path))

        return documents

    def _process_chapter(self, chapter: Chapter) -> List[LangChainDocument]:
        """Обрабатывает главу"""
        documents = []
        chapter_text = []

        # Добавляем заголовок главы
        if chapter.title:
            chapter_text.append(f"# {chapter.title}")

        # Собираем текст из блоков на уровне главы
        chapter_blocks = [item for item in chapter.content if isinstance(item, Block)]
        if chapter_blocks:
            text = self._extract_text_from_blocks(chapter_blocks)
            if text:
                chapter_text.append(text)

        # Если есть текст на уровне главы, создаем документ
        if len(chapter_text) > 1:  # > 1, потому что первый элемент - это заголовок
            metadata = {
                "chapter": chapter.title,
                "section_path": chapter.title,
                "section_title": "",
                "section_id": chapter.id,
                "level": 1
            }
            documents.append(LangChainDocument(
                page_content="\n\n".join(chapter_text),
                metadata=metadata
            ))

        # Обрабатываем секции
        for content_item in chapter.content:
            if isinstance(content_item, Section):
                documents.extend(self._process_section(content_item, chapter.title))
                
        return documents

    def split_document(self, document: BaseDocument) -> List[LangChainDocument]:
        """
        Разбивает документ на фрагменты, объединяя текст в рамках одной секции.
        
        Args:
            document: Документ для разбиения
            
        Returns:
            Список LangChain Document объектов
        """
        documents = []
        
        for chapter in document.chapters:
            documents.extend(self._process_chapter(chapter))
            
        return documents