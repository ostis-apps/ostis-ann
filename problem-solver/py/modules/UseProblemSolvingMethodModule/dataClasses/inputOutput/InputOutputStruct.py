from dataclasses import dataclass

import numpy as np
from sc_client.models import ScAddr


@dataclass
class InputOutput:
    object_addr: ScAddr
    data_array: np.array
