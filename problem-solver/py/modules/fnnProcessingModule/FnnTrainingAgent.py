import numpy as np
import tensorflow as tf
from typing import List
from sc_kpm import ScAgentClassic
from sc_client.models import ScAddr
from sc_kpm.sc_result import ScResult
from .FnnReader import FnnReader
from .TrainParams import TrainParams


class FnnTrainingAgent(ScAgentClassic):
    def __init__(self) -> None:
        super().__init__("action_train_fnn")

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        self.__reader = FnnReader(action_element)
        self.logger.info("AgentTrainerFnn started")
        result = self.__run()
        self.logger.info("AgentTrainerFnn finished")
        return result

    def __run(self):
        self.__training_params: TrainParams = self.__reader.get_training_train_params()
        self.__training_data: np.ndarray[np.float64] = self.__training_params.input_values
        self.__target_data: np.ndarray[np.float64] = self.__training_params.output_values
        self.__input_layer_size: np.int64 = self.__reader.input_layer_size
        self.__output_layer_size: np.int64 = self.__reader.output_layer_size
        self.__hidden_layers_size: List[np.int64] = self.__reader.hidden_layer_size
        self.__activation_functions: List[str] = self.__reader.activation_functions
        self.__learning_rate: np.float64 = self.__training_params.learning_rate
        self.__epochs: np.int64 = self.__training_params.epochs
        self.__optimizer = tf.keras.optimizers.Adam(learning_rate=self.__learning_rate)
        self.model = tf.keras.models.Sequential()
        self._model = self.__create_model()
        self.__train_model()
        self.__reader.update_weight(self.__get_model_weights())

    @staticmethod
    def __get_activation_function(foo):
        return lambda x: eval(
            foo,
            {
                "x": x,
                "exp": tf.exp,
                "sin": tf.sin,
                "cos": tf.cos,
                "tan": tf.tan,
                "arcsin": tf.asin,
                "arccos": tf.acos,
                "arctan": tf.atan,
            },
        )

    def __get_dense_layer(self, size, fun):
        return tf.keras.layers.Dense(
            size,
            use_bias=False,
            activation=(self.__get_activation_function(fun)),
            dtype=np.float64,
        )

    def __create_model(self):
        for hidden_layer_size in self.__hidden_layers_size:
            foo = self.__activation_functions.pop()
            self.model.add(self.__get_dense_layer(hidden_layer_size, foo))

        foo = self.__activation_functions.pop()
        self.model.add(self.__get_dense_layer(self.__output_layer_size, foo))

        self.model.compile(optimizer=self.__optimizer, loss=tf.keras.losses.Huber())
        return self.model

    def __train_model(self):
        self._model.fit(
            self.__training_data,
            self.__target_data,
            epochs=self.__epochs,
            validation_split=0.2,
        )

    def __get_model_weights(self):
        model_weights = []
        for i, layer in enumerate(self._model.layers):
            layer_weights = layer.get_weights()
            model_weights.append(layer_weights)
        return model_weights
