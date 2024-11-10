from dataclasses import dataclass

import pandas as pd


@dataclass
class DatasetStruct:
    dataset: pd.DataFrame
    labels_column: str
