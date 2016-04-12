#coding:utf-8 
from peewee import *
from datetime import datetime , date , tzinfo , timedelta 
db_config = {
     'host': 'localhost',
     'port': 3306,
     'user': 'root',
     'password': 'qazwsxedc',
     'database': 'cnlp'
 }
db = MySQLDatabase(**db_config)
class TaskInfo(Model):
	task_ID		=	PrimaryKeyField()
	task_status	=	CharField()	
	task_date	=	DateTimeField()
	task_etc	=	CharField() 
	class Meta:
		db_table = 'taskInfo'
		database = db

def getTaskInfo():
	return TaskInfo.select()
def addTaskInfo(data):
	task =TaskInfo()
	task.task_status = "a"
	task.task_date = datetime.now()
	task.task_etc = data
	task.save()
	return task.task_ID
def dropTaskInfo(ID):
	try:
		task = TaskInfo.get(TaskInfo.task_ID == ID)
		return task.delete_instance()
	except DoesNotExist:
		return -2
def changeTaskInfo(data):
	data.save()
def getTaskInfo(ID):
	return TaskInfo.get(TaskInfo.task_ID == ID)
