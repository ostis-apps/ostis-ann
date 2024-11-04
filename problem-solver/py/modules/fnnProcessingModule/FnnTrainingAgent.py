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
        self.logger.info("FnnTrainingAgent started")
        result = self.__run(action_element)
        self.logger.info("FnnTrainingAgent finished")
        return result

    def __run(self, action_element: ScAddr) -> ScResult:
        reader = FnnReader(action_element)

        # Set up training parameters
        self.__training_params: TrainParams = reader.get_training_params()
        self.__input_layer_size: np.int64 = reader.input_layer_size
        self.__output_layer_size: np.int64 = reader.output_layer_size
        self.__hidden_layers_size: List[np.int64] = reader.hidden_layer_size
        self.__activation_functions: List[str] = reader.activation_functions

        # Build model
        self.__model = self.__create_model()

        # Train model
        self.__train_model(self.__model)

        # Write updated weights to memory
        reader.update_weight(self.__get_model_weights())

        # todo: error handling?
        return ScResult.OK

    @staticmethod
    def __evaluate_function(function_string: str):
        return lambda x: eval(
            function_string,
            {
                "x": x,
                "exp": tf.exp,
                "sin": tf.sin,
                "cos": tf.cos,
                "tan": tf.tan,
                "arcsin": tf.asin,
                "arccos": tf.acos,
                "arctan": tf.atan
            },
        )

    def __get_dense_layer(self, size, activation_function: str):
        return tf.keras.layers.Dense(
            size,
            use_bias=False,
            activation=(self.__evaluate_function(activation_function)),
            dtype=np.float64,
        )

    def __create_model(self):
        model = tf.keras.models.Sequential()

        for hidden_layer_size in self.__hidden_layers_size:
            foo = self.__activation_functions.pop()
            model.add(self.__get_dense_layer(hidden_layer_size, foo))

        foo = self.__activation_functions.pop()
        model.add(self.__get_dense_layer(self.__output_layer_size, foo))

        optimizer = tf.keras.optimizers.Adam(learning_rate=self.__training_params.learning_rate)
        model.compile(optimizer=optimizer, loss=tf.keras.losses.Huber())
        return model

    def __train_model(self, model):
        model.fit(
            self.__training_params.input_values,
            self.__training_params.output_values,
            epochs=self.__training_params.epochs,
            validation_split=0.2,
        )

    def __get_model_weights(self):
        return [layer.get_weights() for layer in self.__model.layers]
