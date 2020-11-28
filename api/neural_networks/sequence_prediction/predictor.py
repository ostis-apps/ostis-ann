import os
import numpy

from keras.layers import RepeatVector
from keras.layers import TimeDistributed
from tensorflow.python.keras.layers import Bidirectional, LSTM, Dense
from tensorflow.python.keras.models import Sequential


class Predictor:
    def __init__(self):
        self.input_shape_size = 10
        self.model = Sequential()

        self.model.add(Bidirectional(LSTM(100, activation='relu', input_shape=(self.input_shape_size, 1))))
        self.model.add(RepeatVector(self.input_shape_size))
        self.model.add(Bidirectional(LSTM(100, activation='relu', return_sequences=True)))
        self.model.add(TimeDistributed(Dense(1)))
        self.model.compile(optimizer='adam', loss='mse')

    def train(self):
        models_path = self.config_provider.get_training_model_path('sequence_prediction')
        model_path = os.path.join(models_path, 'awesome_model.tf')

        try:
            self.model.load_weights(model_path)
        except BaseException:
            print("sequence_prediction: No model found or problem during loading. Creating a new model...")

            training_set_length = 5
            originals = [[numpy.sin(float(x)) for x in range(0, 10, 1)],
                         [numpy.sin(float(x)) for x in range(1, 11, 1)],
                         [numpy.sin(float(x)) for x in range(2, 12, 1)],
                         [numpy.sin(float(x)) for x in range(3, 13, 1)],
                         [numpy.sin(float(x)) for x in range(4, 14, 1)]]
            projection = [[numpy.sin(float(x)) for x in range(11, 21, 1)],
                          [numpy.sin(float(x)) for x in range(12, 22, 1)],
                          [numpy.sin(float(x)) for x in range(13, 23, 1)],
                          [numpy.sin(float(x)) for x in range(14, 24, 1)],
                          [numpy.sin(float(x)) for x in range(15, 25, 1)]]

            originals_reshaped = numpy.array(originals).reshape(training_set_length, self.input_shape_size, 1)
            projection_reshaped = numpy.array(projection).reshape(training_set_length, self.input_shape_size, 1)

            self.model.fit(originals_reshaped, projection_reshaped, epochs=1000, validation_split=0.2, batch_size=3)
            self.model.save_weights(model_path)

    def predict(self, new_input):
        return self.model.predict(new_input, verbose=0)


predictor_instance = Predictor()
