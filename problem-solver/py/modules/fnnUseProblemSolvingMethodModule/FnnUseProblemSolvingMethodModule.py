from sc_kpm import ScModule

from .FnnUseProblemSolvingMethodAgent import FnnUseProblemSolvingMethodAgent


class FnnUseProblemSolvingMethodModule(ScModule):
    def __init__(self) -> None:
        super().__init__(FnnUseProblemSolvingMethodAgent())