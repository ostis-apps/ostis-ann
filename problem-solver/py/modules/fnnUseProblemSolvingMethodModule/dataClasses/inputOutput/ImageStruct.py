from dataclasses import dataclass
from InputOutputStruct import InputOutput

import numpy as np


@dataclass
class Image(InputOutput):
    image_array: np.array
    image_shape: tuple
    label: str