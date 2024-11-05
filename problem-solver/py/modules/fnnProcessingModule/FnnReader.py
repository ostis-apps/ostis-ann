import logging
import sc_kpm
import numpy as np
from sc_client.models import *
from sc_client.constants import sc_types
from sc_client.client import *
from typing import List, Union
from .TrainParams import TrainParams

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class FnnReader:
    def __init__(self, action_node: ScAddr) -> None:
        self.__action_node = action_node
        self._network: ScAddr = self.__find_network()
        self._layers: List[ScAddr] = self.__find_layers()
        self._input_neurons: List[ScAddr] = self.__get_input_neurons()
        self._output_neurons: List[ScAddr] = self.__get_output_neurons()
        self._hidden_layers: List[ScAddr] = self.__get_hidden_layers()
        self._hidden_neurons: List[ScAddr] = self.__get_neurons_hidden_layer()[::-1]
        self._weights: np.ndarray[np.float64] = []
        self._weights_addr: List[ScAddr] = []
        self._weights.append(self.__get_weights_for_neurons(self._input_neurons))
        self._activation_functions: List[str] = self.__get_activation_functions()
        for pack in self._hidden_neurons:
            self._weights.append(self.__get_weights_for_neurons(pack))
        self._input_values_addr: List[ScAddr] = []
        self._input_values: np.ndarray[np.float64] = self.__get_input_values()

    @property
    def weights(self) -> np.ndarray[np.float64]:
        return self._weights
    
    @property
    def activation_functions(self) -> List[str]:
        return self._activation_functions
    
    @property
    def input_values(self) -> np.ndarray[np.float64]:
        return self._input_values 

    @property
    def hidden_layer_size(self) -> List[np.int64]:
        hidden_layers_size = []
        for hidden_number in self._hidden_neurons:
            hidden_layers_size.append(len(hidden_number)) 
        return hidden_layers_size
    
    @property
    def input_layer_size(self) -> np.int64:
        return len(self._input_neurons)
    
    @property
    def output_layer_size(self) -> np.int64:
        return len(self._output_neurons)

    def __find_network(self) -> ScAddr:
        template = ScTemplate()
        template.triple_with_relation(
            self.__action_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR_STRUCT,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_kpm.ScKeynodes["rrel_1"]
        )
        result_search = template_search(template)
        return result_search[0][2]

    def __find_layers(self) -> List[ScAddr]:
        template = ScTemplate()
        template.triple_with_relation(  # searching for layers
            self._network,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.NODE_VAR_STRUCT,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR_NOROLE,
        )
        search_results = template_search(template)
        return [result[2] for result in search_results]

    def __identificators(self, addresses: Union[ScAddr, List[ScAddr]]) -> None:
        if isinstance(addresses, ScAddr):
            print(addresses, "=", sc_kpm.utils.get_system_idtf(addresses))
        elif isinstance(addresses, List):
            for address in addresses:
                if isinstance(address, ScAddr):
                    print(address, "=", sc_kpm.utils.get_system_idtf(address))

    def logs(self) -> None:
        print(self._layers, "layers ids")
        self.__identificators(self._layers)
        print(self._input_neurons, "input neurons ids")
        print(self._output_neurons, "output neurons ids")
        print(self._hidden_layers, "hidden layers ids")
        print(self._hidden_neurons, "hidden neurons ids")
        print(self._weights, "weights")
        print(self._input_values, "input values")
        print(self._activation_functions, "activation functions")

    def __get_layer_by_name(self, name: str) -> ScAddr:
        for target_layer in self._layers:
            if sc_kpm.utils.get_system_idtf(target_layer) == name:
                return target_layer
        return None

    def __get_input_neurons(self) -> Union[List[ScAddr], ScAddr]:
        neuron_list = []
        target_layer = self.__get_layer_by_name("distribution_layer")
        template = ScTemplate()
        template.triple_with_relation(  # searching for first neuron
            target_layer,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            "rrel_1",
        )
        result = template_search(template)
        target_edge = result[0][1]
        neuron_list.append(result[0][2])
        while True:  # searching for other neurons
            template = ScTemplate()
            template.triple_with_relation(
                target_edge,
                sc_types.EDGE_D_COMMON_VAR,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                "nrel_goto",
            )
            result = template_search(template)
            if len(result) == 0:
                break
            target_edge = result[0][2]
            template = ScTemplate()
            template.triple(target_layer, target_edge, sc_types.NODE_VAR)
            result = template_search(template)
            neuron_list.append(result[0][2])
        return neuron_list

    def __get_output_neurons(self) -> Union[List[ScAddr], ScAddr]:
        target_layer = self.__get_layer_by_name("processing_layer")
        template = ScTemplate()
        template.triple(  # searching for output neurons
            target_layer, sc_types.EDGE_ACCESS_VAR_POS_PERM, sc_types.NODE_VAR
        )
        neurons = template_search(template)
        return [neuron[2] for neuron in neurons]

    def __get_hidden_layers(self) -> List[ScAddr]:
        for layer in self._layers:
            if sc_kpm.utils.get_system_idtf(layer) == "hidden_layer":
                break
        if layer:
            template = ScTemplate()
            template.triple(
                layer,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                sc_types.NODE_VAR,
            )
            hidden_layers = [x[2] for x in template_search(template)]
            return hidden_layers
        return []

    def __get_neurons_hidden_layer(self) -> List[ScAddr]:
        neurons_of_hidden_layers = []
        for layer in self._hidden_layers:
            template = ScTemplate()
            template.triple(  # searching for hidden neurons
                layer, sc_types.EDGE_ACCESS_VAR_POS_PERM, sc_types.NODE_VAR
            )
            neurons = template_search(template)
            neurons_of_hidden_layers.append([neuron[2] for neuron in neurons])
        return neurons_of_hidden_layers

    def __get_weights_for_neurons(self, neurons: List[ScAddr]) -> List[np.float64]:
        weights = []
        weights_layer_addr = []
        for neuron in neurons:
            weights_for_neuron = []
            weights_for_neuron_addr = []
            template = ScTemplate()
            template.triple(
                neuron,
                sc_types.EDGE_D_COMMON_VAR,
                sc_types.NODE_VAR,
            )
            result_search_for_neurons_weights = template_search(template)
            for edge in result_search_for_neurons_weights:
                template = ScTemplate()
                template.triple_with_relation(
                    sc_types.NODE_VAR_CLASS,
                    sc_types.EDGE_ACCESS_VAR_POS_PERM,
                    edge[1],
                    sc_types.EDGE_ACCESS_VAR_POS_PERM,
                    sc_kpm.ScKeynodes["rrel_weigth"],
                )
                weight = template_search(template)
                template = ScTemplate()
                template.triple(
                    weight[0][0],
                    sc_types.EDGE_D_COMMON_VAR,
                    sc_types.LINK_VAR,
                )
                weight_value = template_search(template)
                weights_for_neuron.append(
                    np.float64(sc_kpm.utils.get_link_content_data(weight_value[0][2]))
                )
                weights_for_neuron_addr.append(weight_value[0][2])
            weights.append(weights_for_neuron)
            weights_layer_addr.append(weights_for_neuron_addr)
        self._weights_addr.append(weights_layer_addr)
        return np.array(weights)

    def __get_input_values(self) -> np.ndarray[np.float64]:
        input_values = []
        template = ScTemplate()
        template.triple_with_relation(
            self.__action_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_kpm.ScKeynodes["rrel_2"]
        )
        result_search = template_search(template)
        template = ScTemplate()
        template.triple(
            result_search[0][2], sc_types.EDGE_ACCESS_VAR_POS_PERM, sc_types.LINK_VAR
        )
        result = template_search(template)
        for set in result:
            input_values.append(sc_kpm.utils.get_link_content_data(set[2]).split(";"))
            self._input_values_addr.append(set[2])
        return np.array(input_values, dtype=np.float64)

    def get_training_params(self) -> TrainParams:
        template = ScTemplate()
        template.triple_with_relation(
            self.__action_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_kpm.ScKeynodes["rrel_2"]
        )
        train_params = template_search(template)[0][2]
        template = ScTemplate()
        template.triple_with_relation(
            train_params,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_kpm.ScKeynodes["rrel_data"]
        )
        training_data_node = template_search(template)[0][2]
        template = ScTemplate()
        template.triple_with_relation(
            train_params,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.LINK_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_kpm.ScKeynodes["rrel_number_epochs"]
        )
        number_epochs : np.int64 = np.int64(sc_kpm.utils.get_link_content_data(template_search(template)[0][2]))
        template = ScTemplate()
        template.triple_with_relation(
            train_params,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.LINK_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_kpm.ScKeynodes["rrel_learning_rate"]
        )
        learning_rate : np.float64 = np.float64(sc_kpm.utils.get_link_content_data(template_search(template)[0][2]))
        template = ScTemplate()
        template.triple(
            training_data_node, sc_types.EDGE_ACCESS_VAR_POS_PERM, sc_types.NODE_STRUCT
        )
        data_struct_nodes = template_search(template)
        input_values = []
        output_values = []
        for data_struct_node in data_struct_nodes:
            template = ScTemplate()
            template.triple_with_relation(
                data_struct_node[2],
                sc_types.EDGE_ACCESS_VAR_POS_PERM, 
                sc_types.LINK_VAR,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                sc_kpm.ScKeynodes["rrel_input_values"]
            )
            for input_link in template_search(template):
                input_values.append(sc_kpm.utils.get_link_content_data(input_link[2]).split(";"))
            template = ScTemplate()
            template.triple_with_relation(
                data_struct_node[2],
                sc_types.EDGE_ACCESS_VAR_POS_PERM, 
                sc_types.LINK_VAR,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                sc_kpm.ScKeynodes["rrel_output_values"]
            )
            for output_link in template_search(template):
                output_values.append(sc_kpm.utils.get_link_content_data(output_link[2]).split(";"))
        input_values: np.ndarray[np.float64] = np.array(input_values, dtype=np.float64)
        output_values: np.ndarray[np.float64] = np.array(output_values, dtype=np.float64)
        return TrainParams(input_values, output_values, number_epochs, learning_rate)

    def __get_activation_functions(self) -> List[str]:
        activation_functions: List[str] = []
        layers = [self.__get_layer_by_name("processing_layer")]
        layers += self._hidden_layers
        for layer in layers:
            template = ScTemplate()
            template.triple_with_relation(
                layer,
                sc_types.EDGE_D_COMMON_VAR,
                sc_types.NODE_VAR,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                sc_kpm.ScKeynodes["nrel_activation_function"],
            )
            activation_function_node = template_search(template)
            template = ScTemplate()
            template.triple(
                activation_function_node[0][2],
                sc_types.EDGE_D_COMMON_VAR,
                sc_types.LINK_VAR,
            )
            activation_function = sc_kpm.utils.get_link_content_data(
                template_search(template)[0][2]
            )
            activation_functions.append(activation_function)
        return activation_functions

    def update_weight(self, weights: np.ndarray[np.float64]) -> None:
        def make_linear(l):
            if not isinstance(l, list):
                return [l]
            answer = []
            for elm in l:
                answer += make_linear(elm)
            return answer

        weights_addr = make_linear(self._weights_addr)
        weights_values = []
        for i in weights:
            for j in i:
                for k in j:
                    for z in k:
                        weights_values.append(z)
        for addr, weight in zip(weights_addr,weights_values):
            link_content = ScLinkContent(str(weight), ScLinkContentType.STRING, addr)
            set_link_contents(link_content)

    def commit_result(self, output_values: List[np.ndarray[np.float64]], sc_client) -> None:
        # ScConstruction.create_node(sc_type: ScType, alias: str = None)
        # ScConstruction.create_edge(sc_type: ScType, src: str | ScAddr, trg: str | ScAddr, alias: str = None)
        # ScConstruction.create_link(sc_type: ScType, content: ScLinkContent, alias: str = None)
        construction = ScConstruction()
        construction.create_node(sc_types.NODE_CONST_NOROLE, alias="nrel_answer") # creating nrel_answer node
        nrel_answer_node = sc_client.client.create_elements(construction)[0]

        construction = ScConstruction()
        construction.create_node(sc_types.NODE_CONST_STRUCT) # creating struct node
        struct_node = sc_client.client.create_elements(construction)[0]

        construction = ScConstruction()
        construction.create_edge(sc_types.EDGE_D_COMMON_CONST,self.__action_node,struct_node) # create edge bt act&struct
        edge_common_d = sc_client.client.create_elements(construction)[0]

        construction = ScConstruction()
        construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM,nrel_answer_node,edge_common_d) # connect nrel_answer&edge
        sc_client.client.create_elements(construction)

        construction = ScConstruction()
        construction.create_node(sc_types.NODE_CONST_TUPLE, alias="") # main tuple node
        main_tuple_node = sc_client.client.create_elements(construction)[0]

        construction = ScConstruction()
        construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM,struct_node,main_tuple_node) # connect struct&tuple
        sc_client.client.create_elements(construction)

        for i, data_node in enumerate(self._input_values_addr):
            construction = ScConstruction()
            construction.create_node(sc_types.NODE_CONST_TUPLE, alias="")
            tuple_node = sc_client.client.create_elements(construction)[0]

            construction = ScConstruction()
            construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM,main_tuple_node,tuple_node)
            construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM,tuple_node,data_node)
            sc_client.client.create_elements(construction)

            str_output_values = []
            for values in output_values[i]:
                str_output_values.append(str(values))

            construction = ScConstruction()
            construction.create_link(sc_types.LINK_CONST, content = ScLinkContent(";".join(str_output_values), ScLinkContentType.STRING))
            link_node = sc_client.client.create_elements(construction)[0]

            construction = ScConstruction()
            construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM,tuple_node,link_node)
            sc_client.client.create_elements(construction)[0]
