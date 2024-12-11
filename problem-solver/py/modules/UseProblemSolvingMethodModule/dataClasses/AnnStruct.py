from dataclasses import dataclass
from typing import List

import keras
from sc_client.models import ScAddr


@dataclass
class AnnStruct:
    network_address: ScAddr
    ann_model: keras.Model
    num_of_inputs: int
    num_of_outputs: int
    output_labels: List[str] = None