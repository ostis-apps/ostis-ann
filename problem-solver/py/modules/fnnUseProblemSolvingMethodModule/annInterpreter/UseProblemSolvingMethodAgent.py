from sc_client.client import create_elements, template_search
from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType
from sc_client.models import ScAddr, ScTemplate
from sc_kpm import ScAgentClassic, ScKeynodes
from sc_kpm.sc_result import ScResult
from sc_kpm.utils import get_system_idtf, create_node, create_edge, get_link_content_data
import tensorflow as tf
import numpy

from modules.fnnUseProblemSolvingMethodModule.annInterpreter.InterpretationParametersReader import \
    InterpretationParametersReader

from modules.fnnUseProblemSolvingMethodModule.dataClasses import InterpretationParameters


class UseProblemSolvingMethodAgent(ScAgentClassic):
    def __init__(self) -> None:
        super().__init__("action_use_problem_solving_method")

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        self.logger.info("FnnUseAgent started")
        result = self.__run(action_element)
        self.logger.info("FnnUseAgent finished")
        return result

    def __run(self, action_element: ScAddr) -> ScResult:
        reader = InterpretationParametersReader()
        interpretation_parameters: InterpretationParameters = reader.get_interpretation_parameters(action_element)

        pass
