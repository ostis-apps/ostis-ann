from dataclasses import dataclass
from typing import List

from sc_client.models import ScAddr

from inputOutput.InputOutputStruct import InputOutput
from modules.fnnUseProblemSolvingMethodModule.dataClasses.AnnStruct import AnnStruct


@dataclass
class InterpretationParameters:
    ann_struct: AnnStruct
    input_struct: InputOutput               # inputs for ann
    problem_types: List[ScAddr] = None      # todo or maybe unused


