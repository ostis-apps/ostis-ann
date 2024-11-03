import numpy as np
from numpy import exp, sin, cos, tan, arcsin, arccos, arctan
from typing import List
from sc_kpm import ScAgentClassic
from sc_client.models import ScAddr
from sc_kpm.sc_result import ScResult
from .FnnReader import FnnReader


class FnnInterpreterAgent(ScAgentClassic):
    def __init__(self) -> None:
        super().__init__("action_interpreter_fnn")
        self.__output_values: List[np.ndarray[np.float64]] = []

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        self.__reader = FnnReader(action_element)
        self.logger.info("AgentIntepreterFnn started")
        result = self.run()
        self.logger.info("AgentIntepreterFnn finished")
        return result

    def run(self):
        self.__weights: np.ndarray[np.float64] = self.__reader.weigths
        self.__input_values: np.ndarray[np.float64] = self.__reader.input_values
        self.__activation_functions: List[str] = self.__reader.activation_functions
        print('weights:\n',self.__weights)
        print('input values:\n',self.__input_values)
        for input_value in self.__input_values:
            self.__predict(input_value)
        print('output values:\n',self.__output_values)
        self.__reader.commit_result(self.__output_values)

    def __predict(self, input_value: np.ndarray[np.float64]):
        output_value = input_value.copy()
        for i, weight in enumerate(self.__weights):
            output_value = self.__function(output_value.dot(weight), i)
        self.__output_values.append(output_value)

    def __function(self, x, i):
        return eval(self.__activation_functions[i])
