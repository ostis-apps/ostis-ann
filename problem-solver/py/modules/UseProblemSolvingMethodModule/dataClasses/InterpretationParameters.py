from dataclasses import dataclass
from typing import List

from sc_client.models import ScAddr

from .AnnStruct import AnnStruct
from .inputOutput.ImageStruct import Image


@dataclass
class InterpretationParameters:
    ann_struct: AnnStruct
    input_struct: Image               # inputs for ann
    problem_types: List[ScAddr] = None      # todo or maybe unused


