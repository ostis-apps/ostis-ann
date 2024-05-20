import base64
from typing import List
from sc_kpm import ScKeynodes
from sc_kpm.sc_result import ScResult
from sc_kpm.utils import create_node, create_link, create_edge
from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType
from sc_client.models.sc_construction import ScLinkContentType
from sc_client.models import ScAddr, ScEventParams, ScTemplate
from sc_client.client import events_create, is_event_valid, template_search, get_link_content
from sc_client.constants.sc_types import EDGE_ACCESS_CONST_POS_PERM as COM_CON
from sc_client.constants.sc_types import EDGE_D_COMMON_CONST as NREL_CON
from sc_client.constants.sc_types import NODE_CONST_CLASS as COM_CLASS
from sc_client.constants.sc_types import NODE_CONST_NOROLE as COM_NOROLE
from sc_client.constants.sc_types import NODE_CONST as COM_NODE
from sc_client.constants.sc_types import NODE_CONST_STRUCT as COM_STRUCT
from sc_client.constants.sc_types import LINK_VAR, NODE_VAR_STRUCT, EDGE_D_COMMON_VAR, EDGE_ACCESS_VAR_POS_PERM
from .text_converter import generate_sc
from sc_kpm import ScAgentClassic
from sc_client.models import ScEvent
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)

class LanguageTranslator(ScAgentClassic):
    def __init__(self) -> None:
        super().__init__("sc_translator_agent")

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        pass

    def _register(self) -> ScEvent:
        base_structure = ScKeynodes.resolve("ostis_ann_chats_history", sc_type=COM_CLASS)
        template = ScTemplate()
        template.triple(base_structure, EDGE_ACCESS_VAR_POS_PERM, NODE_VAR_STRUCT)
        template_result = template_search(template)
        for triples in template_result:
            event_type = ScEventType.ADD_OUTGOING_EDGE
            event_params = ScEventParams(triples[2], event_type, self.run) #triples[2] нода чата
            sc_event = events_create(event_params)
            status = is_event_valid(sc_event[0])
        return sc_event[0]
    
    def run(self, src: ScAddr, edge: ScAddr, trg: ScAddr) -> None:
        template = ScTemplate()
        template.triple_with_relation(
            trg,
            EDGE_D_COMMON_VAR,
            LINK_VAR,
            EDGE_ACCESS_VAR_POS_PERM,
            ScKeynodes.resolve("nrel_text_prompt",COM_NOROLE),
        )
        template_result = template_search(template)
        text_prompt = get_link_content(template_result[0][2]) # текст с линки читаем
        struct_node = self.__create_question_structure(text=text_prompt)
        if struct_node:
            nrel_con_1 = create_edge(NREL_CON, trg, struct_node)
            create_edge(COM_CON, ScKeynodes.resolve("nrel_struct_pointer", COM_NOROLE), nrel_con_1)
        else:
            logging.warn('Сообщение не являлось задачей классификации/регрессии')
    
    def __create_com_edge(self, src, trg) -> ScAddr:
        return create_edge(COM_CON, src, trg)

    def __create_question_structure(self, text: str, image: base64 = None) -> ScAddr|None:
        que_type, sc_code = generate_sc(text)
        if que_type == 'classification':
            return self.__create_classify_question(sc_code[0], image)
        elif que_type == 'regression':
            return self.__create_regression_structure(sc_code)
        elif que_type == 'NULL':
            return None

    def __create_classify_question(self, node_name: str, image: base64 = None) -> ScAddr:
        elements = dict()
        elements["tuple_1"] = create_node(sc_types.NODE_CONST_TUPLE)
        elements["tuple_2"] = create_node(sc_types.NODE_CONST_TUPLE)
        elements["null_1"] = create_node(COM_NODE)
        elements["null_2"] = create_node(COM_NODE)
        elements["base64"] = create_link(content=base64, content_type=ScLinkContentType.STRING)
        elements["concept_format_png"] = ScKeynodes.resolve("concept_format_png", COM_CLASS)
        elements["concept_image"] = ScKeynodes.resolve("concept_image", COM_CLASS)
        elements["concept_unk"] = ScKeynodes.resolve("concept_unknown_entity", COM_CLASS)
        elements["concept_null"] = create_node(COM_CLASS)
        elements["{node_name}"] = ScKeynodes.resolve(node_name, COM_CLASS)
        elements["nrel_translation"] = ScKeynodes.resolve("nrel_sc_text_translation", sc_types.NODE_CONST_NOROLE)
        elements["nrel_entities"] = ScKeynodes.resolve("nrel_entities_on_image", sc_types.NODE_CONST_NOROLE)
        elements["com_con_1"] = self.__create_com_edge(elements["tuple_1"], elements["base64"])
        elements["com_con_2"] = self.__create_com_edge(elements["concept_format_png"], elements["base64"])
        elements["nrel_con_1"] = create_edge(NREL_CON, elements["tuple_1"], elements["null_1"])
        elements["nrel_con_2"] = create_edge(NREL_CON, elements["null_1"], elements["tuple_2"])
        elements["com_con_4"] = self.__create_com_edge(elements["nrel_translation"], elements["nrel_con_1"])
        elements["com_con_5"] = self.__create_com_edge(elements["concept_image"], elements["null_1"])
        elements["com_con_6"] = self.__create_com_edge(elements["nrel_entities"], elements["nrel_con_2"])
        elements["com_con_7"] = self.__create_com_edge(elements["tuple_2"], elements["null_2"])
        elements["com_con_8"] = self.__create_com_edge(elements["concept_null"], elements["null_2"])
        elements["com_con_9"] = self.__create_com_edge(elements["concept_unk"], elements["concept_null"])
        elements["com_con_10"] = self.__create_com_edge(elements["{node_name}"], elements["concept_null"])
        struct_node = create_node(COM_STRUCT)
        for element in elements.values():
            self.__create_com_edge(struct_node, element)
        return struct_node

    def __create_regression_structure(self, args: List[str]) -> ScAddr:
        elements = dict()
        elements["{args[0]}"] = ScKeynodes.resolve(args[0], COM_CLASS) # entity - concept_car
        elements["{args[1]}"] = ScKeynodes.resolve(args[1], COM_CLASS) # measure - concept_cost
        elements["{args[2]}"] = ScKeynodes.resolve(args[2], COM_CLASS) # entity to measure - concept_engine
        elements["{args[3]}"] = ScKeynodes.resolve(args[3], sc_types.NODE_CONST_NOROLE) # nrel_measurement_in_ some metric 
        elements["{args[4]}"] = ScKeynodes.resolve(args[4], COM_CLASS) # concept_number
        elements["value"] = create_link(content=float(args[5]), content_type=ScLinkContentType.FLOAT) # link value of metric - 4
        elements["concept_unknown_value"] = ScKeynodes.resolve("concept_unknown_value", COM_CLASS)
        elements["nrel_idtf"] = ScKeynodes.resolve("nrel_idtf", sc_types.NODE_CONST_NOROLE)
        elements["concept_null_1"] = create_node(COM_CLASS)
        elements["concept_null_2"] = create_node(COM_CLASS)
        elements["null_1"] = create_node(COM_NODE)
        elements["null_2"] = create_node(COM_NODE)
        elements["com_con_1"] = self.__create_com_edge(elements["{args[0]}"], elements["null_1"])
        elements["com_con_2"] = self.__create_com_edge(elements["concept_null_1"], elements["null_1"])
        elements["com_con_3"] = self.__create_com_edge(elements["concept_null_2"], elements["null_1"])
        elements["com_con_4"] = self.__create_com_edge(elements["{args[1]}"], elements["concept_null_1"]) 
        elements["com_con_5"] = self.__create_com_edge(elements["concept_unknown_value"], elements["concept_null_1"])
        elements["com_con_6"] = self.__create_com_edge(elements["{args[2]}"], elements["concept_null_2"])
        elements["nrel_con_1"] = create_edge(NREL_CON, elements["concept_null_2"], elements["null_2"])
        elements["nrel_con_2"] = create_edge(NREL_CON, elements["null_2"], elements["value"])
        elements["com_con_7"] = self.__create_com_edge(elements["{args[3]}"], elements["nrel_con_1"])
        elements["com_con_8"] = self.__create_com_edge(elements["{args[4]}"], elements["null_2"])
        elements["com_con_9"] = self.__create_com_edge(elements["nrel_idtf"], elements["nrel_con_2"])
        struct_node = create_node(COM_STRUCT)
        for element in elements.values():
            self.__create_com_edge(struct_node, element)
        return struct_node