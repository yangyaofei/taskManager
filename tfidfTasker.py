#coding:utf-8
#此模块用于TFIDF 关键词提取task执行
import time
import rawdataDB
import multiprocessing
import rawdataGetter as getter
import taskDB
import jieba
import jieba.posseg as pseg

#####################################
# 后期将这部分写入一个文件
# 
#####################################
def taskerStatus(ID,status,message):
	data = taskDB.getTaskInfo(ID)
	data.task_status = status
	data.task_etc = message
	taskDB.changeTask(data)
def taskerToError(ID,message):
	#logger.info("taskerToError")
	# 转到出错状态 并保存出错原因
	taskerStatus(ID,'e',message)
def taskerToComplete(ID):
	#loggrt.g("taskerToComplete")
	taskerStatus(ID,'c','')
#####################################
#END
############################################################
#	文本处理部分
#
def removeNULL(data):
# 去掉没用的空格 Tab \r <br>
	data = data.replace("\r","")
	data = data.replace("\n","")
	data = data.replace("\t","")
	data = data.replace("<br >","\n")
	data = data.replace("<br />","\n")
	data = data.replace(" ","")
	return data

# 下面三个函数是用来去掉没用的词的函数 参数都是词组成的list
PUNC = u'''，。《》？“”‘’：；！、,.<>?"':;!(）()'''
def puncFilter(wordsList,punc):
# 出现标点就去掉
	for p in PUNC:
		i = 0
		while i < len(wordsList):
			if wordsList[i].find(p) != -1:
				del wordsList[i]
				continue
			i+=1
	return wordsList
def digitalFilter(wordsList):
	i = 0
	while i < len(wordsList):
		if wordsList[i].isdigit():
			del wordsList[i]
			continue
		i+=1
	return wordsList
def oneWordFilter(texts): 
# 去掉长度为1的词
	i = 0
	while i < len(texts):
		if 1 >= len(texts[i]):
			del	texts[i]
			continue
		i+=1
	return texts
# 从切词结果得到词组成的list
def getWordList(words):
	l = []
	for i in words:
		l.append(i.word)
	return l

def mergeWordDict(d1,d2):
	# d1 数据库数据 d2 准备添加数据 
	# 返回值为两个,第一个是两部分交集部分的合并(需要update) 
	#			   第二个是两个的异或部分(需要insert)
	s1 = set(d1.keys())
	s2 = set(d2.keys())
	if len(s1 - s2) != 0:
		# 理论上d1应该为d2子集,所以如果补集有数据则说明出错了!
		#printandlog("merge error")
		return
	s3 = s2 - s1
	#d3 = dict((k, d[k]) for k in list(s3) if k in d2)
	d3 = {}
	for i in set(s3):
		d3[i] = d2[i]
	for i in d1:
		d1[i]["TFIDF_frq"] += d2[i]["TFIDF_frq"]
		d1[i]["TFIDF_sum_frq"] += d2[i]["TFIDF_sum_frq"]
	return d1,d3
def addWordDict(texts,wordsDict=None):
# 列表 如果第二个参数有值,则加入到字典中,并返回
	newWordDict = makeWordDict(texts)
	if None != wordsDict:
		for i in newWordDict:
			if(wordsDict.has_key(i)):
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

def makeWordDict(text):# 仅将其构造成字典,以便统计
	wordsDict = {}
	for i in text:
		# 因为数据库中有50长度限制,而词长度不会超过50
		# 所以超过的,直接丢弃
		if 50 <= len(i):
			continue
		if(wordsDict.has_key(i)):
			wordsDict[i]["TFIDF_sum_frq"] += 1
		else:
			wordsDict[i] ={}
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
import tfidfDB
import math
def getIDF(wordsList):# 词语列表
	data = tfidfDB.getFromWords(wordsList)
	data = tfidfDB.tranDataToDict(data)
	count = rawdataDB.zl_project.select().count()
	idf = {}
	for word in data:
		idf[word["TFIDF_word"]] = math.log10(float(count)/(word["TFIDF_frq"]+1))
	return idf
def getTF(wordsDict):#包括词频的字典
# 此处有两种计算方法,一个是用所有词的次数为分母
# 一个是用最好词的词频作为分母,最终效果应该一样
# 此处不使用,直接用词频
	tf = {}
	for word in wordsDict:
		tf[word] = wordsDict[word]["TFIDF_sum_frq"]
	return tf
#
def getTFIDF(tf,idf):
	tfidf = {}
	for i in tf :
		tfidf[i] = tf[i]*idf[i]
	return tfidf
#####################################
# start tasker
def startTasker(task_ID,SQL):
	zl_IDs = getter.getData(getter.generateValues(SQL))
	error = zl_IDs["message"]
	zl_IDs = getter.getIDs(zl_IDs)
	print("get IDs over")
	print(zl_IDs)
	wordsDict = {}	
	for ID in zl_IDs:
		print("."),
		data = rawdataDB.getFromID(ID)
		data = removeNULL(data.alltext)
		data = pseg.cut(data)
		words = getWordList(data)
		words = oneWordFilter(words)
		words = puncFilter(words,PUNC)
		words = digitalFilter(words)
		wordsDict = addWordDict(words,wordsDict)
	#print(wordsDict)
	wordsList = wordsDict.keys()
	idf = getIDF(wordsList)
	tf = getTF(wordsDict)
	tfidf = getTFIDF(tf,idf)
	sorted_tfidf = sorted(tfidf, key=lambda data: data[1], reverse = True)
	for i in sorted_tfidf[:100]:
		print sorted_tfidf[i][0],
		print("		")
		print sorted_tfidf[i][1]
		
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
class Producer(multiprocessing.Process):
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
				logger.debug("Producer is getting data"+str(iterator)+"-"+str(iterator+step))
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
