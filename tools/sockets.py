# coding:utf-8
import socket
from tools import config

"""
配置文件变量:
global:
socket_port		: server端口
socket_buffer	: socket通信buffer大小
queue			: server与taskManager之间队列大小

"""
BUFF_SIZE = config.get()["socket_buffer"]
SOCKET_PORT = config.get()["socket_port"]


def createSocket():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("localhost", SOCKET_PORT))
	s.listen(5)
	return s


def connectServer():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('localhost', 8001))
	return s


def recv(sock):
	szBuf = ''
	while(True):
		buf = sock.recv(BUFF_SIZE)
		szBuf += buf
		if len(buf) < BUFF_SIZE:
			break
	return szBuf
