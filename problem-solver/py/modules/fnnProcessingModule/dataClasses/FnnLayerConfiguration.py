from dataclasses import dataclass

from sc_client.models import ScAddr


@dataclass
class FnnLayerConfiguration:
    address: ScAddr
    output_size: int | None
    activation_function: str | None
    input_size: int | None = None
