from dataclasses import dataclass

import pandas as pd
from sc_client.models import ScAddr

from modules.fnnProcessingModule.dataClasses.FnnLayerConfiguration import FnnLayerConfiguration


@dataclass
class FnnStruct:
    network_address: ScAddr
    layers_configuration: tuple[FnnLayerConfiguration, ...]
