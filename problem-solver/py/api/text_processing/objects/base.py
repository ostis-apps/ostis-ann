import uuid
from dataclasses import dataclass, field
from pathlib import PurePath

from typing import Union, Dict, Any, Optional, Tuple, List

PathLike = Union[str, PurePath]


@dataclass
class BaseObject:
    """Base class for all objects."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    page: Optional[int] = None
    bbox: Optional[Tuple[float, float, float, float]] = None


@dataclass
class Block(BaseObject):
    """Abstract document block."""
    type: str = field(default="block")


@dataclass
class TextBlock(Block):
    """Text block."""
    text: str = field(default="")
    type: str = field(default="text")


@dataclass
class ImageBlock(Block):
    """Image block."""
    image_path: PathLike = field(default="")
    caption: Optional['ImageCaption'] = None
    text_blocks: List[TextBlock] = field(default_factory=list)
    type: str = field(default="image")


@dataclass
class TableBlock(Block):
    """Table block."""
    table_data: Any = field(default="")
    caption: Optional[str] = None
    type: str = field(default="table")


@dataclass
class Header(TextBlock):
    """Header block."""
    type: str = field(default="header")


@dataclass
class ImageCaption(TextBlock):
    """Image caption block."""
    type: str = field(default="image_caption")


@dataclass
class Section(BaseObject):
    """Section containing a title, blocks, subsections, and a type."""
    title: str = field(default="")
    blocks: List[Block] = field(default_factory=list)
    sections: List['Section'] = field(default_factory=list)
    type: str = field(default="section")


@dataclass
class Chapter(BaseObject):
    """Document chapter containing a title, content (sections and blocks), and a type."""
    title: str = field(default="")
    content: List[Union[Section, Block]] = field(default_factory=list)
    type: str = field(default="chapter")


@dataclass
class Document(BaseObject):
    """Document."""
    filename: str = field(default="")
    chapters: List[Chapter] = field(default_factory=list)
    type: str = field(default="document")
