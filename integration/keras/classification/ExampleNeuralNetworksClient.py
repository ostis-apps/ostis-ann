# -*- coding: utf-8 -*-
import os
import time

from integration.keras.classification.NeuralNetworksClient import \
	classification

number_image = input(
	"Введите номер изображения с цифрой для распознавания (0..9): ")
check = True
while check == True:
	if number_image == "0" or number_image == "1" or number_image == "2" or number_image == "3" or number_image == "4" or number_image == "5" or number_image == "6" or number_image == "7" or number_image == "8" or number_image == "9":
		check = False
	else:
		print("Необходимо ввести цифру от 0 до 9!")
		number_image = input(
			"Введите номер изображения с цифрой для распознавания (0..9): ")

# Загрузка изображения
img_path = number_image + ".jpg"
img_data = None
with open(img_path, "rb") as fh:
	img_data = fh.read()

host = "127.0.0.1"
port = 9090

a = os.getcwd()

start_time = time.time()
print(classification(host, port, "lenet", "classification_max", img_data))
print("Время обработки запроса: %.5f секунд" % (time.time() - start_time))
