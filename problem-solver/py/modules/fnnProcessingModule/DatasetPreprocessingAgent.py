import numpy as np
import tensorflow as tf
from typing import List
from sc_kpm import ScAgentClassic
from sc_client.models import ScAddr
from sc_kpm.sc_result import ScResult
from .FnnReader import FnnReader
from .TrainParams import TrainParams


class DatasetPreprocessingAgent(ScAgentClassic):
    def __init__(self) -> None:
        super().__init__("action_preprocess_dataset")

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        self.logger.info("DatasetPreprocessingAgent started")

        self.logger.info("DatasetPreprocessingAgent finished")
        return ScResult.OK
