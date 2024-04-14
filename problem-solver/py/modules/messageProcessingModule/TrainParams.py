import numpy as np

class TrainParams:
    def __init__(self,
                 input_values: np.ndarray[np.float64],
                 output_values: np.ndarray[np.float64],
                 epochs: np.int64,
                 learning_rate: np.float64,
                 ) -> None:
        self.input_values: np.ndarray[np.float64] = input_values
        self.output_values: np.ndarray[np.float64] = output_values
        self.epochs: np.ndarray[np.float64] = epochs
        self.learning_rate = learning_rate

    def print_params(self) -> str:
        print(np.hstack((self.input_values,self.output_values)))