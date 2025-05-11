from pathlib import PurePath
from typing import Optional, Union, Iterator, List
import os.path

from api.text_processing.document_loaders.parsers.block_mergers import BlockMerger
from api.text_processing.document_loaders.parsers.classifiers import ObjectsClassifier
from api.text_processing.document_loaders.parsers.cleaners import BaseCleaner
from api.text_processing.document_loaders.parsers.extractors import PDFMinerExtractor
from api.text_processing.document_loaders.base import BaseFileParser
from api.text_processing.objects import Document, Block


class PDFMinerParser(BaseFileParser):
    def __init__(
            self,
            *,
            password: Optional[str] = None
    ):
        super().__init__()
        self.password = password
        self.extractor = PDFMinerExtractor(print_logs=True)
        self.object_classifier = ObjectsClassifier()
        self.cleaner = BaseCleaner()
        self.merger = BlockMerger()

    @staticmethod
    def decode_text(s: Union[bytes, str]) -> str:
        from pdfminer.utils import PDFDocEncoding
        if isinstance(s, bytes) and s.startswith(b"\xfe\xff"):
            return str(s[2:], "utf-16be", "ignore")
        try:
            ords = (ord(c) if isinstance(c, str) else c for c in s)
            return "".join(PDFDocEncoding[o] for o in ords)
        except IndexError:
            return str(s)

    def lazy_parse(self, file_path: Union[str, PurePath]):
        try:
            import pdfminer
            from pdfminer.converter import PDFLayoutAnalyzer
            from pdfminer.layout import (
                LAParams
            )
            from pdfminer.pdfpage import PDFPage

        except ImportError:
            raise ImportError(
                "pdfminer package not found, please install it"
                "with `pip install pdfminer.six"
            )
        objects = self.extractor.load(file_path)

        objects = self.object_classifier.classify(objects)
        text_blocks = self._remove_images(objects)

        for text_block in text_blocks:
            text_block.text = self.cleaner.clean(text_block.text)

        self.extractor.save_to_json(text_blocks, f"output.json")

        blocks = self.merger.process(text_blocks)

        document = Document()
        document.filename = os.path.basename(str(file_path))
        document.chapters = blocks
        self.extractor.save_to_json(document, f"output.json")
        return document

    @staticmethod
    def _remove_images(objects) -> List[Block]:
        text_blocks = []
        for obj in objects:
            if obj.type not in ["image"]:
                text_blocks.append(obj)
        return text_blocks

