# -*- coding: utf-8 -*-
import socket


def create_request(part1, part2, data=None):
	""" Объединение заголовка и тела запроса с указанием общего размера всех передаваемых данных. """
	len_part1 = len(part1)
	len_part2 = len(part2)
	if data != None:
		len_part2 += len(data)

	len_response = str(len_part1 + len_part2)
	len_response = str(len_part1 + len_part2 + len(len_response))

	if data != None:
		return (part1 + str(
			len_part1 + len_part2 + len(len_response)) + part2).encode(
			"utf-8") + data
	else:
		return (
			part1 + str(
				len_part1 + len_part2 + len(len_response)) + part2).encode(
			"utf-8")


def classification(host, port, type_neural_network, type_operation,
				   image_to_classificate=None):
	""" Поддерживается два режима:
		1. Классификация:
			1.1. type_operation = classification_max - классификация с помощью полностью обученной сети.
			1.2. image_to_classificate - изображение цифры в виде бинарной строки.
			1.3. Вовращаемое значение - строка с распознанной цифрой, либо ошибка с кратким пояснением.
		2. Обучение:
			2.1. type_operation = training - обучение сети по новой с параметрами по умолчанию.
			2.2. image_to_classificate = None
			2.3. Возвращаемое значение - строка с результатом обучения (либо с ошибкой): точность классификации на тестовой выборке и длительность обучения в минутах.
		Имеющиеся нейронные сети:
		1. type_neural_network = lenet - СНС LeNet5. Предназначена для распознавания рукописных цифр (одна цифра на одном изображении). Обучение и тестрование проводится на выборке MNIST. """
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		client_socket.connect((host, port))
	except Exception as e:
		client_socket.close()
		return "Error: " + str(e)

	request_part1 = "POST classificate/" + type_neural_network + "/" + type_operation + " HTTP/1.1\r\nClient: v0.1\r\nContent-Length: "
	request_part2 = "\r\n\r\n"

	request = create_request(request_part1, request_part2,
							 image_to_classificate)
	client_socket.send(request)

	recv_data = client_socket.recv(1024)

	# Выделение из полученных данных заголовка ответа
	header = recv_data[:recv_data.find(b"\r\n\r\n") + 4].decode("utf-8")
	data = None

	# Приём остальной части ответа, если его общая длина больше 1024 байт
	if header.find("Content-Length:") != -1:
		try:
			# Определение размера получаемых данных
			len_data = header[header.find("Content-Length:"):]
			len_data = len_data[len_data.find(":") + 1:len_data.find("\r\n")]
			if len_data.find(" ") != -1:
				len_data = len_data[len_data.find(" ") + 1:]
			len_data = int(len_data)

			# Получение недостающих данных
			curr_len_data = len(recv_data)
			while curr_len_data < len_data:
				recv_data += client_socket.recv(1024)
				curr_len_data = len(recv_data)

			# Выделение из полученных данных тела ответа
			data = recv_data[recv_data.find(b"\r\n\r\n") + 4:].decode("utf-8")
		except Exception as e:
			print("Error: " + str(e))

	client_socket.close()
	return data
