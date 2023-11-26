import numpy as np
from numpy import exp, sin, cos, tan, arcsin, arccos, arctan
import tensorflow as tf
from typing import List


class AgentTraining:
    def __init__(
        self,
        training_data: np.ndarray[np.float64],
        target_data: np.ndarray[np.float64],
        input_layer_size: int,
        output_layer_size: int,
        activation_functions: List[str],
        hidden_layers_size: List[int] = [],
        learning_rate: np.float64 = 0.001,
        epochs: int = 100,
        batch_size: int = 1,
    ) -> None:
        self.__training_data: np.ndarray[np.float64] = training_data
        self.__target_data: np.ndarray[np.float64] = target_data
        self.__input_layer_size: int = input_layer_size
        self.__output_layer_size: int = output_layer_size
        self.__hidden_layers_size: List[int] = hidden_layers_size
        self.__activation_functions: List[str] = activation_functions[::-1]
        self.__learning_rate: np.float64 = learning_rate
        self.__epochs : int = epochs
        self.__batch_size : int = batch_size
        self.__optimizer = tf.keras.optimizers.Adam(learning_rate=self.__learning_rate)

    def run(self):
        self._model = self.__create_model()
        self.__train_model()

    def __create_model(self):
        model = tf.keras.models.Sequential()
        for hidden_layer_size in self.__hidden_layers_size:
            foo = self.__activation_functions.pop()
            model.add(tf.keras.layers.Dense(hidden_layer_size,use_bias=False, activation=(lambda x:eval(foo,{'x':x,'exp':tf.exp,'sin': tf.sin, 'cos': tf.cos, 'tan': tf.tan, 'arcsin': tf.asin, 'arccos': tf.acos, 'arctan': tf.atan}))))
        foo = self.__activation_functions.pop()
        model.add(tf.keras.layers.Dense(self.__output_layer_size,use_bias=False, activation=(lambda x:eval(foo,{'x':x,'exp':tf.exp,'sin': tf.sin, 'cos': tf.cos, 'tan': tf.tan, 'arcsin': tf.asin, 'arccos': tf.acos, 'arctan': tf.atan}))))
        model.compile(optimizer=self.__optimizer, loss='huber_loss')
        return model

    def __train_model(self):
        self._model.fit(self.__training_data, self.__target_data, epochs=self.__epochs, batch_size=self.__batch_size, validation_split=0.2)

    def get_model_weights(self):
        model_weights = []
        for i,layer in enumerate(self._model.layers):
            layer_weights = layer.get_weights()
            model_weights.append(layer_weights)
        return model_weights