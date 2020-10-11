from abc import ABC, abstractmethod


class AnnAppBase(ABC):
    @abstractmethod
    def process(self, path):
        pass
