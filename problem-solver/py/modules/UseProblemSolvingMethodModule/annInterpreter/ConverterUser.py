from typing import List

from modules.UseProblemSolvingMethodModule.converters import Converter


class ConverterUser:
    def __init__(self, problems:List[str]):
        self.problems = problems.sort()

    def __findConverter(self)->Converter:
        for problem in self.problems:
            match problem:
                case "concept_image_classification":
                    pass

