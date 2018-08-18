# -*- coding: utf-8 -*-
from integration.keras.classification.NeuralNetworkAPI import classificate

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
img_path = number_image + ".jpg"
img_data = None
with open(img_path, 'rb') as fh:
	img_data = fh.read()
# print(img_data)

print(classificate(img_data, "lenet_classification_max"))
