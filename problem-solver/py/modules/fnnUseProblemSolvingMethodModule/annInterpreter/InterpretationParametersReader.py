import logging
from typing import List

import numpy as np
import sc_kpm
from sc_client.client import *
from sc_client.constants import sc_types
from sc_client.models import *

from modules.fnnUseProblemSolvingMethodModule.dataClasses import InterpretationParameters


class InterpretationParametersReader:
    def __init__(self) -> None:
        pass

    def get_interpretation_parameters(self, action_addr: ScAddr) -> InterpretationParameters:
        ann_address = self.__get_ann_address(action_addr)
        problem = self.__get_problem(action_addr)
        input_type



        return InterpretationParameters(ann_struct=ann_address,)

    @staticmethod
    def __get_rrel_target(source_addr: ScAddr, rrel_name: str) -> ScAddr:
        template = ScTemplate()
        template.triple_with_relation(
            source_addr,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_kpm.ScKeynodes[rrel_name]
        )
        return template_search(template)[0][2]

    @staticmethod
    def __get_nrel_target_link(source_addr: ScAddr, nrel_name: str) -> ScAddr:
        template = ScTemplate()
        template.triple_with_relation(
            source_addr,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.LINK_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_kpm.ScKeynodes[nrel_name]
        )
        return template_search(template)[0][2]

    @staticmethod
    def __get_classes(source_addr: ScAddr) -> List[ScAddr]:
        template = ScTemplate()
        template.triple(
            source_addr,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_CLASS
        )

        sc_classes = []
        for template_result in template_search(template):
            sc_classes.append(template_result[2])
        return sc_classes

    def __get_aliases(self, sc_classes:List[ScAddr]) -> List[str]:
        for sc_class in sc_classes:
            ScTemplateValueItem

    def __get_problem(self, action_addr: ScAddr) -> ScAddr:
        return self.__get_rrel_target(action_addr, "rrel_1")

    def __get_problem_types(self, problem_addr: ScAddr) -> List[ScAddr]:
        return self.__get_classes(problem_addr)

    def __get_ann_address(self, action_addr: ScAddr) -> ScAddr:
        return self.__get_rrel_target(action_addr, "rrel_2")

    def __get_problem_input(self, problem_addr: ScAddr, input_type:str) -> np.array:
        filepath_link_addr =self.__get_nrel_target_link(problem_addr, input_type)
        file_filepath = get_link_content(filepath_link_addr)[0].data