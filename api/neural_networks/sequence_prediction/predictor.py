import numpy as np


class Predictor:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.weights = np.array([[.50], [.50], [.50]])
        self.error_history = []
        self.epoch_list = []

    # activation function ==> S(x) = 1/1+e^(-x)
    def sigmoid(self, x, deriv=False):
        if deriv == True:
            return x * (1 - x)
        return 1 / (1 + np.exp(-x))

    # data will flow through the neural network.
    def feed_forward(self):
        self.hidden = self.sigmoid(np.dot(self.inputs, self.weights))

    # going backwards through the network to update weights
    def backpropagation(self):
        self.error = self.outputs - self.hidden
        delta = self.error * self.sigmoid(self.hidden, deriv=True)
        self.weights += np.dot(self.inputs.T, delta)

    def train(self, epochs=50000):
        # TODO: extract training to model for further processing
        for epoch in range(epochs):
            # flow forward and produce an output
            self.feed_forward()

            # go back though the network to make corrections based on the output
            self.backpropagation()

            # keep track of the error history over each epoch
            self.error_history.append(np.average(np.abs(self.error)))
            self.epoch_list.append(epoch)

    def predict(self, new_input):
        prediction = self.sigmoid(np.dot(new_input, self.weights))
        return prediction


training_inputs = np.array([[0, 1, 0], [0, 1, 1], [0, 0, 0], [1, 0, 0], [1, 1, 1], [1, 0, 1]])
training_outputs = np.array([[0], [0], [0], [1], [1], [1]])
predictor_instance = Predictor(training_inputs, training_outputs)
