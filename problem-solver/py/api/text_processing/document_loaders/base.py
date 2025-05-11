from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from pathlib import PurePath
from typing import Optional, Union

from api.text_processing.objects import Document


class BaseLoader(ABC):
    """Interface for Document Loader.

    Implementations should implement the lazy-loading method using generators
    to avoid loading all Documents into memory at once.

    `load` is provided just for user convenience and should not be overridden.
    """

    def load(self) -> Document:
        """Load data into Document objects."""
        return self.lazy_load()

    async def aload(self) -> list[Document]:
        """Load data into Document objects asynchronously."""
        pass

    def load_and_split(
            self, text_splitter: Optional['TextSplitter'] = None,
    ) -> list[Document]:
        _text_splitter = text_splitter
        docs = self.load()
        return _text_splitter.split_documents(docs) if _text_splitter else docs

    def lazy_load(self) -> Document:
        """A lazy loader for Documents."""
        if type(self).load != BaseLoader.load:
            return self.load()
        msg = f"{self.__class__.__name__} does not implement lazy_load()"
        raise NotImplementedError(msg)

    async def alazy_load(self) -> AsyncIterator[Document]:
        """An async lazy loader for Documents."""
        pass


class BaseFileParser(ABC):
    """Abstract interface for file parsers.

       A file parser provides a way to parse raw data stored in a file into one
       or more documents.
       """

    @abstractmethod
    def lazy_parse(self, file_path: Union[str, PurePath]) -> Document:
        """Lazy parsing interface.

        Subclasses are required to implement this method.

        Args:
            file_path: file path

        Returns:
            Generator of documents
        """

    def parse(self, file_path: Union[str, PurePath]) -> Document:
        """Eagerly parse the blob into a document or documents.

        This is a convenience method for interactive development environment.

        Production applications should favor the lazy_parse method instead.

        Subclasses should generally not over-ride this parse method.

        Args:
            file_path: file path

        Returns:
            List of documents
        """
        return self.lazy_parse(file_path)
