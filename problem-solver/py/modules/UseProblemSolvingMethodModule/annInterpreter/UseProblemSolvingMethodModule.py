from sc_kpm import ScModule

from .UseProblemSolvingMethodAgent import UseProblemSolvingMethodAgent


class UseProblemSolvingMethodModule(ScModule):
    def __init__(self) -> None:
        super().__init__(UseProblemSolvingMethodAgent())