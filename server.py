#!/usr/bin/python

import socket
import thread
import os
import sys
sys.setdefaultencoding("utf-8")
import getopt
import logging
reload(sys)

import daemon
import parse
import request

logging.getLogger().setLevel(0)
def dealClient(conn,addr):
	szBuf = conn.recv(1024); 
	logging.info("get a request")
	recv = request.routeRequest(szBuf)
	conn.send(recv)	
	logging.info("respons the request over")
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
#print(config)	
#print(optlist)	
daemon.daemon_exec(config)
try:  
	logging.info("create socket succ!");  
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);  
	sock.bind(('localhost', 8001));  
	logging.info("bind socket succ!");  
         
        sock.listen(5);  
	logging.info("listen succ!");  
 
except:  
	logging.error("init socket err!");  
 
while True:  
	logging.info("listen for client...");  
	conn, addr = sock.accept();  
       	logging.info("get client:"+str(addr));  
	thread.start_new_thread(dealClient,(conn,addr))
