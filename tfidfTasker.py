# coding:utf-8
# 此模块用于TFIDF 关键词提取task执行
import math
from DB import tfidfDB
from DB import rawdataDB
from tfidf import tools
import tasker
from tools import parse_IDs


# 参数:词语列表
def getIDF(wordsList):
	data = tfidfDB.getFromWords(wordsList)
	data = tfidfDB.tranDataToDict(data)
	count = rawdataDB.zl_project.select().count()
	idf = {}
	for word in data:
		idf[word] = math.log10(float(count) / (data[word][tools.tfidf_key.frq] + 1))
	return idf


# 参数:包括词频的字典
# 此处不使用,直接用词频
def getTF(wordsDict):
	tf = {}
	for word in wordsDict:
		tf[word] = wordsDict[word][tools.tfidf_key.sum_frq]
	return tf


def getIDF_2(wordsList, sub_sum):
	data = tfidfDB.getFromWords(wordsList)
	data = tfidfDB.tranDataToDict(data)
	count = rawdataDB.zl_project.select().count()
	idf = {}
	for word in data:
		idf[word] = float(count) / (data[word][tools.tfidf_key.sum_frq])
	return idf


def getTFIDF(tf, idf):
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
	step = 100

	zl_IDs = parse_IDs.getData(parse_IDs.generateValues(SQL))
	error = zl_IDs["message"]
	print(error)
	zl_IDs = parse_IDs.getIDs(zl_IDs)
	print("get IDs over")
	print(zl_IDs)

	wordsDict = {}
	iterator = len(zl_IDs) / step

	if len(zl_IDs) % step != 0:
		iterator += 1

	print len(zl_IDs)
	for i in xrange(iterator):
		print("." + str(i) + " " + str(iterator))
		if (i + 1) * step >= len(zl_IDs):
			data = rawdataDB.getFromIDs(zl_IDs[i * step:])
		else:
			data = rawdataDB.getFromIDs(
				zl_IDs[i * step:(i + 1) * step - 1])
		print("get Data over")
		text = []
		for d in data:
			if d.alltext is not None and 0 != len(d.alltext):
				text.append(d.alltext)
		print("pre process over")
		for t in text:
			t = tasker.removeNULL(t)
			words = tasker.getWordList(t)
			words = tasker.oneWordFilter(words)
			if 0 == len(words):
				continue
			wordsDict = tools.addWordDict(words, wordsDict)
		print("process over")
	# print(wordsDict)
	wordsList = wordsDict.keys()
	idf = getIDF(wordsList)
	idf_2 = getIDF(wordsList)
	tf = getTF(wordsDict)
	tfidf = getTFIDF(tf, idf)
	tfidf_2 = getTFIDF(tf, idf_2)
	sorted_tfidf = sorted(tfidf, key=lambda data: tfidf[data], reverse=True)
	sorted_frq = sorted(
		wordsDict, key=lambda data: wordsDict[data]["TFIDF_sum_frq"], reverse=True)
	sorted_sum = sorted(
		wordsDict, key=lambda data: wordsDict[data]["TFIDF_frq"], reverse=True)
	sorted_tfidf_2 = sorted(tfidf_2, key=lambda data: tfidf_2[data], reverse=True)

	with open("../result/tfidf.txt", "w") as f:
		for i in sorted_tfidf:  # [:500]:
			f.write(i)
			f.write("		")
			f.write(str(tfidf[i]))
			f.write("\n")
	with open("../result/frq.txt", "w") as f:
		for i in sorted_frq:  # [:500]:
			f.write(i)
			f.write("		")
			f.write(str(wordsDict[i]["TFIDF_sum_frq"]))
			f.write("\n")
	with open("../result/sum.txt", 'w') as f:
		for i in sorted_sum:  # [:500]:
			f.write(i)
			f.write("		")
			f.write(str(wordsDict[i]["TFIDF_frq"]))
			f.write("\n")
	with open("../result/tfidf_2.txt", "w") as f:
		for i in sorted_tfidf_2:  # [:500]:
			f.write(i)
			f.write("		")
			f.write(str(tfidf[i]))
			f.write("\n")


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
