from sc_client.models import ScAddr
import sc_kpm
from sc_kpm import ScAgentClassic
from sc_kpm.sc_result import ScResult
import numpy as np
from sc_client.models import *
from sc_client.constants import sc_types
from sc_client.client import *
from typing import List, Union
from .FNN import FNN
from .AgentTraining import AgentTraining


class AgentArtificialNeuralNetwork(ScAgentClassic):
    def __init__(self) -> None:
        print('Created Agent')
        super().__init__("action_solve_artificial_neural_network")
        self.__ann_name: str = ''
        self.__train_flag: bool = True

    def run(self) -> None:
        self._network: ScAddr = self.__find_network()
        self._layers: List[ScAddr] = self.__find_layers()
        self._input_neurons: List[ScAddr] = self.__get_input_neurons()
        self._output_neurons: List[ScAddr] = self.__get_output_neurons()
        self._hidden_layers: List[ScAddr] = self.__get_hidden_layers()
        self._hidden_neurons: List[List[ScAddr]] = self.__get_neurons_hidden_layer()
        self._weigths: List[np.ndarray[np.float64]] = []
        self._weigths.append(self.__get_weigths_for_neurons(self._input_neurons))
        for pack in self._hidden_neurons:
            self._weigths.append(self.__get_weigths_for_neurons(pack))
        self._input_values: np.ndarray[np.float64] = self.__get_input_values()
        self._activation_functions: List[str] = self.__get_activation_functions()
        if self.__train_flag:
            self.__train_model()

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        template = ScTemplate()
        template.triple_with_relation(
            action_element,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            "rrel_1"
        )
        result = template_search(template)
        self.__ann_name: str = sc_kpm.utils.get_system_idtf(result[0][2])
        template = ScTemplate()
        template.triple_with_relation(
            action_element,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            "rrel_2")
        result = template_search(template)
        self.__data_set_name: str = sc_kpm.utils.get_system_idtf(result[0][2])
        self.run()
        return 

    def __train_model(self) -> None:
        hidden_layers_size = []
        for hidden_number in self._hidden_neurons:
            hidden_layers_size.append(len(hidden_number))
        # Надо будет реализовать две выборки: тестовую и обучающую. Пока что на тестовой выборке получаются у значения и они же используются для обучения.
        fnn = FNN(self._weigths, self._input_values, self._activation_functions)
        fnn.run()
        np.array(fnn.output_values)
        trained_model = AgentTraining(
            self._input_values,
            fnn.output_values(),
            len(self._input_neurons),
            len(self._output_neurons),
            self._activation_functions,
            hidden_layers_size,
        )
        trained_model.run()
        model_weights = trained_model.get_model_weights()
        t_weights = []
        for weights in model_weights:
            t_weights.append(weights[0])
        print(t_weights)
        fnn = FNN(t_weights, self._input_values, self._activation_functions)
        fnn.run()
        print(fnn.output_values())

    def __find_network(self) -> ScAddr:
        main_node = sc_kpm.ScKeynodes[self.__ann_name]
        template = ScTemplate()
        template.triple(  # searching for ann structure
            main_node, sc_types.EDGE_ACCESS_VAR_POS_PERM, sc_types.NODE_VAR_STRUCT
        )
        search_results = template_search(template)
        return search_results[0][2]

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
        print(self._weigths, "weigths")
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

    def __get_weigths_for_neurons(
        self, neurons: List[ScAddr]
    ) -> List[List[np.float64]]:
        weigths = []
        for neuron in neurons:
            weigths_for_neuron = []
            template = ScTemplate()
            template.triple(
                neuron,
                sc_types.EDGE_D_COMMON_VAR,
                sc_types.NODE_VAR,
            )
            result_search_for_neurons_weigths = template_search(template)
            for edge in result_search_for_neurons_weigths:
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
                weigths_for_neuron.append(
                    np.float64(sc_kpm.utils.get_link_content_data(weight_value[0][2]))
                )
            weigths.append(weigths_for_neuron)
        return np.array(weigths)

    def __get_input_values(self) -> np.ndarray[np.float64]:
        data_set_node = sc_kpm.ScKeynodes["training_set"]
        input_values = []
        template = ScTemplate()
        template.triple(
            data_set_node, sc_types.EDGE_ACCESS_VAR_POS_PERM, self.__data_set_name
        )
        result = template_search(template)
        template = ScTemplate()
        template.triple(
            result[0][2], sc_types.EDGE_ACCESS_VAR_POS_PERM, sc_types.LINK_VAR
        )
        result = template_search(template)
        for set in result:
            input_values.append(sc_kpm.utils.get_link_content_data(set[2]).split(";"))
        return np.array(input_values, dtype=np.float64)

    def __get_activation_functions(self) -> List[str]:
        activation_functions: List[str] = []
        layers = []
        layers.append(self.__get_layer_by_name("processing_layer"))
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


def main():
    url = "ws://localhost:8090/ws_json"
    connect(url)
    ann = AgentArtificialNeuralNetwork()
    ann.logs()
    disconnect()


if __name__ == "__main__":
    main()
