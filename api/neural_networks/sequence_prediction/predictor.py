import os
import numpy

from keras.layers import RepeatVector
from keras.layers import TimeDistributed
from tensorboard.errors import NotFoundError
from tensorflow.python.keras.layers import Bidirectional, LSTM, Dense
from tensorflow.python.keras.models import Sequential


class Predictor:
    def __init__(self):
        self.model = Sequential()

    def train(self):
        models_path = self.config_provider.get_training_model_path('sequence_prediction')
        model_path = os.path.join(models_path, 'awesome_model.tf')

        # try:
        #     self.model.load_weights(model_path)
        # finally:
        #     print("sequence_prediction: No model found or problem during loading. Creating a new model...")

        originals = [float(x) for x in range(5, 301, 5)]
        projection = [float(y) for y in range(20, 316, 5)]

        originals_reshaped = numpy.array(originals).reshape(20, 3, 1)
        projection_reshaped = numpy.array(projection).reshape(20, 3, 1)

        self.model.add(Bidirectional(LSTM(100, activation='relu', input_shape=(3, 1))))
        self.model.add(RepeatVector(3))
        self.model.add(Bidirectional(LSTM(100, activation='relu', return_sequences=True)))
        self.model.add(TimeDistributed(Dense(1)))
        self.model.compile(optimizer='adam', loss='mse')

        self.model.fit(originals_reshaped, projection_reshaped, epochs=150, validation_split=0.2, batch_size=3)
        self.model.save_weights(model_path)

    def predict(self, new_input):
        return self.model.predict(new_input, verbose=0)


predictor_instance = Predictor()
