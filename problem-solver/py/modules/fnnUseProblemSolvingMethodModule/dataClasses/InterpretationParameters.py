from dataclasses import dataclass

from sc_client.models import ScAddr

from inputOutput.InputOutputStruct import InputOutput
from modules.fnnUseProblemSolvingMethodModule.dataClasses.AnnStruct import AnnStruct


@dataclass
class InterpretationParameters:
    ann_struct: AnnStruct
    problem_type: ScAddr        # for instance concept_images_classification
    input_struct: InputOutput   # inputs for ann

