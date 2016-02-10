#!/usr/bin/python

import socket
import thread
import parse
import request
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
def dealClient(conn,addr):
	szBuf = conn.recv(1024); 
	print("getData") 
	recv = request.routeRequest(szBuf)
	print(repr(recv))
	conn.send(recv)	
def addTask():
	print("addTask")
def listTask():
	print("listTask")
if "__main__" == __name__:  
	try:  
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);  
		print("create socket succ!");  
		sock.bind(('localhost', 8001));  
		print("bind socket succ!");  
          
	        sock.listen(5);  
		print("listen succ!");  
  
	except:  
		print("init socket err!");  
  
	while True:  
		print("listen for client...");  
		conn, addr = sock.accept();  
        	print("get client");  
	        print(addr);  
		thread.start_new_thread(dealClient,(conn,addr))
