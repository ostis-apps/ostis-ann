import logging

from os.path import dirname, abspath

import pandas as pd
import sc_kpm
from sc_client.client import *
from sc_client.constants import sc_types
from sc_client.models import *

from modules.fnnProcessingModule.dataClasses.DatasetStruct import DatasetStruct
from modules.fnnProcessingModule.dataClasses.FnnLayerConfiguration import FnnLayerConfiguration
from modules.fnnProcessingModule.dataClasses.FnnStruct import FnnStruct
from modules.fnnProcessingModule.dataClasses.TrainingParameters import TrainingParameters

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class TrainingParametersReader:
    def __init__(self) -> None:
        pass

    # todo: strict type validation for parameters, otherwise it may end up crashing network trainer later
    def get_training_params(self, action_addr: ScAddr) -> TrainingParameters:
        fnn_address = self.__get_fnn_address(action_addr)
        params_address = self.__get_params_address(action_addr)

        dataset_address = self.__get_dataset_addr(params_address)

        dataset = self.__get_dataset(dataset_address)
        labels_column_name = self.__get_labels_column_name(dataset_address)
        dataset_struct = DatasetStruct(dataset, labels_column_name)

        epoch = self.__get_epochs(params_address)
        learning_rate = self.__get_learning_rate(params_address)
        batch_size = self.__get_batch_size(params_address)
        
        layers_configuration = self.__get_layers_configuration(fnn_address)
        layers_configuration = self.__adjust_layers_config(layers_configuration, dataset_struct)
        fnn_struct = FnnStruct(fnn_address, layers_configuration)

        return TrainingParameters(fnn_struct, dataset_struct, epoch, learning_rate, batch_size)

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

    def __get_fnn_address(self, action_addr) -> ScAddr:
        return self.__get_rrel_target(action_addr, "rrel_1")

    def __get_params_address(self, action_addr: ScAddr) -> ScAddr:
        return self.__get_rrel_target(action_addr, "rrel_2")

    def __get_dataset_addr(self, params_address: ScAddr) -> ScAddr:
        return self.__get_rrel_target(params_address, "rrel_dataset")

    def __get_dataset(self, dataset_address: ScAddr) -> pd.DataFrame:
        filepath_link_addr = self.__get_nrel_target_link(dataset_address, "nrel_csv_filepath")
        dataset_filepath = get_link_content(filepath_link_addr)[0].data

        # todo: review and maybe refactor specification of filepath
        script_directory = dirname(dirname(abspath(__file__)))
        ann_path = dirname(dirname(dirname(dirname(script_directory))))
        kb_path = f'{ann_path}/kb'

        df = pd.read_csv(f'{kb_path}/{dataset_filepath}')
        return df

    def __get_labels_column_name(self, dataset_address) -> str:
        labels_column_name_link_addr = self.__get_nrel_target_link(dataset_address, "nrel_labels_column_name")
        labels_column_name = get_link_content(labels_column_name_link_addr)[0].data

        return labels_column_name

    def __get_learning_rate(self, params_address) -> float:
        # todo: Numeric links are somehow stored in format of 'float:0.001'
        #  so it's easier to store them as strings like '0.001' for now
        #  Bug in gwf translation or inability to store floats in general?
        addr = self.__get_rrel_target(params_address, "rrel_learning_rate")

        return float(get_link_content(addr)[0].data)

    def __get_epochs(self, params_address) -> int:
        # todo: Numeric links are somehow stored in format of 'float:0.001'
        #  so it's easier to store them as strings like '0.001' for now
        #  Bug in gwf translation or inability to store floats in general?
        addr = self.__get_rrel_target(params_address, "rrel_number_epochs")

        return int(get_link_content(addr)[0].data)

    def __get_batch_size(self, params_address) -> int:
        # todo: Numeric links are somehow stored in format of 'float:0.001'
        #  so it's easier to store them as strings like '0.001' for now
        #  Bug in gwf translation or inability to store floats in general?
        addr = self.__get_rrel_target(params_address, "rrel_batch_size")

        return int(get_link_content(addr)[0].data)

    def __get_activation_func(self, layer_address) -> str | None:
        try:
            link_addr = self.__get_nrel_target_link(layer_address, "nrel_activation_function")
            return get_link_content(link_addr)[0].data
        except IndexError:  # If no activation function is specified for layer
            return None

    def __get_layer_size(self, layer_address) -> int | None:
        # todo: Numeric links are somehow stored in format of 'float:0.001'
        #  so it's easier to store them as strings like '0.001' for now
        #  Bug in gwf translation or inability to store floats in general?
        try:
            link_addr = self.__get_nrel_target_link(layer_address, "nrel_size")
            return int(get_link_content(link_addr)[0].data)
        except:  # If no size is specified for layer
            return None

    def __get_layers_configuration(self, fnn_address) -> tuple[FnnLayerConfiguration, ...]:
        layers_config: list[FnnLayerConfiguration] = []

        # Get first layer
        template = ScTemplate()
        template.triple_with_relation(
            fnn_address,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.NODE_VAR_STRUCT,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_kpm.ScKeynodes["nrel_first_layer"]
        )
        input_layer_addr = template_search(template)[0][2]

        # Get config for each layer
        current_layer_addr = input_layer_addr
        while True:
            current_layer_size = self.__get_layer_size(current_layer_addr)
            current_layer_function = self.__get_activation_func(current_layer_addr)
            current_layer_config = FnnLayerConfiguration(address=current_layer_addr,
                                                         output_size=current_layer_size,
                                                         activation_function=current_layer_function)
            layers_config.append(current_layer_config)

            template = ScTemplate()
            template.triple_with_relation(
                current_layer_addr,
                sc_types.EDGE_D_COMMON_VAR,
                sc_types.NODE_VAR_STRUCT,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                sc_kpm.ScKeynodes["nrel_goto"]
            )

            results = template_search(template)
            if len(results) == 0:
                break

            current_layer_addr = results[0][2]

        return tuple(layers_config)

    def __adjust_layers_config(self,
                               layers_configuration: tuple[FnnLayerConfiguration, ...],
                               dataset_struct: DatasetStruct
                               ) -> tuple[FnnLayerConfiguration, ...]:
        """

        :param layers_configuration:
        :param dataset_struct:
        :return: Layers configuration with adjusted size for 1st and last layers based on dataset
        """
        # Assuming the dataset is flattened and there is always single column with labels
        input_size = len(dataset_struct.dataset.axes[1]) - 1
        layers_configuration[0].input_size = input_size

        # Output layer size equals to number of classes in dataset
        labels_column = dataset_struct.labels_column
        output_size = dataset_struct.dataset[labels_column].nunique()
        layers_configuration[-1].output_size = output_size

        return layers_configuration
