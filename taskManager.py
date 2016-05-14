# coding:utf-8
import multiprocessing
import threading
import tasker
# import taskDB
import parse
from logger import logger


class TaskerManager(multiprocessing.Process):
	def __init__(self, queue):
		multiprocessing.Process.__init__(self)
		self.queue = queue

	def run(self):
		lock = threading.Lock()
		taskerList = {}  # 用task_ID为key,内容是Process的字典
		# 启动一个线程去获取数据
		t = threading.Thread(target=request, args=(self.queue, taskerList, lock))
		t.start()
		while True:
			handleTasker(taskerList, lock)
		# lock.acquire()
		# lock.release()


def request(queue, taskerList, lock):
	while True:
		data = queue.get_nowait()
		logger.info("get a data")
		route(data, taskerList, lock)


def route(data, taskerList, lock):
	if data[parse.MAIN_KEY[1]] == "B":
		return startTask(rawdata)
	elif data[parse.MAIN_KEY[1]] == "S":
		return stopTask(raw_data)


def handleTasker(taskerList, lock):
	# 每次处理进程列表中已经终止的那些
	# 前期先不管状态如何,后期可以根据退出的状态进行不同的操作
	# TODO
	for t in taskerList:
		if not taskerList.is_alive():
			tasker[t].join()
			lock.acquire()
			taskerList.remove(t)
			lock.release()


def startTask(task_ID, taskerList, lock):
	# 检查状态是否可以start
	# 修改状态为s fork() execl() 传值ID等
	# 不在这一层做处理,在tasker做处理
	if task_ID not in taskerList:
		return
	tasker.startTasker(task_ID, taskerList, lock)


def stopTask(task_ID, taskerList, lock):
	# 根据PID终止进程,修改数据库任务状态 删除相关结果 返回
	if not taskerList[task_ID]:
		return
	taskerList[task_ID].tereminal()
	taskerList[task_ID].join()
	lock.acquire()
	taskerList.remove(task_ID)
	lock.release()


def pauseTask():
	# 最后实现
	return

'''
				fork() execl() kill
	taskManager----------------------->tasker
taskManager:
	由request调用,然后在taskManager中进行数据库的存储,fork等工作
	维护一个临时列表,记录子进程(tasker)的状态以及PID,并与数据库中比较,
如果不同,则进行更新,特别是已经不存在的进程则标记为error或者stop
	维护临时列表的时间是在request调用时调用
tasker:
	由taskManger fork后利用execl执行tasker,仅执行任务,并把任务状态实时
写入数据库中,不与taskeManager通信.

'''
