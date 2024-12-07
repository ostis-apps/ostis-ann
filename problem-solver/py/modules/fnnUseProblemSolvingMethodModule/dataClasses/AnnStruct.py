from dataclasses import dataclass
from typing import List

from sc_client.models import ScAddr


@dataclass
class AnnStruct:
    network_address: ScAddr
    num_of_inputs: int
    num_of_outputs: int
    output_labels: List[str] = None