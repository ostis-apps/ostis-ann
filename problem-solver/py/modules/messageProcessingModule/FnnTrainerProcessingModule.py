from sc_kpm import ScModule
from .FnnTrainerAgent import AgentTraining


class FnnTrainerProcessingModule(ScModule):
    def __init__(self):
        super().__init__(AgentTraining())
