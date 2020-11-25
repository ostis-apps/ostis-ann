import numpy as np

from neural_networks.ann_app_base import AnnAppBase
from neural_networks.sequence_prediction.predictor import predictor_instance


class AnnApp(AnnAppBase):
    def process(self, path):
        example = np.loadtxt(path, dtype=np.int)

        return predictor_instance.predict([example])[0][0]
