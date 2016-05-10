#coding:utf-8
import multiprocessing
import tasker
'''def addTask(data):
	#添加数据库  返回 状态为a
	return 
'''
taskerList = []
def handleTasker()
	for t in taskerList:
	# 每次处理进程列表中已经终止的那些
	# 前期先不管状态如何,后期可以根据退出的状态进行不同的操作
	# TODO
		if not t.is_alive:
			t.join()
			taskerList.remove(t)
def startTask():
	#检查状态是否可以start
	#修改状态为s fork() execl() 传值ID等
	p = multiprocessing.Process(target=tasker.startTasker,args=(task_ID))
	taskerList.append(p)
	return 
def stopTask(ID):
	#根据PID终止进程,修改数据库任务状态 删除相关结果 返回
	return
def editTask(ID):
	#判断任务状态 可以修改后 修改数据库 返回
	return
def restartTask():
	#判断任务状态 可以时 kill 删除相关数据库结果 任务状态为a
	return
def pauseTask():
	#最后实现
	return
def getResult():
	#根据数据库中的状态,返回结果
	return
def deleteResult():
	return
def listTask():
	#查找数据库 返回
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

