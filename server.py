#!/usr/bin/python
# coding:utf-8
import thread
import sys
import getopt
import traceback
import multiprocessing
import taskManager
from tools import sockets
from tools import daemon
from tools import parse
from tools.logger import logger
from tools import config
from DB import taskDB
reload(sys)
sys.setdefaultencoding("utf-8")
# data 为处理好的数据 判断其中内容后直接执行相关请求


# TODO
# 	一个想法,是否应该将server部分作为一个单独的进程而将后
# 	台的部分作为另外一个单独的进程,这样做的好处就是server
# 	部分由于后台任务管理导致前台不能接受请求和数据的问题
# 	但问题是值得这样写么,毕竟不会有这么多的请求.所以先将这
# 	个问题列为TODO,等以后没事儿的时候实现
#
# 需要写一些判断,保证数据真的传过来了
# 如 addTask中的判断一样
# if name is None or name is None or type is None or para is None:
# 		logger.info("get wrong data")


class SocketServer(multiprocessing.Process):
	def __init__(self, queue):
		multiprocessing.Process.__init__(self)
		self.queue = queue

	def run(self):
		try:
			socket = sockets.createSocket()
			logger.info("create socket succ!")
			while True:
				logger.info("listen for client...")
				conn, addr = socket.accept()
				logger.info("get client:" + str(addr))
				thread.start_new_thread(self.dealClient, (conn, addr))
		except:
			logger.error("init socket err!")
			logger.error(traceback.format_exc())
			traceback.print_exc()
			socket.close()
		finally:
			socket.close()

	def dealClient(self, conn, addr):
		try:
			szBuf = sockets.recv(conn)
			logger.info("get a request")
			recv = self.routeRequest(szBuf)
			lenth = conn.send(recv)
			logger.info("respons the request over,send " + str(lenth) + "data")
		except:
			logger.error("error in dealwith client close this connection")
			logger.error(traceback.format_exc())
			traceback.print_exc()
		finally:
			conn.close()

	def routeRequest(self, raw_data):
		data = parse.parseTo(raw_data)
		logger.info("identify data[" + str(data) + "] and route it")
		if data[parse.MAIN_KEY.request] == parse.REQUEST.startTask:
			return self.startTask(data)
		elif data[parse.MAIN_KEY.request] == parse.REQUEST.stopTask:
			return self.stopTask(data)
		else:
			return parse.responseError()

	def startTask(self, data):
		task_ID = parse.paresID(data)
		if task_ID is None:
			return parse.responseError()
		task = taskDB.getTaskInfo(task_ID)
		if task.task_status != parse.TASK_STATUS.addTask:
			return parse.responseError()
		self.queue.put(data)
		logger.info("startTask task_ID:" + str(task_ID))
		return parse.responseOK()

	def stopTask(self, data):
		task_ID = parse.paresID(data)
		if task_ID is None:
			return parse.responseError()
		task = taskDB.getTaskInfo(task_ID)
		if task.task_status != parse.TASK_STATUS.process:
			return parse.responseError()
		self.queue.put(data)
		logger.info("stopTask task_ID:" + str(task_ID))
		return parse.responseOK()


def printHelp():
	print("help")


def printVersion():
	print("version")

# 选项处理
shortopt = 'd:h'
longopt = ["daemon=", "help", "version", "pid-file=", "log-file="]
optlist, argvs = getopt.getopt(sys.argv[1:], shortopt, longopt)
opt_config = {}
for key, value in optlist:
	if(key == "-d"):
		opt_config["daemon"] = value
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
		opt_config["daemon"] = value
	elif(key == "--pid-file"):
		opt_config["pid-file"] = value
	elif(key == "--log-file"):
		opt_config["log-file"] = value
opt_config["pid-file"] = opt_config.get("pid-file", "/var/run/nlpServer.pid")
opt_config["log-file"] = opt_config.get("log-file", "/var/log/nlpServer.log")
daemon.daemon_exec(opt_config)
# END

# 读取配置文件
QUEUE_MAX = (config.get())["queue"]

queue = multiprocessing.Queue(QUEUE_MAX)

server = SocketServer(queue)
server.daemon = True
manager = taskManager.TaskerManager(queue)
# manager.daemon = True
server.start()
manager.start()
server.join()
manager.join()
# 锁 start task
