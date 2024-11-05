from sc_kpm import ScModule

from .DatasetPreprocessingAgent import DatasetPreprocessingAgent
from .FnnTrainingAgent import FnnTrainingAgent


class FnnTrainingModule(ScModule):
    def __init__(self):
        super().__init__(FnnTrainingAgent(), DatasetPreprocessingAgent())
