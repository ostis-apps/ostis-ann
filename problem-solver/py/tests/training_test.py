import tensorflow as tf
import numpy
from fashion_converter import Converter


# TODO: вынести в отдельный класс+, поменять пути на относительные(унифицировать, по возможности), приём путей из sc-структуры(это уже в агента внести), приём множества элементов из sc (типо мы определяем цифры, нам на вход приходят пути + множество цифр)

model_path = 'problem-solver/py/tests/fashion.keras'
data_path = 'problem-solver/py/tests/image_test.png'
model = tf.keras.models.load_model(model_path)
model_input_data = Converter.convert(data_path)

# TODO: вынести в работу агента + 
predictions = model.predict(model_input_data)
score = tf.nn.softmax(predictions[0])
print(numpy.max(score*100)//1)

# TODO: добавить составление выходных данных в sc