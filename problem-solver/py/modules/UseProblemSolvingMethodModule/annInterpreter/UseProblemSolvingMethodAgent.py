import sc_kpm
from sc_client.client import create_elements, template_search, resolve_keynodes
from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType
from sc_client.models import ScAddr, ScTemplate, ScConstruction, ScIdtfResolveParams
from sc_kpm import ScAgentClassic, ScKeynodes
from sc_kpm.sc_result import ScResult
from sc_kpm.utils import get_system_idtf, create_node, create_edge, get_link_content_data
import tensorflow as tf
import numpy

from modules.UseProblemSolvingMethodModule.annInterpreter.InterpretationParametersReader import \
    InterpretationParametersReader
from modules.UseProblemSolvingMethodModule.converters.ImageConverter import ImageConverter

from modules.UseProblemSolvingMethodModule.dataClasses.InterpretationParameters import InterpretationParameters
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
        # Get Interpretation parameters from input struct
        reader = InterpretationParametersReader()
        interpretation_parameters: InterpretationParameters = reader.get_interpretation_parameters(action_element)

        model = interpretation_parameters.ann_struct.ann_model
        input_data = ImageConverter.convert_image_to_inputs(interpretation_parameters.input_struct,
                                                            interpretation_parameters.ann_struct.num_of_inputs)

        predictions = model.predict(input_data)
        score = tf.nn.softmax(predictions[0])
        print(numpy.max(score * 100))
        self.logger.info(f"Object score:{score}")

        self.__save_ann_output(predictions, interpretation_parameters)

        output_construct = ScConstruction()
        output_construct.create_edge(sc_type=sc_types.EDGE_D_COMMON_CONST,
                                     src=action_element,
                                     trg=interpretation_parameters.input_struct.object_addr,
                                     alias='edge')
        output_construct.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM,
                                     sc_kpm.ScKeynodes["nrel_result"],
                                     'edge')
        addresses = create_elements(output_construct)
        assert all(addresses)

        return ScResult.OK

    def __save_ann_output(self, predictions: numpy.array, interpretation_parameters: InterpretationParameters) -> None:
        objet_addr = interpretation_parameters.input_struct.object_addr
        max_prediction: int = numpy.max(tf.nn.softmax(predictions[0]) * 100)
        self.__save_ann_output_to_sc_memory(max_prediction, objet_addr)

    def __save_ann_output_to_sc_memory(self, max_prediction: int, object_addr: ScAddr) -> None:
        self.logger.info(f"Max prediction: {max_prediction}")
        result_node_params = ScIdtfResolveParams(idtf=f'someclass', type=sc_types.NODE_CONST_CLASS)
        result_node_addr = resolve_keynodes(result_node_params)[0]
        construction = ScConstruction()
        construction.create_edge(sc_type=sc_types.EDGE_ACCESS_CONST_FUZ_PERM,
                                 src=result_node_addr,
                                 trg=object_addr,
                                 alias='fuz_edge')
        addresses = create_elements(construction)
        assert len(addresses) == 1
        assert all(addresses)
        fuz_edge_addr = addresses[0]
        self.logger.info(f'Fuz Edge addr:{fuz_edge_addr}')

        probability_node_params = ScIdtfResolveParams(idtf=f'{str(max_prediction)}%', type=sc_types.NODE_CONST_CLASS)
        probability_node_addr = resolve_keynodes(probability_node_params)[0]
        probability_construction = ScConstruction()
        probability_construction.create_edge(sc_type=sc_types.EDGE_ACCESS_CONST_POS_PERM,
                                             src=sc_kpm.ScKeynodes["probability"],
                                             trg=probability_node_addr, )
        probability_construction.create_edge(sc_type=sc_types.EDGE_ACCESS_CONST_POS_PERM,
                                             src=probability_node_addr,
                                             trg=fuz_edge_addr)
        addresses = create_elements(probability_construction)
        assert len(addresses) == 2
        assert all(addresses)
        # fuz_edge_addr = addresses[0]
        self.logger.info(f'Probability created')

        self.logger.info(f"Saved to kb")
