from sc_kpm import ScModule
from .FnnInterpreterAgent import FnnInterpreterAgent


class FnnInterpreterModule(ScModule):
    def __init__(self):
        super().__init__(FnnInterpreterAgent())
