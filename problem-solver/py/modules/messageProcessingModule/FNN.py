import numpy as np
from numpy import exp, sin, cos, tan, arcsin, arccos, arctan
from typing import List


class FNN:
    def __init__(
        self,
        weights: np.ndarray[np.float64],
        input_values: np.ndarray[np.float64],
        activation_function: List[str],
    ) -> None:
        self.__weights: np.ndarray[np.float64] = weights
        self.__input_values: np.ndarray[np.float64] = input_values
        self.__activation_functions: List[str] = activation_function
        self.__output_values: List[np.ndarray[np.float64]] = []

    def run(self):
        for input_value in self.__input_values:
            self.predict(input_value)

    def predict(self, input_value: np.ndarray[np.float64]):
        output_value = input_value.copy()
        for i, weight in enumerate(self.__weights):
            output_value = self.function(output_value.dot(weight), i)
        self.__output_values.append(output_value)

    def function(self, x, i):
        return eval(self.__activation_functions[i])

    def output_values(self):
        return np.array(self.__output_values)
