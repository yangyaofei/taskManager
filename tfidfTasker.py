# coding:utf-8
# 此模块用于TFIDF 关键词提取task执行
import math
from DB import tfidfDB
from DB import rawdataDB
from DB import taskResultDB
from tools.logger import logger
from tfidf import tools
import tasker
import sys
import gc
from tools import parse_IDs


# words是一个字典,值为权重
def save_to_result(task_id, words, result_type):
	save_list = []
	for i in words:
		item = {
			taskResultDB.resultKey.task_ID: task_id,
			taskResultDB.resultKey.weight_type: result_type,
			taskResultDB.resultKey.word: i,
			taskResultDB.resultKey.word_weight: words[i]
		}
		save_list.append(item)
	taskResultDB.addResult(save_list)


# tfidf格式字典保存,两个都保存
# 注意使tfidf格式的字典的保存,不是tfidf算法的数据的保存
def save_tfidf_to_result(task_id, words_dict):
	frq_list = []
	frq_sum_list = []
	for i in words_dict:
		item_frq = {
			taskResultDB.resultKey.task_ID: task_id,
			taskResultDB.resultKey.weight_type: taskResultDB.resultType.FRQ_COUNT,
			taskResultDB.resultKey.word: i,
			taskResultDB.resultKey.word_weight:
				words_dict[i][tfidfDB.TFIDF_key.frq]
		}
		frq_list.append(item_frq)
	taskResultDB.addResult(frq_list)
	# 用于GC
	frq_list = []
	gc.collect()
	for i in words_dict:
		item_frq_sum = {
			taskResultDB.resultKey.task_ID: task_id,
			taskResultDB.resultKey.weight_type: taskResultDB.resultType.FRQ_SUM,
			taskResultDB.resultKey.word: i,
			taskResultDB.resultKey.word_weight:
				words_dict[i][tfidfDB.TFIDF_key.sum_frq]
		}
		frq_sum_list.append(item_frq_sum)
	taskResultDB.addResult(frq_sum_list)


# 参数:词语列表
def get_idf(words_list):
	data = tfidfDB.getFromWords(words_list)
	data = tfidfDB.tranDataToDict(data)
	count = rawdataDB.zl_project.select().count()
	idf = {}
	for word in data:
		idf[word] = math.log10(float(count) / (data[word][tools.tfidf_key.frq] + 1))
	return idf


# 参数:包括词频的字典
# 此处不使用,直接用词频
def get_tf(words_dict):
	tf = {}
	for word in words_dict:
		tf[word] = words_dict[word][tfidfDB.TFIDF_key.sum_frq]
	return tf


def get_idf_2(words_list):
	data = tfidfDB.getFromWords(words_list)
	data = tfidfDB.tranDataToDict(data)
	count = rawdataDB.zl_project.select().count()
	idf = {}
	for word in data:
		idf[word] = float(count) / (data[word][tfidfDB.TFIDF_key.sum_frq])
	return idf


def get_tfidf_2(tf, idf_2):
	count = rawdataDB.zl_project.select().count()
	tfidf = {}
	for i in tf:
		if i not in idf_2:
			tfidf[i] = float(count)
		else:
			tfidf[i] = tf[i] * idf_2[i]
	return tfidf


def get_tfidf(tf, idf):
	count = rawdataDB.zl_project.select().count()
	tfidf = {}
	for i in tf:
		if i not in idf:
			tfidf[i] = tf[i] * math.log10(float(count))
		else:
			tfidf[i] = tf[i] * idf[i]
	return tfidf

#####################################
# start tasker


def startTasker(task_ID, SQL):
	tasker.taskerToStart(task_ID)
	tasker.initCutter()
	tasker.taskerLog(task_ID, "init Cutter over")
	step = 100
	length = 0
	iterator = 0
	progress = 1
	for item in parse_IDs.get_raw(SQL,size=step):
		if len(item[0]) == 0:
			logger.error("get IDs fail")
			tasker.taskerToError(task_ID, item[1])
			sys.exit(-1)

		if progress == 1:
			logger.info("get IDs over")
			tasker.taskerLog(task_ID, "get IDs over")
			tasker.TaskerToProcess(task_ID)

		words_dict = {}
		words_dict_title = {}  # 标题
		words_dict_abstract = {}  # 摘要
		words_dict_claim = {}  # 权利要求

		# calculate step
		# 用于生成进度
		length = item[1]
		iterator = length / step
		if length % step != 0:
			iterator += 1
		# 进度显示
		msg = "进度: " + str(progress) + "/ 共" + str(iterator)
		tasker.taskerLog(task_ID, msg)
		progress += 1

		text = []
		text_title = []  # 标题
		text_abstract = []  # 摘要
		text_claim = []  # 权利要求

		for d in item[0]:
			d = d["_source"]
			if d["alltext"] is not None and 0 != len(d["alltext"]):
				text.append(d["alltext"])
			if d["abstractcontent"] is not None and 0 != len(d["abstractcontent"]):
				text_abstract.append(d["abstractcontent"])
			if d["name"] is not None and 0 != len(d["name"]):
				text_title.append(d["name"])
			if d["right_require"] is not None and 0 != len(d["right_require"]):
				text_claim.append(d["right_require"])
		for t in text:
			t = tasker.removeNULL(t)
			words = tasker.getWordList(t)
			words = tasker.oneWordFilter(words)
			if 0 == len(words):
				continue
			words_dict = tools.addWordDict(words, words_dict)
		for t in text_title:
			t = tasker.removeNULL(t)
			words = tasker.getWordList(t)
			words = tasker.oneWordFilter(words)
			if 0 == len(words):
				continue
			words_dict_title = tools.addWordDict(words, words_dict_title)
		for t in text_claim:
			t = tasker.removeNULL(t)
			words = tasker.getWordList(t)
			words = tasker.oneWordFilter(words)
			if 0 == len(words):
				continue
			words_dict_claim = tools.addWordDict(words, words_dict_claim)
		for t in text_abstract:
			t = tasker.removeNULL(t)
			words = tasker.getWordList(t)
			words = tasker.oneWordFilter(words)
			if 0 == len(words):
				continue
			words_dict_abstract = tools.addWordDict(words, words_dict_abstract)
		gc.collect()
	tasker.taskerLog(task_ID, "process step-1 over")
	tasker.taskerLog(task_ID, "save result to database")
	# ++++++++++++++++
	words_dict_ = {}
	words_dict_ = tools.mergeWordDict(words_dict_, words_dict_claim)[0]
	words_dict_ = tools.mergeWordDict(words_dict_, words_dict_title)[0]
	words_dict_ = tools.mergeWordDict(words_dict_, words_dict_abstract)[0]

	words_list = words_dict.keys()
	tf = get_tf(words_dict)
	idf = get_idf(words_list)
	tfidf = get_tfidf(tf, idf)
	save_to_result(task_ID, tfidf, taskResultDB.resultType.TFIDF)
	tasker.taskerLog(task_ID, "save tfidf over")

	# GC
	words_dict_claim = None
	words_dict_title = None
	words_dict_abstract = None
	idf = None
	tfidf = None
	gc.collect()

	idf_2 = get_idf_2(words_list)
	tfidf_2 = get_tfidf_2(tf, idf_2)
	save_to_result(task_ID, tfidf_2, taskResultDB.resultType.TFIDF_2)
	tasker.taskerLog(task_ID, "save tfidf_2 over")

	idf_2 = None
	tfidf_2 = None
	gc.collect()

	save_tfidf_to_result(task_ID, words_dict)
	tasker.taskerLog(task_ID, "save frq over")
	# ++++++++++++++++++++++++++++++++++++++++++++++++++
	frq_list = []
	frq_sum_list = []
	for i in words_dict_:
		item_frq = {
			taskResultDB.resultKey.task_ID: task_ID,
			taskResultDB.resultKey.weight_type: taskResultDB.resultType.ABSTRACT,
			taskResultDB.resultKey.word: i,
			taskResultDB.resultKey.word_weight:
				words_dict_[i][tfidfDB.TFIDF_key.frq]
		}
		frq_list.append(item_frq)
	taskResultDB.addResult(frq_list)
	frq_list = []
	gc.collect()
	for i in words_dict_:
		item_frq_sum = {
			taskResultDB.resultKey.task_ID: task_ID,
			taskResultDB.resultKey.weight_type: taskResultDB.resultType.CLAIM,
			taskResultDB.resultKey.word: i,
			taskResultDB.resultKey.word_weight:
				words_dict_[i][tfidfDB.TFIDF_key.sum_frq]
		}
		frq_sum_list.append(item_frq_sum)
	taskResultDB.addResult(frq_sum_list)

	tasker.taskerLog(task_ID, "save frq_other over")
	# ++++++++++++++++++++++++++++++++++++++++++++++++++

	tasker.taskerLog(task_ID, "process step-2 over")
	tasker.taskerLog(task_ID, "process complete")
	tasker.taskerToComplete(task_ID)
	gc.collect()

	# sorted_tfidf = sorted(tfidf, key=lambda data: tfidf[data], reverse=True)
	# sorted_frq = sorted(
	# 	words_dict, key=lambda data: words_dict[data]["TFIDF_sum_frq"], reverse=True)
	# sorted_sum = sorted(
	# 	words_dict, key=lambda data: words_dict[data]["TFIDF_frq"], reverse=True)
	# sorted_tfidf_2 =
	# 	sorted(tfidf_2, key=lambda data: tfidf_2[data], reverse=True)

	'''
	queue = multiprocessing.Queue(MAX_QUEUE)
	p = Producer(queue,zl_IDs,1000)
	logger.info(taskID_for_log+"start a process to get data")
	p.start()
	data = []
	# Get data use queue and Process it
	while True:
		logger.info(taskID_for_log+"in while to get data from queue")

dirt = queue.get()
		if dirt["flag"] == "e":
			logger.info(taskID_for_log+"get a 'e'flag to end loop")
			break
		logger.debug(taskID_for_log+"get data and print")
		for d in dirt["data"]:
			print(d.id),
			#print(d.apply_num),
			print(" "),
		print("")
	p.join()

#'''
# 生产者 用来从database获取数据,并传输给主进程进行处理
# 传输数据是一个字典,flag和data,flag为d的时候证明传输的
# 是数据,当flag的值为e的时候表示数据已经传输完毕
'''class Producer(multiprocessing.Process):
	def __init__(self,queue,zl_IDs,step):
		multiprocessing.Process.__init__(self)
		self.queue = queue
		self.zl_IDs = zl_IDs
		self.step = step
	def run(self):
		from logger import logger
		iterator = 0
		IDs = self.zl_IDs
		queue = self.queue
		step = self.step
		while iterator < len(IDs):
			data = []
			dirt = {}
			if iterator > (len(IDs)-step):
				print(iterator)
				logger.debug("Producer is getting data"+str(iteratot))
				data = rawdataDB.getFromIDs(IDs[iterator:])
			else:
				logger.debug(
					"Producer is getting data"+str(iterator)+"-"+str(iterator+step))
				data = rawdataDB.getFromIDs(IDs[iterator:iterator+step])
			dirt["flag"] = "d"
			dirt["data"] = data
			queue.put(dirt)
			iterator+=step
		logger.debug("Producer get data complete")
		dirte = {}
		logging.debug("Producer put a 'e'flage to end")
		dirte["flag"] = "e"
		queue.put(dirte)
		queue.close()
'''
