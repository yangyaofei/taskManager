#coding:utf-8
import socket
BUFF_SIZE = 1024
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(('localhost',8001))

def send(data):
	sock.send(data)
def recv():
	szBuf = ''
	while(True):
		buf = sock.recv(BUFF_SIZE)
		szBuf += buf
		if(len(buf) < BUFF_SIZE):
			break
	return szBuf
def close():
	sock.close()
