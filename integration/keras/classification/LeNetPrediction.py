# -*- coding: utf-8 -*-
import time

import numpy
from tensorflow.python.keras.models import model_from_json
from tensorflow.python.keras.preprocessing import image

number_image = input(
	"Введите номер изображения с цифрой для распознования (0..9): ")
check = True
while check == True:
	if number_image == "0" or number_image == "1" or number_image == "2" or number_image == "3" or number_image == "4" or number_image == "5" or number_image == "6" or number_image == "7" or number_image == "8" or number_image == "9":
		check = False
	else:
		print("Необходимо ввести цифру от 0 до 9!")
		number_image = input(
			"Введите номер изображения с цифрой для распознования (0..9): ")

# Загрузка изображения
start_time = time.time()
img_path = number_image + ".jpg"
img = image.load_img(img_path, target_size=(28, 28), grayscale=True)

# Преобразование изображения в массив numpy
x = image.img_to_array(img)

# Инвертирование цвета и нормализация
x = 255 - x
x /= 255
x = numpy.expand_dims(x, axis=0)

# Загрузка модели из файла
json_file = open("lenet_model.json", "r")
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)

# Загрузка весов в модель
model.load_weights("lenet_weights.h5")

# Компиляция модели
model.compile(loss="categorical_crossentropy", optimizer="adam",
			  metrics=["accuracy"])

# Распознавание
prediction = model.predict(x)
prediction = numpy.argmax(prediction)
print("На изображении цифра %d" % prediction)
print("Время распознавания: %f секунд." % (time.time() - start_time))
