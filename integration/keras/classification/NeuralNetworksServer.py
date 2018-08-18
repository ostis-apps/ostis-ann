# -*- coding: utf-8 -*-
import curses
import os
import platform
import signal
import socket
import sys
from datetime import datetime

import tensorflow
from CNN_LeNet import LeNet

from integration.keras.classification.ClientWorking import ClientWorking

host = "127.0.0.1"
port = 9090


# Необходимо для корректного закрытия сокетов при выходе из программы.
def on_stop(*args):
	print(" Сервер остановлен.")
	sys.exit(0)


# При нажатии комбинаций Ctrl+Z, Ctrl+C либо закрытии терминала будет вызываться функция on_stop() (Работает только на linux системах!)
if platform.system() == "Linux":
	for sig in (signal.SIGTSTP, signal.SIGINT, signal.SIGTERM):
		signal.signal(sig, on_stop)

# Сохранение графа вычислений tensorflow по умолчанию для передачи его в другой поток
default_graph = tensorflow.get_default_graph()

# Инициализация сети LeNet для распознавания рукописных цифр.
lenet = LeNet(default_graph)

img_path = "1.jpg"
img_data = None
with open(img_path, "rb") as fh:
	img_data = fh.read()

# Если есть аргументы командной строки - считывание их, иначе запрос на ввод адреса сервера с клавиатуры.
if len(sys.argv) > 1:
	if sys.argv[1].find(":") != -1:
		host = sys.argv[1][:sys.argv[1].find(":")]
		port = int(sys.argv[1][sys.argv[1].find(":") + 1:])
	else:
		print(
			"Второй параметр должен содержать адрес сервера в виде host:port!")
		sys.exit()
else:
	curses.setupterm()
	print(
		"\nВведите адрес сервера, либо пропустите, что бы использовать локальный адрес.")
	temp_host = input("Введите хост: ")
	if temp_host != "":
		host = temp_host
	else:
		os.write(sys.stdout.fileno(), curses.tigetstr('cuu1'))
		print("Введите хост: " + str(host))

	temp_port = input("Введите порт: ")
	if temp_port != "":
		port = int(temp_port)
	else:
		os.write(sys.stdout.fileno(), curses.tigetstr('cuu1'))
		print("Введите порт: " + str(port))

# Создание и привязка сокета
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	server_socket.bind((host, port))
except Exception as e:
	print("Error: %s" % e)
	sys.exit()
print(
	"\n%s [INFO] | Сервер запущен, адрес: %s:%d. Ожидание подключений...\n" % (
		datetime.now(), host, port))

# Обработка клиентов
while True:
	server_socket.listen(5)
	client_socket, client_addr = server_socket.accept()
	new_client_thread = ClientWorking(client_socket, client_addr, lenet)
	new_client_thread.start()
