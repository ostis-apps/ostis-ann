import numpy
import numpy as np
from datetime import datetime

from neural_networks.ann_app_base import AnnAppBase
from neural_networks.sequence_prediction.predictor import predictor_instance
import matplotlib.pyplot as plot


class AnnApp(AnnAppBase):
    def process(self, path):
        loaded_sin_input = numpy.sin(np.loadtxt(path, dtype=np.float))
        reshaped_input = loaded_sin_input.reshape((1, predictor_instance.input_shape_size, 1))
        predicted = predictor_instance.predict(reshaped_input)

        input_plot = reshaped_input.reshape(predictor_instance.input_shape_size, 1)
        predicted_plot = predicted.reshape(predictor_instance.input_shape_size, 1)

        plot.plot(input_plot, color='g', label='input')
        plot.plot(range(len(input_plot), len(input_plot) + predictor_instance.input_shape_size),
                  predicted_plot, color='m', label='predicted')
        plot.title(datetime.now())
        plot.legend()

        saved_path = f'{path}_processed.png'
        plot.savefig(saved_path)
        plot.clf()

        return list(predicted_plot.reshape(predictor_instance.input_shape_size)), saved_path
