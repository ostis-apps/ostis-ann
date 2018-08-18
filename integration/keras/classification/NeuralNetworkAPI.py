# -*- coding: utf-8 -*-
import time
from io import BytesIO

import numpy
from PIL import Image as pilImage
from tensorflow.python.keras import utils
from tensorflow.python.keras.datasets import mnist
from tensorflow.python.keras.layers import Conv2D, MaxPooling2D
from tensorflow.python.keras.layers import Dense, Dropout, Flatten
from tensorflow.python.keras.models import Sequential, model_from_json
from tensorflow.python.keras.preprocessing import image


def lenet_training():
	# Для повторяемости результатов (опорное значение для генератора случайных чисел)
	numpy.random.seed(42)

	# Размер изображения в обучающей выборке
	img_width, img_height = 28, 28

	# Загрузка обучающей выборки mnist (X_train и X_test - наборы изображений с цифрами, y_train и y_test -
	# цифры, которые на них изображены (т.е. правильные ответы, метки классов))
	(X_train, y_train), (X_test, y_test) = mnist.load_data()

	# Преобразование размерности изображений (смена строк и столбцов местами, в трёхмерный массив n x m x p,
	# где n - номер изображения, m - столбец в изображении, p - строка)
	X_train = X_train.reshape(X_train.shape[0], img_width, img_height, 1)
	X_test = X_test.reshape(X_test.shape[0], img_width, img_height, 1)
	input_shape = (img_width, img_height, 1)

	# Нормализация данных (перевод значений в диапазон 0..1)
	X_train = X_train.astype("float32")
	X_test = X_test.astype("float32")
	X_train /= 255
	X_test /= 255

	# Преобразование меток в категории (категория - массив из 10 элементов, где все элементы равны 0 кроме того,
	# который является ответом, он равен 1)
	Y_train = utils.to_categorical(y_train, 10)
	Y_test = utils.to_categorical(y_test, 10)

	# Создание модели сети
	model = Sequential()

	# Слой свертки, 75 карт признаков, размер ядра свертки: 5х5
	# Представляет из себя разбиение каждого изображения на матрицы 5х5, интенсивность цвета каждого пикселя умножается
	# на веса соответствующего данной части изображения нейрона, результаты суммируются и передаются дальше
	# 75 карт признаков - т.е. 75 наборов слоёв, которые используют разные ядра свёртки (т.е. по сути, выделяют 75 признаков)
	model.add(Conv2D(75, kernel_size=(5, 5), activation="relu",
					 input_shape=input_shape))
	# Слой подвыборки (субдискретизирующий слой), размер пула 2х2
	# Нужен что бы распознавать цифры разного масштаба на изображении, на этом слое берутся результаты матрицы нейронов 2х2
	# предыдущего слоя и выбирается из них максимальное
	# Dropout - слой регуляризации, нужен что бы предотвратить переобучение (на этом слое каждый раз, когда подаётся новый
	# объект, случайным образом отключаются нейроны с заданной вероятностью)
	model.add(MaxPooling2D(pool_size=(2, 2)))
	model.add(Dropout(0.2))
	# Слой свертки, 100 карт признаков, размер ядра свертки 5х5
	model.add(Conv2D(100, kernel_size=(5, 5), activation="relu"))
	# Слой подвыборки, размер пула 2х2
	model.add(MaxPooling2D(pool_size=(2, 2)))
	model.add(Dropout(0.2))
	# Полносвязный слой, 500 нейронов, необходим для классификации
	# Flatten - преобразование из двумерного вида в одномерный
	# В слое типа Dense происходит соединение всех нейронов предыдущего уровня со всеми нейронами следующего уровня
	model.add(Flatten())
	model.add(Dense(500, activation="relu"))
	model.add(Dropout(0.5))
	# Полносвязный выходной слой, 10 нейронов, которые соответствуют классам рукописных цифр от 0 до 9
	# При успешном распознавании на выходе одного из этих нейронов будет значение, близкое к 1, а на остальных - близкие к 0
	model.add(Dense(10, activation="softmax"))

	# Компиляция модели и вывод данных о ней
	model.compile(loss="categorical_crossentropy", optimizer="adam",
				  metrics=["accuracy"])
	print(model.summary())

	# Обучение сети
	start_time = time.time()
	model.fit(X_train, Y_train, batch_size=200, epochs=10,
			  validation_split=0.2, verbose=2)

	# Оценивание качества обучения на тестовых данных, loss - значение функции ошибки, acc - точность
	scores = model.evaluate(X_test, Y_test, verbose=0)
	print("Точность работы на тестовых данных: %.2f%%" % (scores[1] * 100))
	print("Время обучения: %d секунд." % (time.time() - start_time))

	# Генерация описания модели в формате json и запись её в файл
	model_json = model.to_json()
	json_file = open("lenet_model.json", "w")
	json_file.write(model_json)
	json_file.close()

	# Сохранение весов в файл (для работы необходим пакет h5py (sudo pip3 install h5py) и libhdf5-dev (sudo apt-get install libhdf5-dev))
	model.save_weights("lenet_weights.h5")
	pass


def lenet_classification(recognize_image):
	start_time = time.time()

	# Преобразование изображения в массив numpy
	x = image.img_to_array(recognize_image)

	# Инвертирование цвета и нормализация
	x = 255 - x
	x = x / 255
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
	return prediction


map = {}
map.update({"lenet_classification_max": lenet_classification})
map.update({"lenet_teach": lenet_training})


def classificate(recognize_image, type):
	""" Поддерживает два режима:
	1. Классификация:
		recognize_image - изображение в виде бинарной строки.
		type = "lenet_classification_max" - для полностью обученной СНС LeNet.
		Возвращаемое значение - распознанная цифра, int от 0 до 9, если значение type неправильное, то -1.

	2. Обучение:
		recognize_image = None.
		type = "lenet_teach" - для СНС LeNet с параметрами по умолчанию.
		Возвращаемое значение отсутствует."""
	function = map.get(type)
	if function == None:
		return -1
	if recognize_image == None:
		return function()

	stream = BytesIO(recognize_image)
	recognize_image = pilImage.open(stream)
	recognize_image = recognize_image.convert('L')
	recognize_image.thumbnail((28, 28), pilImage.ANTIALIAS)

	return function(recognize_image)
