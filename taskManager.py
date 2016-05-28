# coding:utf-8
import multiprocessing
import threading
import traceback
import tasker
import time
import sys
import signal
# import taskDB
from tools import parse
from tools.logger import logger
from DB import taskDB

# TaskManager进程有两个线程
# 主线程:
# 	监视taskList列表中的进程,在其终止时释放他们,并更新taskList
# 副线程:
# 	从queue中获取task信息,并进行相应的操作


class TaskerManager(multiprocessing.Process):
	def __init__(self, queue):
		multiprocessing.Process.__init__(self)
		self.queue = queue
		self.lock = threading.Lock()
		self.taskerList = {}  # 用task_ID为key,内容是Process的字典

	def run(self):
		logger.info("TaskManager start")
		# 处理SIGTERM 信号量
		signal.signal(signal.SIGTERM, self.exit)
		# 先处理上次的错误数据之后,再进入
		self.handleLast()
		# 启动一个线程去获取数据
		t = threading.Thread(target=self.request)  # , args=(self,))
		t.start()
		logger.info("TaskManager getQueue thread start")
		while True:
			# logger.info("check process list")
			self.handleTasker()
			time.sleep(1)
		# lock.acquire()
		# lock.release()

	def exit(self, argv1, argv2):
		# 杀死所有子进程之后退出
		self.lock.acquire()
		for t in self.taskerList:
			self.taskerList[t].terminate()
		self.lock.release()
		sys.exit(0)

	def handleLast(self):
		tasks = taskDB.getAllTaskInfo()
		for t in tasks:
			if t.task_status == parse.TASK_STATUS.process or\
				t.task_status == parse.TASK_STATUS.startTask:
				t.task_status = parse.TASK_STATUS.error
				t.save()

	def request(self):
		try:
			while True:
				data = self.queue.get()
				logger.info("get a data")
				self.route(data)
		except:
			logger.error(traceback.format_exc())

	def route(self, data):
		logger.info("get a data:" + str(data))
		task_ID = parse.paresID(data)
		if data[parse.MAIN_KEY.request] == parse.REQUEST.startTask:
			return self.startTask(task_ID)
		elif data[parse.MAIN_KEY.request] == parse.REQUEST.stopTask:
			return self.stopTask(task_ID)

	def handleTasker(self):
		# 每次处理进程列表中已经终止的那些
		# 前期先不管状态如何,后期可以根据退出的状态进行不同的操作
		# TODO
		self.lock.acquire()
		for t in self.taskerList.keys():
			if not self.taskerList[t].is_alive():
				# 看任务是否完成,没有完成则标记为error
				task = taskDB.getTaskInfo(t)
				if task.task_status == parse.TASK_STATUS.process or\
					task.task_status == parse.TASK_STATUS.startTask:
					task.task_status = parse.TASK_STATUS.error
					task.save()
					logger.info("get a stoped task turn to error")
				self.taskerList[t].join()
				del self.taskerList[t]
		self.lock.release()

	def startTask(self, task_ID):
		self.lock.acquire()
		if task_ID in self.taskerList:
			tasker.taskerToError(task_ID, "star error")
			self.lock.release()
			return
		task = tasker.Tasker(task_ID)
		# task.daemon = True
		task.start()
		if task is not None:
			self.taskerList[task_ID] = task
		self.lock.release()

	def stopTask(self, task_ID):
		self.lock.acquire()
		if task_ID not in self.taskerList:
			tasker.taskerToError(task_ID, "stopTask error No such task")
			self.lock.release()
			return
		logger.info("stopTask :" + str(task_ID))
		self.taskerList[task_ID].terminate()
		logger.info("stopTask over")
		self.taskerList[task_ID].join()
		del self.taskerList[task_ID]
		self.lock.release()

	def pauseTask():
		# 最后实现
		return
