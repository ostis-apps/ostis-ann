import numpy as np
import tensorflow as tf
from sc_client.models import ScAddr
from sc_kpm import ScAgentClassic
from sc_kpm.sc_result import ScResult

from .FnnModelBuilder import build_model
from .FnnTrainer import train_model
from .TrainingParametersReader import TrainingParametersReader


class FnnTrainingAgent(ScAgentClassic):
    def __init__(self) -> None:
        super().__init__("action_train_fnn")

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        self.logger.info("FnnTrainingAgent started")
        result = self.__run(action_element)
        self.logger.info("FnnTrainingAgent finished")
        return result

    def __run(self, action_element: ScAddr) -> ScResult:
        # Get training parameters from input struct
        reader = TrainingParametersReader()
        training_parameters = reader.get_training_params(action_element)

        print(training_parameters.batch_size)
        print(training_parameters.dataset_struct.labels_column)
        print(training_parameters.fnn_struct.layers_configuration)
        # Build model
        model: tf.keras.Model = build_model(training_parameters)

        # Train model
        train_model(model, training_parameters)

        # Write trained network to memory
        self.__save_model(model)

        # todo: error handling
        return ScResult.OK

    # todo
    def __save_model(self, model):
        pass
