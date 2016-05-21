# coding:utf-8
from DB import taskDB
import signal
from tools import parse
from tools import common
from tools.logger import logger
import multiprocessing
import jieba
from jieba import posseg
import traceback
import sys
import datetime


class TASK_TYPE:
	tfidf = 1


class Tasker(multiprocessing.Process):
	def __init__(self, task_ID):
		multiprocessing.Process.__init__(self)
		self.task_ID = task_ID

	def run(self):
		try:
			signal.signal(signal.SIGTERM, self.exit)
			task = taskDB.getTaskInfo(self.task_ID)
			self.task_para = task.task_para
			if task.task_type == TASK_TYPE.tfidf:
				import tfidfTasker
				tfidfTasker.startTasker(self.task_ID, task.task_para)
				# testTasker(self.task_ID, self.task_para)
		except SystemExit:
			logger.info("tasker exit with sys.exit()")
			exit(0)
		except:
			logger.error("tasker error exit:" + traceback.format_exc())
			taskerToError(self.task_ID, traceback.format_exc())
			sys.exit(-1)

	def exit(self, arg1, arg2):
		logger.info("tasker exit")
		taskerToError(self.task_ID, "stopTasker")
		sys.exit(0)


def time():
	return datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S.%f')


def taskerLog(ID, log):
	data = taskDB.getTaskInfo(ID)
	if data.task_data is None:
		data.task_data = ""
	time_str = time()
	data.task_data += time_str + ":" + log + "\n"
	taskDB.changeTaskInfo(data)


def changeTaskerStatus(ID, message, status):
	data = taskDB.getTaskInfo(ID)
	if data.task_data is None:
		data.task_data = ""
	time_str = time()
	data.task_data += time_str + ":" + message + "\n"
	data.task_status = status
	taskDB.changeTaskInfo(data)


def taskerToError(ID, message):
	logger.error("taskerToError")
	changeTaskerStatus(ID, "taskerError\n" + message, parse.TASK_STATUS.error)


def taskerToComplete(ID):
	msg = "taskerToComplete"
	logger.info(msg)
	data = taskDB.getTaskInfo(ID)
	data.task_finish_time = datetime.datetime.now()
	taskDB.changeTaskInfo(data)
	changeTaskerStatus(ID, msg, parse.TASK_STATUS.complete)


def taskerToStart(ID):
	msg = "taskerToStart"
	logger.info(msg)
	changeTaskerStatus(ID, msg, parse.TASK_STATUS.startTask)


def TaskerToProcess(ID):
	msg = "taskerToProcess"
	logger.info(msg)
	changeTaskerStatus(ID, msg, parse.TASK_STATUS.process)


def initCutter():
	import logging
	jieba.setLogLevel(logging.INFO)
	jieba.load_userdict(common.getProjectPath() + "dict.txt")
	jieba.initialize()


# 只需要名词
# TODO 此处可能使用工具自带方法可以加快速度
def getWordList(texts):
	words = posseg.cut(texts)
	l = []
	for i in words:
		if i.flag.find("n") != -1:
			l.append(i.word)
	return l


# 文本处理部分
# 去掉没用的空格 Tab \r <br>
def removeNULL(data):
	data = data.replace("\r", "")
	data = data.replace("\n", "")
	data = data.replace("\t", "")
	data = data.replace("<br >", "\n")
	data = data.replace("<br />", "\n")
	data = data.replace(" ", "")
	return data

# 下面三个函数是用来去掉没用的词的函数 参数都是词组成的list
PUNC = u'''，。《》？“”‘’：；！、,.<>?"':;!(）()'''


# 出现标点就去掉
def puncFilter(wordsList, punc):
	for p in PUNC:
		i = 0
		while i < len(wordsList):
			if wordsList[i].find(p) != -1:
				del wordsList[i]
				continue
			i += 1
	return wordsList


def digitalFilter(wordsList):
	i = 0
	while i < len(wordsList):
		if wordsList[i].isdigit():
			del wordsList[i]
			continue
		i += 1
	return wordsList


def oneWordFilter(texts):
	i = 0
	while i < len(texts):
		if 1 >= len(texts[i]):
			del texts[i]
			continue
		i += 1
	return texts


def testTasker(task_ID, para):
	task = taskDB.getTaskInfo(task_ID)
	task.task_status = parse.TASK_STATUS.startTasK
	task.data = "tasker start\n"
	taskDB.changeTaskInfo(task)
	import time
	time.sleep(1)
	taskerLog(task_ID, "process tasker")
	task.task_status = parse.TASK_STATUS.process
	task.save()
	for i in xrange(10):
		time.sleep(4)
		taskerLog(task_ID, str(i))
	taskerToComplete(task_ID)
	taskerLog(task_ID, "tasker over")
