import logging
from os.path import dirname, abspath
from typing import List

import PIL.Image
import numpy

import numpy as np
import sc_kpm
from sc_client.client import *
from sc_client.constants import sc_types
from sc_client.models import *
from tensorflow.python import keras

from modules.fnnUseProblemSolvingMethodModule.dataClasses.InterpretationParameters import InterpretationParameters
from modules.fnnUseProblemSolvingMethodModule.dataClasses.AnnStruct import AnnStruct
from modules.fnnUseProblemSolvingMethodModule.dataClasses.inputOutput.ImageStruct import Image


# todo: use absolute filepaths?
def get_ann_path() -> str:
    script_directory = dirname(dirname(abspath(__file__)))
    ann_path = dirname(dirname(dirname(dirname(dirname(script_directory)))))
    return ann_path


class InterpretationParametersReader:
    def __init__(self) -> None:
        pass

    def get_interpretation_parameters(self, action_addr: ScAddr) -> InterpretationParameters:
        ann_address = self.__get_ann_address(action_addr)

        ann_input_shape = self.__get_ann_input_shape(ann_address)
        ann_output_shape = self.__get_ann_output_shape(ann_address)

        ann_struct = AnnStruct(ann_address, ann_input_shape, ann_output_shape)

        problem_addr = self.__get_problem_addr(action_addr)
        input_struct = self.__get_image(self.__get_image_addr(problem_addr))

        return InterpretationParameters(ann_struct, input_struct)

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

    # def __get_classes(source_addr: ScAddr) -> List[ScAddr]:
    #     template = ScTemplate()
    #     template.triple(
    #         sc_types.NODE_CLASS,
    #         sc_types.EDGE_ACCESS_VAR_POS_PERM,
    #         source_addr
    #     )
    #
    #     sc_classes = []
    #     for template_result in template_search(template):
    #         sc_classes.append(template_result[2])
    #     return sc_classes

    def __get_problem_addr(self, action_addr: ScAddr) -> ScAddr:
        return self.__get_rrel_target(action_addr, "rrel_1")

    # def __get_problem_types(self, problem_addr: ScAddr) -> List[ScAddr]:
    #     return self.__get_classes(problem_addr)

    def __get_image_addr(self, problem_addr: ScAddr) -> ScAddr:
        return self.__get_rrel_target(problem_addr, "rrel_input_image")

    def __get_file(self, file_addr: ScAddr, nrel_name: str) -> str:
        filepath_link_addr = self.__get_nrel_target_link(file_addr, nrel_name)
        file_filepath = get_link_content(filepath_link_addr)[0].data
        return file_filepath

    def __get_image(self, image_addr: ScAddr) -> Image:
        image_path = self.__get_file(image_addr, "nrel_filepath")
        kb_path = f'{get_ann_path()}/kb'

        image = PIL.Image.open(f'{kb_path}/{image_path}')
        image_struct = Image(numpy.array(image), image_shape=image.size)
        return image_struct

    def __get_ann_address(self, action_addr: ScAddr) -> ScAddr:
        return self.__get_rrel_target(action_addr, "rrel_2")

    def __get_keras_model(self, model_addr: ScAddr) -> keras.Model:
        ann_path = self.__get_file(model_addr, "nrel_keras_ann")
        kb_path = f'{get_ann_path()}/kb'

        model = keras.models.load_model(f"{kb_path}/{ann_path}")
        return model

    def __get_ann_input_shape(self, ann_addr: ScAddr) -> int:
        model = self.__get_keras_model(ann_addr)
        return model.input_shape

    def __get_ann_output_shape(self, ann_addr: ScAddr) -> int:
        model = self.__get_keras_model(ann_addr)
        return model.output_shape
