import numpy as np

from neural_networks.ann_app_base import AnnAppBase
from neural_networks.sequence_prediction.predictor import predictor_instance


class AnnApp(AnnAppBase):
    def process(self, path):
        example = np.loadtxt(path, dtype=np.float)
        new_input = example.reshape((1, 3, 1))

        return predictor_instance.predict(new_input)
