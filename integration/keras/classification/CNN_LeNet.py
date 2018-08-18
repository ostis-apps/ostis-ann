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

# Для повторяемости результатов (опорное значение для генератора случайных чисел)
numpy.random.seed(42)


class LeNet:
	def __init__(self, default_graph):
		self.model_classification_max = None
		self.default_graph = default_graph
		self.init_classification_max()
		self.is_training = False
		pass

	def training(self):
		""" Обучение сети на тестовой выборке рукописных цифр mnist с параметрами по умолчанию.
		Возвращает строку, содержащую: точность классификации на тестовых данных и затраченное на обучение время. """
		self.is_training = True

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

		# Создание модели однонаправленной (последовательной) сети
		model = Sequential()

		start_time = None
		end_time = None
		scores = None

		# Нужно для того, что бы в вычислениях исползовать граф вычислений tensorflow, заданный по умолчанию при загрузке всех модулей
		with self.default_graph.as_default():
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
			# объект (т.е. происходит передача сигналов между предыдущим слоем и следующим), случайным образом отключаются нейроны
			# с вероятностью 0.2, т.е. вероятность 20% того, что нейрон не будет участвовать в обучении на следующем слое, он будет «отключён»)
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
			print("Точность работы на тестовых данных: %.2f%%" % (
				scores[1] * 100))
			end_time = time.time()
			print("Время обучения: %d секунд." % (end_time - start_time))

			# Генерация описания модели в формате json и запись её в файл
			model_json = model.to_json()
			json_file = open("lenet_model.json", "w")
			json_file.write(model_json)
			json_file.close()

			# Сохранение весов в файл (для работы необходим пакет h5py (sudo pip3 install h5py) и libhdf5-dev (sudo apt-get install libhdf5-dev))
			model.save_weights("lenet_weights.h5")

			self.is_training = False
			self.init_classification_max()
			return "Обучение завершено. Точность классификации на тестовой выборке %.2f%%, время обучения: %.2f минут." % (
				scores[1] * 100, (end_time - start_time) / 60)

	def init_classification_max(self):
		""" Загрузка модели сети и её весов из файлов, компиляция полученной сети и проверка её работоспособности. """
		# Загрузка модели из файла
		json_file = open("lenet_model.json", "r")
		loaded_model_json = json_file.read()
		json_file.close()
		self.model_classification_max = model_from_json(loaded_model_json)

		# Загрузка весов в модель
		self.model_classification_max.load_weights("lenet_weights.h5")

		# Компиляция модели
		self.model_classification_max.compile(loss="categorical_crossentropy",
											  optimizer="adam",
											  metrics=["accuracy"])

		# Загрузка тестового изображения
		test_image_value = 0
		recognize_image = pilImage.open("test_classification_lenet.jpg")
		recognize_image = recognize_image.convert('L')
		recognize_image.thumbnail((28, 28), pilImage.ANTIALIAS)

		# Преобразование изображения в массив numpy
		x = image.img_to_array(recognize_image)

		# Инвертирование цвета и нормализация
		x = 255 - x
		x = x / 255
		x = numpy.expand_dims(x, axis=0)

		# Распознавание
		prediction = self.model_classification_max.predict(x)
		prediction = int(numpy.argmax(prediction))
		if prediction == test_image_value:
			print("Тестовое изображение классифицированно правильно.")
		else:
			print(
				"Error: тестовое изображение классифицировано неверно. Обучите сеть заново.")
		pass

	def classification_max(self, recognize_image, client_addr):
		""" Классификация (для полностью обученной сети):
			1. recognize_image - изображение в виде бинарной строки.
			2. client_addr - адрес клиента для вывода информационных сообщений.
			Возвращаемое значение - распознанная цифра, int от 0 до 9. """
		if self.is_training == True:
			print("%s:%s | Сеть недоступна, выполняется обучение сети." % (
				client_addr[0], client_addr[1]))
			return "-1"

		start_time = time.time()

		try:
			# Преобразование бинарной строки в PIL Image
			stream = BytesIO(recognize_image)
			recognize_image = pilImage.open(stream)

			# Если изображение прямоугольное, то преобразование его в квадратное
			width, height = recognize_image.size
			if width > height:
				background = pilImage.new('RGB', (width, width),
										  (255, 255, 255))
				background.paste(recognize_image, (0, (width - height) // 2))
				recognize_image = background
			elif width < height:
				background = pilImage.new('RGB', (height, height),
										  (255, 255, 255))
				background.paste(recognize_image, ((height - width) // 2, 0))
				recognize_image = background

			# Преобразование изображение в чёрно-белое и уменьшение размера до 28х28
			recognize_image = recognize_image.convert('L')
			recognize_image.thumbnail((28, 28), pilImage.ANTIALIAS)
		except Exception as e:
			print("%s:%s | Error: %s" % (client_addr[0], client_addr[1], e))
			return "-2"

		# Преобразование изображения в массив numpy
		x = image.img_to_array(recognize_image)

		# Инвертирование цвета и нормализация
		x = 255 - x
		x = x / 255
		x = numpy.expand_dims(x, axis=0)

		# Распознавание
		prediction = self.model_classification_max.predict(x)
		prediction = int(numpy.argmax(prediction))
		print(
			"%s:%s | На изображении цифра %d, время распознавания: %f секунд." % (
				client_addr[0], client_addr[1], prediction,
				(time.time() - start_time)))
		return prediction
