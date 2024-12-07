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
from modules.fnnUseProblemSolvingMethodModule.converters.ImageConverter import ImageConverter

from modules.fnnUseProblemSolvingMethodModule.dataClasses import InterpretationParameters
from tests.fashion_converter import Converter


class UseProblemSolvingMethodAgent(ScAgentClassic):
    def __init__(self) -> None:
        super().__init__("action_use_problem_solving_method")

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        self.logger.info("UseProblemSolvingMethodAgent started")
        result = self.__run(action_element)
        self.logger.info("UseProblemSolvingAgent finished")
        return result

    def __run(self, action_element: ScAddr) -> ScResult:
        # Get Interpretation parameters frim input struct
        reader = InterpretationParametersReader()
        interpretation_parameters: InterpretationParameters = reader.get_interpretation_parameters(action_element)

        model = interpretation_parameters.ann_struct.ann_model
        input_data = ImageConverter.convert_image_to_inputs(interpretation_parameters.input_struct,
                                                            interpretation_parameters.ann_struct.num_of_inputs)

        predictions = model.predict(input_data)
        score = tf.nn.softmax(predictions[0])
        print(numpy.max(score * 100))
        print(score)

        return ScResult.OK
