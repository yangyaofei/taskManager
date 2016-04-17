#!/usr/bin/python

import socket
import thread
import os
import sys
import getopt
import logger
reload(sys)
sys.setdefaultencoding("utf-8")
import daemon
import parse
import request
from logger import logger
import traceback
def dealClient(conn,addr):
	try:
		MAX_SIZE = 1024
		szBuf = ''
		while(True):
			buf = conn.recv(MAX_SIZE)
			szBuf += buf
			if(len(buf) < MAX_SIZE):
				break
		logger.info("get a request")
		recv = request.routeRequest(szBuf)
		lenth = conn.send(recv)
		logger.info("respons the request over,send "+str(lenth)+"data")
	except:
		logger.error("error in dealwith client close this connection")
		logger.error(traceback.format_exc())
		traceback.print_exc()
	finally:
		conn.close()

def printHelp():
	print("help")
def printVersion():
	print("version")

shortopt = 'd:h'
longopt = ["daemon=","help","version","pid-file=","log-file="]
optlist, argvs = getopt.getopt(sys.argv[1:],shortopt,longopt)
config = {}
for key ,value in optlist:
	if(key == "-d"):
		config["daemon"] = value
	elif(key == "-h"):
		printHelp()
		sys.exit(0)
	elif(key == "--help"):
		printHelp()
		sys.exit(0)
	elif(key == "--version"):
		printVersion()
		sys.exit(0)
	elif(key == "--daemon"):
		config["daemon"] = value
	elif(key == "--pid-file"):
		config["pid-file"] = value
	elif(key == "--log-file"):
		config["log-file"] = value
config["pid-file"] = config.get("pid-file","/var/run/nlpServer.pid")
config["log-file"] = config.get("log-file","/var/log/nlpServer.log")
daemon.daemon_exec(config)
try:  
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);  
	logger.info("create socket succ!");  
	sock.bind(('localhost', 8001));  
	logger.info("bind socket succ!");  
	sock.listen(5);  
	logger.info("listen succ!");  
	while True:  
		logger.info("listen for client...");  
		conn, addr = sock.accept();  
		logger.info("get client:"+str(addr)) 
		thread.start_new_thread(dealClient,(conn,addr))
except:  
	logger.error("init socket err!");
	logger.error(traceback.format_exc()) 
	traceback.print_exc()
	sock.close()
finally:
	sock.close() 


