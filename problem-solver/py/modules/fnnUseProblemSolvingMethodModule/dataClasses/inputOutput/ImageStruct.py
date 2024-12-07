from dataclasses import dataclass
from InputOutputStruct import InputOutput

import numpy as np


@dataclass
class Image(InputOutput):
    # data_array: np.array
    image_shape: tuple = None
    label: str = None