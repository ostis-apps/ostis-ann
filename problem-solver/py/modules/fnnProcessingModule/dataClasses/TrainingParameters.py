from dataclasses import dataclass

from .DatasetStruct import DatasetStruct
from .FnnStruct import FnnStruct


@dataclass
class TrainingParameters:
    fnn_struct: FnnStruct
    dataset_struct: DatasetStruct
    epochs: int
    learning_rate: float
    batch_size: int
