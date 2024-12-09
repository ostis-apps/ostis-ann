import logging
import sc_kpm
from sc_client.client import *
from sc_client.constants import sc_types
from sc_client.models import *
from sc_client.models import ScAddr, ScConstruction, ScLinkContentType, ScLinkContent
from sc_kpm import ScAgentClassic, ScKeynodes
from sc_kpm.sc_result import ScResult
from sc_kpm.utils import get_system_idtf
from sc_kpm.sc_sets import ScSet

from sc_kpm.utils import get_link_content_data
from typing import Union
import sc_kpm.utils as utils

import os
from kaggle.api.kaggle_api_extended import KaggleApi


class DownloadSamplingSolver(ScAgentClassic):
    def __init__(self) -> None:
        super().__init__("action_download_sampling") 

    def on_event(self, class_node: ScAddr, edge: ScAddr, action_node: ScAddr) -> ScResult:

        self.logger.debug("AGENT STARTED!")
        result = self.__run(action_node)
        is_successful = result == ScResult.OK
        self.logger.debug("AGENT FINISHED!")
        return result 

    def get_link_content_kaggle(self, action_node: ScAddr) -> Union[str, int]:
        link_kaggle = self.__get_download_link(action_node)
        kaggle_url = get_link_content_data(link_kaggle)
        return kaggle_url

    def get_link_content(self, action_node: ScAddr) -> Union[str, int]:
        link_folder = self.__get_download_path(action_node)
        download_path = get_link_content_data(link_folder)
        return download_path

    @staticmethod
    def __get_nrel_target_link(action_node: ScAddr, nrel_name : str) -> ScAddr:
        template = ScTemplate()
        template.triple_with_relation(
            action_node,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.LINK_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_kpm.ScKeynodes[nrel_name]
        )
        return template_search(template)[0][2]

    def __get_download_link(self, action_node: ScAddr) -> ScAddr:
        return self.__get_nrel_target_link(action_node, "nrel_link_kaggle")


    def __get_download_path(self, action_node: ScAddr) -> ScAddr:
        return self.__get_nrel_target_link(action_node, "nrel_link_folder")

    
    def __save_link_to_sc_memory(self, kaggle_url: str,  nrel_name: str, action_node) -> None:
        link = utils.create_link(kaggle_url)
        utils.create_norole_relation(
            action_node,
            link,
            ScKeynodes.resolve(nrel_name, sc_types.NODE_CONST_NOROLE)
        )
        self.logger.info(f"Ссылка на kaggle памяти сохранена")

    def __save_link_to_folder_to_sc_memory(self, download_path: str,  nrel_name: str, action_node) -> None:
        link = utils.create_link(download_path)
        utils.create_norole_relation(
            action_node,
            link,
            ScKeynodes.resolve(nrel_name, sc_types.NODE_CONST_NOROLE)
        )
        self.logger.info(f"Ссылка на папку в памяти сохранена")


    def __add_classes(self, dataset_path: str, dataset_file_name_with_extention: str, action_node):
        import pandas as pd

        file_path = os.path.join(dataset_path,dataset_file_name_with_extention)

        df = pd.read_csv(file_path)
        
        columns = df.columns.tolist()
        column_classes = [ScKeynodes.resolve(column, sc_types.NODE_CONST_CLASS) for column in columns]
        class_set = ScSet(*column_classes)
        utils.create_norole_relation(
            action_node,
            class_set.set_node,
            ScKeynodes.resolve("nrel_classes", sc_types.NODE_CONST_NOROLE)
        )
 

    def __run(self, action_node: ScAddr) -> ScResult:
        os.environ['KAGGLE_CONFIG_DIR'] = './'

        api = KaggleApi()
        api.authenticate()

        kaggle_url = self.get_link_content_kaggle(action_node)
        print(kaggle_url)

        dataset_full_name = self.__extract_dataset_path(kaggle_url)
        
        download_path = self.get_link_content(action_node)

        api.dataset_download_files(dataset_full_name, path=download_path, unzip=True)

        files = os.listdir(download_path) 
        files_with_paths = [os.path.join(download_path, f) for f in files]  
        latest_file = max(files_with_paths, key=os.path.getctime) 

        extention = ".csv"
        dataset_file_name = self.__extract_dataset_file(kaggle_url)
        dataset_file_name_with_extention = dataset_file_name + extention
    
        new_file_path = os.path.join(download_path, dataset_file_name_with_extention)
        os.rename(latest_file, new_file_path)
        
        self.logger.info(f"Датасет {dataset_file_name_with_extention} успешно скачан в {download_path}")

        self.logger.info("AGENT DOWNLOADED DATASET")

        construction = ScConstruction()
        self.__save_link_to_sc_memory(kaggle_url, "nrel_link_kaggle", action_node)
        self.__save_link_to_folder_to_sc_memory(download_path, "nrel_link_folder", action_node)
        self.__add_classes(download_path, dataset_file_name_with_extention, action_node)
        self.logger.info("AGENT CLASSIFIED DATASET")

        return ScResult.OK

    def __extract_dataset_path(self, kaggle_url: str) -> str:
        return "/".join(kaggle_url.rstrip("/").split("/")[-2:])

    def __extract_dataset_file(self, kaggle_url: str) -> str:
        return "/".join(kaggle_url.rstrip("/").split("/")[-1:])