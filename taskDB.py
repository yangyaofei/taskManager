# coding:utf-8
from peewee import Model, MySQLDatabase
from peewee import PrimaryKeyField, CharField, DateTimeField, IntegerField
from peewee import DoesNotExist
import datetime
db_config = {
	'host': 'localhost',
	'port': 3306,
	'user': 'root',
	'password': 'qazwsxedc',
	'database': 'cnlp'
}
db = MySQLDatabase(**db_config)


class TaskInfo(Model):
	task_ID = PrimaryKeyField()
	task_name = CharField()
	task_create_time = DateTimeField()
	task_finish_time = DateTimeField()
	task_type = IntegerField()
	task_status = CharField()
	task_data = CharField()
	task_para = CharField()

	class Meta:
		db_table = 'taskInfo'
		database = db


def getAllTaskInfo():
	return TaskInfo.select()


def addTaskInfo(task_name, task_type, task_para):
	task = TaskInfo()
	task.task_name = task_name
	task.task_create_time = datetime.now()
	task.task_type = task_type
	task.task_status = "a"
	task.task_para = task_para
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
	try:
		return TaskInfo.get(TaskInfo.task_ID == ID)
	except DoesNotExist:
		return None
