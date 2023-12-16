from sc_kpm import ScModule
from .AgentIntepreterFnn import FnnSolver


class FnnAgentProcessingModule(ScModule):
    def __init__(self):
        super().__init__(FnnSolver())
