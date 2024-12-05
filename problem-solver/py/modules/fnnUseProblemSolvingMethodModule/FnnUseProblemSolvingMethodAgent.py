from sc_client.client import create_elements, template_search
from sc_client.constants import sc_types
from sc_client.constants.common import ScEventType
from sc_client.models import ScAddr, ScTemplate
from sc_kpm import ScAgentClassic, ScKeynodes
from sc_kpm.sc_result import ScResult
from sc_kpm.utils import get_system_idtf, create_node, create_edge, get_link_content_data
import tensorflow as tf
import numpy
import sys
import os
sys.path.append('/home/dom/ostis/ostis-ann/problem-solver/py/tests/') # Тут прописан костыль, нужно избавиться
from fashion_converter import Converter # Путь к конвертеру сделать через переменную

class FnnUseProblemSolvingMethodAgent(ScAgentClassic):
    def __init__(self)-> None:
        super().__init__("action_use_problem_solving_method")
        
    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        self.logger.info("FnnUseAgent started")
        result = self.__run(action_element)
        self.logger.info("FnnUseAgent finished")
        return result
    
    def __run(self, action_element: ScAddr) -> ScResult:
        template = ScTemplate()
        
        template.triple_with_relation(
            action_element,
            sc_types.EDGE_ACCESS_CONST_FUZ_TEMP,
            sc_types.NODE_CONST_STRUCT,
            sc_types.EDGE_D_COMMON_VAR,
            ScKeynodes["rrel_1"]
        )
        
        template.triple_with_relation(
            action_element,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.LINK_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScKeynodes["nrel_sc_text_translation"]
        )
        
        image_link = template_search(template)[2]
        
        model_link = template_search(template)[2]
        '''
        template.triple_with_relation(
            action_element,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.NODE_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScKeynodes["nrel_converter"]
        )
        
        converter_node = template_search(template)[2]
        
        template.triple_with_relation(
            converter_node,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.LINK_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScKeynodes["nrel_sc_text_translation"]
        )
        '''
        
        model_path = get_link_content_data(model_link)
        data_path = 'problem-solver/py/tests/image_test.png' # Непонятно через что
        
        # Подготовка к выполнению (конвертирование данных и загрузка инс)
        model = tf.keras.models.load_model(model_path)
        model_input_data = Converter.convert(data_path)
        
        # Предсказание в заданой модели с конвертированными данными
        predictions = model.predict(model_input_data)
        score = tf.nn.softmax(predictions[0])
        probability = numpy.max(score*100)//1
        
        
        result_struct = create_node(sc_types.NODE_CONST_STRUCT)
        result_edge = create_edge(action_element, sc_types.EDGE_ACCESS_CONST_POS_PERM, result_struct)
        create_edge("nrel_result", sc_types.EDGE_D_COMMON_CONST, result_edge)
        
        template.triple_with_relation(
            
            
        )
        return ScResult.OK