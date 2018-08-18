# -*- coding: utf-8 -*-
from datetime import datetime
from threading import Thread

server_version = "0.1"


class ClientWorking(Thread):
	def __init__(self, client_socket, client_addr, lenet):
		Thread.__init__(self)
		self.client_socket = client_socket
		self.client_addr = client_addr
		self.lenet = lenet
		pass

	def run(self):
		""" Запуск потока для обработки клиента. """
		try:
			# По истечении 60 секунд клиент будет принудительно отключён
			self.client_socket.settimeout(60)

			print('\n%s [INFO] | Подключился клиент %s:%s' % (
				datetime.now(), self.client_addr[0], self.client_addr[1]))
			while True:
				recv_data = self.client_socket.recv(1024)

				# Если клиент отключился - выход из цикла
				if not recv_data:
					break

				# Обработка принятых данных и генерация ответа
				send_data = self.__request_processing(recv_data)

				self.client_socket.send(send_data.encode("utf-8"))

		except Exception as e:
			print("%s [ERROR] | %s:%s | Error: %s" % (
				datetime.now(), self.client_addr[0], self.client_addr[1], e))

		self.client_socket.close()
		print("%s [INFO] | Клиент %s:%s отключён.\n" % (
			datetime.now(), self.client_addr[0], self.client_addr[1]))
		pass

	def __request_processing(self, recv_data):
		""" Обработка принятого запроса. """
		error_response_header = "HTTP/1.1 400 Bad Request\r\nServer: NeuralNetworks_v" + server_version + "\r\nContent-Length: "
		server_error_header = "HTTP/1.1 500 Internal Server Error\r\nServer: NeuralNetworks_v" + server_version + "\r\nContent-Length: "

		# Выделение из полученных данных заголовка запроса
		header = recv_data[:recv_data.find(b"\r\n\r\n") + 4].decode("utf-8")
		data = None

		# Приём остальной части запроса, если его общая длина больше 1024 байт
		if header.find("Content-Length:") != -1:
			try:
				# Определение размера получаемых данных
				len_data = header[header.find("Content-Length:"):]
				len_data = len_data[
						   len_data.find(":") + 1:len_data.find("\r\n")]
				if len_data.find(" ") != -1:
					len_data = len_data[len_data.find(" ") + 1:]
				len_data = int(len_data)

				# Получение недостающих данных
				curr_len_data = len(recv_data)
				while curr_len_data < len_data:
					recv_data += self.client_socket.recv(1024)
					curr_len_data = len(recv_data)

				# Выделение из полученных данных тела запроса
				data = recv_data[recv_data.find(b"\r\n\r\n") + 4:]
			except Exception as e:
				return self.__create_response(server_error_header, "\r\n\r\n",
											  "Error: " + str(e))
		else:
			return self.__create_response(error_response_header, "\r\n\r\n",
										  "Error: в заголовке запроса обязательно должна быть указана его длина.")

		# Обработка запроса
		if header.find("POST") != -1:
			return self.__POST(header, data)
		else:
			return self.__create_response(error_response_header, "\r\n\r\n",
										  "Error: данный запрос не поддерживается.")

	def __POST(self, header, data):
		""" Обработка запроса POST. """
		error_server_response_header = "HTTP/1.1 500 Internal Server Error\r\nServer: NeuralNetworks_v" + server_version + "\r\nContent-Length: "
		error_response_header = "HTTP/1.1 404 Not Found\r\nServer: NeuralNetworks_v" + server_version + "\r\nContent-Length: "
		normal_response_header = "HTTP/1.1 200 OK\r\nServer: NeuralNetworks_v" + server_version + "\r\nContent-Length: "

		# Выделение из заголовка запроса типа нейронной сети и действия с ней
		type_neural_network = header[
							  header.find("POST") + 5:header.find("HTTP") - 1]
		type_neural_network = type_neural_network[
							  type_neural_network.find("/") + 1:]

		type_operation = type_neural_network[
						 type_neural_network.find("/") + 1:]
		type_neural_network = type_neural_network[
							  :type_neural_network.find("/")]

		if type_neural_network == "lenet":
			if type_operation == "classification_max":
				result = self.lenet.classification_max(data, self.client_addr)
				if result == "-1":
					return self.__create_response(normal_response_header,
												  "\r\n\r\n",
												  "Error: сеть " + type_neural_network + " на данный момент обучается. Повторите запрос позже.")
				if result == "-2":
					return self.__create_response(error_server_response_header,
												  "\r\n\r\n",
												  "Error: входное изображение имеет неверный формат (необходима бинарная строка).")
				return self.__create_response(normal_response_header,
											  "\r\n\r\n", str(result))
			elif type_operation == "training":
				print(
					"%s:%s | Инициировано обучение сети с параметрами по умолчанию на выборке mnist." % (
						self.client_addr[0], self.client_addr[1]))
				return self.__create_response(normal_response_header,
											  "\r\n\r\n",
											  self.lenet.training())
			else:
				return self.__create_response(error_response_header,
											  "\r\n\r\n",
											  "Error: опреация " + type_operation + " не поддерживается для сети " + type_neural_network + ".")
		else:
			return self.__create_response(error_response_header, "\r\n\r\n",
										  "Error: сеть " + type_neural_network + " не поддерживается.")

	def __create_response(self, part1, part2, data=None):
		""" Объединение заголовка и тела ответа с указанием общего размера всех передаваемых данных. """
		len_part1 = len(part1)
		len_part2 = len(part2)
		if data != None:
			len_part2 += len(data)

		len_response = str(len_part1 + len_part2)
		len_response = str(len_part1 + len_part2 + len(len_response))

		if data != None:
			return part1 + str(
				len_part1 + len_part2 + len(len_response)) + part2 + data
		else:
			return part1 + str(
				len_part1 + len_part2 + len(len_response)) + part2
