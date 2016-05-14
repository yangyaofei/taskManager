# coding:utf-8
# 此模块用于TFIDF 关键词提取task执行
import rawdataDB
import rawdataGetter as getter
import taskDB
import jieba
import jieba.posseg as pseg
import tfidfDB
import math

#####################################
# 后期将这部分写入一个文件
#####################################


def taskerStatus(ID, status, message):
	data = taskDB.getTaskInfo(ID)
	data.task_status = status
	data.task_etc = message
	taskDB.changeTask(data)


def taskerToError(ID, message):
	# logger.info("taskerToError")
	# 转到出错状态 并保存出错原因
	taskerStatus(ID, 'e', message)


def taskerToComplete(ID):
	# loggrt.g("taskerToComplete")
	taskerStatus(ID, 'c', '')

#####################################
# END
############################################################
# 	文本处理部分


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


# 去掉长度为1的词
def oneWordFilter(texts):
	i = 0
	while i < len(texts):
		if 1 >= len(texts[i]):
			del texts[i]
			continue
		i += 1
	return texts


# 从切词结果得到词组成的list
def getWordList(words):
	l = []
	for i in words:
		if i.flag.find("n") != -1:
			l.append(i.word)
	return l


def mergeWordDict(d1, d2):
	# d1 数据库数据 d2 准备添加数据
	# 返回值为两个,第一个是两部分交集部分的合并(需要update)
	# 			   第二个是两个的异或部分(需要insert)
	s1 = set(d1.keys())
	s2 = set(d2.keys())
	if len(s1 - s2) != 0:
		# 理论上d1应该为d2子集,所以如果补集有数据则说明出错了!
		# printandlog("merge error")
		return
	s3 = s2 - s1
	# d3 = dict((k, d[k]) for k in list(s3) if k in d2)
	d3 = {}
	for i in set(s3):
		d3[i] = d2[i]
	for i in d1:
		d1[i]["TFIDF_frq"] += d2[i]["TFIDF_frq"]
		d1[i]["TFIDF_sum_frq"] += d2[i]["TFIDF_sum_frq"]
	return d1, d3


# 列表 如果第二个参数值,则加入到字典中,并返回
def addWordDict(texts, wordsDict=None):
	newWordDict = makeWordDict(texts)
	if wordsDict is not None:
		for i in newWordDict:
			if i in wordsDict:
				wordsDict[i]["TFIDF_sum_frq"] += newWordDict[i]["TFIDF_sum_frq"]
				wordsDict[i]["TFIDF_frq"] += 1
			else:
				wordsDict[i] = {}
				wordsDict[i]["TFIDF_sum_frq"] = newWordDict[i]["TFIDF_sum_frq"]
				wordsDict[i]["TFIDF_frq"] = 1
				wordsDict[i]["TFIDF_word"] = i
		return wordsDict
	else:
		return newWordDict


# 仅将其构造成字典,以便统计
def makeWordDict(text):
	wordsDict = {}
	for i in text:
		# 因为数据库中有50长度限制,而词长度不会超过50
		# 所以超过的,直接丢弃
		if 50 <= len(i):
			continue
		if i in wordsDict:
			wordsDict[i]["TFIDF_sum_frq"] += 1
		else:
			wordsDict[i] = {}
			wordsDict[i]["TFIDF_sum_frq"] = 1
			wordsDict[i]["TFIDF_frq"] = 1
			wordsDict[i]["TFIDF_word"] = i
	return wordsDict


def cut(texts):
	texts = pseg.cut(texts)
	return texts
#
#
############################################################
#


# 参数:词语列表
def getIDF(wordsList):
	data = tfidfDB.getFromWords(wordsList)
	data = tfidfDB.tranDataToDict(data)
	count = rawdataDB.zl_project.select().count()
	idf = {}
	for word in data:
		idf[data[word]["TFIDF_word"]] =\
			math.log10(float(count) / (data[word]["TFIDF_frq"] + 1))
	return idf


# 参数:包括词频的字典
# 此处有两种计算方法,一个是用所有词的次数为分母
# 一个是用最好词的词频作为分母,最终效果应该一样
# 此处不使用,直接用词频
def getTF(wordsDict):
	tf = {}
	for word in wordsDict:
		tf[word] = wordsDict[word]["TFIDF_sum_frq"]
	return tf


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
	jieba.load_userdict('dict.txt')
	step = 10
	zl_IDs = getter.getData(getter.generateValues(SQL))
	error = zl_IDs["message"]
	print(error)
	zl_IDs = getter.getIDs(zl_IDs)
	print("get IDs over")
	print(zl_IDs)
	wordsDict = {}
	iterator = len(zl_IDs) / step
	if len(zl_IDs) % step != 0:
		iterator += 1
	print len(zl_IDs)
	# for test
	# iterator = i
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
			t = removeNULL(t)
			words = pseg.cut(t)
			words = getWordList(words)
			words = oneWordFilter(words)
			if 0 == len(words):
				continue
			# words = puncFilter(words,PUNC)
			# words = digitalFilter(words)
			wordsDict = addWordDict(words, wordsDict)
		print("process over")
	# print(wordsDict)
	wordsList = wordsDict.keys()
	idf = getIDF(wordsList)
	tf = getTF(wordsDict)
	tfidf = getTFIDF(tf, idf)
	sorted_tfidf = sorted(tfidf, key=lambda data: tfidf[data], reverse=True)
	sorted_frq = sorted(
		wordsDict, key=lambda data: wordsDict[data]["TFIDF_sum_frq"], reverse=True)
	sorted_sum = sorted(
		wordsDict, key=lambda data: wordsDict[data]["TFIDF_frq"], reverse=True)

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
