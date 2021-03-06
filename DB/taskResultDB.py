# coding:utf-8
from peewee import Model, MySQLDatabase
from peewee import CharField, IntegerField, CompositeKey
from db_base import MySQLDatabaseRetry
import db_config


db_config = db_config.getTaskResult()
db = MySQLDatabaseRetry(**db_config)


class resultType:
	FRQ_SUM = 1
	FRQ_COUNT = 2
	TFIDF = 3
	TFIDF_2 = 4
	TITLE = 5
	ABSTRACT = 6
	CLAIM = 7


class resultKey:
	task_ID = "task_ID"
	word = "word"
	word_weight = "word_weight"
	weight_type = "weight_type"


class TaskResult(Model):
	task_ID = IntegerField()
	word = CharField()
	word_weight = IntegerField()
	weight_type = IntegerField()

	class Meta:
		db_table = "taskResult"
		database = db
		primary_key = CompositeKey(
			resultKey.task_ID, resultKey.word, resultKey.weight_type)


# 根据两个参数获取result,如果第二个参数不给
# 则返回所有type的result,入股type==0,则返回小于零
# 也就是单篇文章的result
def getResult(task_ID, weight_type=None):
	if weight_type is None:
		return TaskResult.select().where(TaskResult.task_ID == task_ID)
	if weight_type == 0:
		return TaskResult.select().where(
			TaskResult.task_ID == task_ID, TaskResult.weight_type < 0)
	return TaskResult.select().where(
		TaskResult.task_ID == task_ID, TaskResult.weight_type == weight_type)


# 将可迭代的TaskResult输出成dict
# 以weight_type为key,值是以word为key的dict,值为weight
def tranDataToDict(datas):
	result_dict = {}
	for i in datas:
		if i.weight_type not in result_dict:
			result_dict[i.weight_type] = {}
		result_dict[i.weight_type][i.word] = i.word_weight
	return result_dict


# 方法同上,但是生成的二级结构是list,
# 其中[0]是word[1]是weight,然后[0] , [1] 又分别使是一个List
# 这样做是为了减小内存占用
# 结构仍然是weight_type的dict
def tranDataToList(datas):
	result_dict = {}
	for i in datas:
		if i.weight_type not in result_dict:
			result_dict[i.weight_type] = []
		result_dict[i.weight_type].append([i.word, i.word_weight])
	return result_dict


# 列表,内容是字典
def addResult(results):
	if 0 == len(results):
		return
	with db.atomic():
		for i in xrange(0, len(results), 3000):
			TaskResult.insert_many(results[i:i + 3000]).execute()


def deleteResult(task_ID):
	try:
		query = TaskResult.delete().where(TaskResult.task_ID == task_ID)
		return query.execute()
	except:
		return None
