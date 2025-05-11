import os.path
from abc import ABC
from pathlib import PurePath
from typing import Union, Optional, Iterator, List

from api.text_processing.document_loaders.base import BaseLoader
from api.text_processing.document_loaders.parsers.pdf import PDFMinerParser
from api.text_processing.objects import Document


class BasePDFLoader(BaseLoader, ABC):
    """Base Loader class for `PDF` files."""

    def __init__(
            self, file_path: Union[str, PurePath]
    ):
        self.file_path = str(file_path)
        if "~" in self.file_path:
            self.file_path = os.path.expanduser(self.file_path)


class PDFMinerLoader(BasePDFLoader):
    def __init__(
            self,
            file_path: Union[str, PurePath],
            *,
            password: Optional[str] = None
    ) -> None:
        super().__init__(file_path)
        self.parser = PDFMinerParser(
            password=password
        )
    def lazy_load(self) -> Document:
        file = self.file_path
        return self.parser.lazy_parse(file)

