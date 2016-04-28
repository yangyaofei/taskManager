#!/usr/bin/python
#coding:utf-8
import sys
import tasker
import tfidfDB
import multiprocessing
import rawdataDB
import jieba
import jieba.posseg as pseg
import logging
import multiprocessing
import traceback
import os
import time
import signal
import getopt
import pickle
import logger
reload(sys) 
sys.setdefaultencoding('utf8')  
############################################################
##
##	此脚本用于将整个文本库进行遍历分词,统计词频用于
##	TFIDF关键词的IDF(逆向文件频率)部分统计,此脚本可
##	以在脚本退出时保存统计进度,以便下次继续.
##		注:此处是除SIGKILL信号之外的程序终结,
##		对SIGKILL也有一定的措施保护进度的保存
##		但是不能保证数据一定有效,ps:断电什么
##		的肯定不行了,但是这个和SIGKILL没啥区别
##	此脚本利用multiprocessing进行多进程并行计算,这样
##	会增加文本处理的效率,具体用法等等,请看下面源码,用
##	法在最后的注释中有详细的解释,不明白请看代码
##
############################################################

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
		printandlog("merge error")
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
#
#
############################################################


def printDirc(text_dirc):
	for t in text_dirc:
		print t,
		print text_dirc[t],
def prints(texts):
	for t in texts:
		print t,
		print("/"),
def printWordDict(d):
	for i in d:
		print i,
		print d[i]["TFIDF_sum_frq"],
		print d[i]["TFIDF_frq"],
		print d[i]["TFIDF_word"]
def printError(d):
	for i in d:
		if 50 <= len(i):
			print(i)
		if 1 >= len(i):
			print(i)
		if i.isdigit():
			print(i)
		for p in PUNC:
			if i.find(p) != -1:
				print(i)
def log(txt):
	with open("log.log","a") as f:
		f.write(txt)
def printandlog(t):
	print(t)
	with open("log.main.log","a") as f:
		f.write(t+"\n")

											#####
											#####
#################################################
#################################################
def cut(texts):
	texts = pseg.cut(texts)
	return texts


#################################################		
# 下列函数用于处理数据时的进度保存,读取,识别和更新

# index 代表当前已完成成序列的最后一个ID
# 如: 3,4,5,7,8,10 则index=5
# indexs 代表index后已经完成的所有ID的集合
# 上述数据中 indexs = (7,8,10)

index = "index.save"
indexs = "index.s.save"
# 从文件中获取ID
def getIDFromFile():
	try:
		storeID = -1
		storeIDs = set()
		if os.path.isfile(index):
			with open(index) as f:
				storeID = f.read()
				if storeID.isdigit():
					storeID = int(storeID)
		if os.path.isfile(indexs):
			with open(indexs,"rb") as f:
				storeIDs = pickle.load(f)
		return storeID,storeIDs
	except:
		return -1,set()
# 将ID,IDs保存到文件中
def setIDToFile(ID,IDs):
	with open(index,"w") as f:
		f.write(str(ID))
	with open(indexs,"wb") as f:
		pickle.dump(IDs, f)
		#f.write(str(IDs))

# 整理数据,去掉已经成序列的IDs,并迭代ID
def manageIndex(index,indexs):
	indexs = set(indexs)
	while True:
		if  index+DATA_SIZE in indexs:
			indexs.remove(index+DATA_SIZE)
			index+=DATA_SIZE
		else:
			break
	return index,indexs
# 根据保存的数据得到没有处理的ID集合放入IDs中
# 并更新ID到最前面
def getIDsFromIndex(index,indexs):
	if startID > index:
		return -1,set()
	IDs = set()
	indexs = set(indexs)
	while True:
		index+=DATA_SIZE
		if 0 == len(indexs):
			break
		if index not in indexs:
			IDs.add(index)
			#IDs.append(index)
		else:
			indexs.remove(index)
	return index,IDs
#
##########################################################
##########################################################
##														##
##			 PROCESSer 类 三个							##
##														##
##########################################################
##########################################################
#
# 生产者,用于从数据库获取数据给消费者
class Producer(multiprocessing.Process):
	def __init__(self,queue,size):
		multiprocessing.Process.__init__(self)
		self.queue = queue
		self.size = size 
		self.name = "Producer"
		# 一次性传输给消费者的大小 
	def run(self):
		# 初始化ID为最开始的ID
		ID = startID
		# 信号量响应
		signal.signal(signal.SIGTERM,self.exit)
		# 获取logger
		self.logger = logger.getLogger(logging.INFO,"tfidf.producer.log")
		# 获取整个表大小
		DATA_MAXSIZE = rawdataDB.zl_project.select().count()
		# 获取保存的没有完成的任务id和ID进度
		tID,tIDs = getIDFromFile()
		#self.logger.info("getID and IDs:"+str(tID)+"-"+str(tIDs))
		sID,sIDs = getIDsFromIndex(tID,tIDs)
		self.logger.info("getID and IDs:"+str(sID)+"-"+str(sIDs))
		if sID == -1:
			self.logger.info("新任务,从头执行")
		else:
			if sID <= startID:
				self.logger.info("错误的sID,从头开始")
			else:
				self.logger.info("获取任务进度成功,在"+str(sID)+"处开始")
				ID = sID
				for i in sIDs:
					self.logger.info("处理一些未完成的任务ID:"+str(i))
					texts = self.getTextsFromID(i)
					queue.put(texts)
		try:
			#m = "Producer process: "
			while True:
				if DATA_MAXSIZE < ID:
					break
				#self.logger.info("getting texts from ID:"+str(ID))
				texts = self.getTextsFromID(ID)
				#if 0 == len(text):
				#	continue
				queue.put(texts)
				self.logger.info(str(ID)+"-"+str(ID+self.size-1)+"/"+str(DATA_MAXSIZE))
				ID+=self.size
		except SystemExit:
			self.logger.info("process exit with sys.exit()")
			exit(0)
		except:
			error = traceback.format_exc()
			self.logger.error("Producer error")
			self.logger.error(error)
			exit(-1)

	def getTextsFromID(self,ID):
		size = self.size
		texts = []
		texts.append(ID)
		IDs = range(ID,ID+size-1)
		# sys.stdout.flush()
		datas = rawdataDB.getFromIDs(IDs)
		for i in datas:
			texts.append(i.alltext)
		return texts
	def exit(self,arg1,arg2):
		self.logger.info("Producer exit")
		sys.exit(0)




##########################################################
#
# 消费者,和主进程用queue通信.消费者用于分词,并将数据传给
# Consumer_save.
# 打包数据与得到的数据类似,第一个element为ID信息,第二个需
# 要update部分,第三个需要insert部分.


class Consumer(multiprocessing.Process):
	def __init__(self,queue,save_queue,processNo):
		multiprocessing.Process.__init__(self)
		self.queue = queue
		self.save_queue = save_queue
		self.processNo = processNo
		self.name = "Consumer_"+str(processNo)
	def run(self):
		#signal.signal(signal.SIGTERM,consumer_exit)
		try:
			self.logger = logger.getLogger(logging.INFO,"tfidf."+str(self.processNo)+".log")
			#self.logger = multiprocessing.get_logger()
			jieba.setLogLevel(logging.INFO)
			jieba.load_userdict("/home/yyf/workspace/separate/dict.txt")
			while(True):
				datas = self.queue.get()
				if 0 == len(datas):
					self.logger.error("null list exit")
					break
				#saveID(datas[0])
				datas = self.processText(datas)
				self.save_queue.put(datas)
				#saveID(0-datas[0])
		except SystemExit:
			self.logger.info("process exit with sys.exit()")
			exit(0)
		except:
			error = traceback.format_exc()
			self.logger.error(str(self.processNo)+" Error")
			self.logger.error(error)			
			exit(-1)

	def processText(self,texts):
		ID = texts[0]
		#setIDToFile(ID)
		self.logger.debug("get datas ID="+str(ID))
		wordsDict = {}
		for text in texts[1:]:
			text = removeNULL(text)
			words = getWordList(cut(text))
			words = oneWordFilter(words)
			words = puncFilter(words,PUNC)
			words = digitalFilter(words)
			wordsDict = addWordDict(words,wordsDict)
			self.logger.debug("cut over ID="+str(ID))
			db_data = tfidfDB.getFromWords(wordsDict.keys())
			db_data = tfidfDB.tranDataToDict(db_data)
			d1,d2 = mergeWordDict(db_data,wordsDict)
			#printError(d1)
			#printError(d2)
			return [ID,d1,d2]
	def exit(self,argv1,argv2):
		# 没啥用,先放这儿
		self.logger.info("Consumer exit")
		sys.exit(0)
			

#
#
#######################################################

#######################################################
# 第二个消费者,处理Comsumer处理后的数据,将数据存入数据库,
# 如果让每个Consumer处理保存过程的话会出现脏数据
def saver_test(ID):
	with open("savertest.index","a") as f:
		f.write(str(ID)+"\n")
class Consumer_saver(multiprocessing.Process):
	def __init__(self,save_queue):
		multiprocessing.Process.__init__(self)
		self.save_queue = save_queue
		self.name = "Consumer_saver"
	def run(self):
		# 初始化
		self.ID =  startID
		self.IDs = set()
		# 初始化logger
		self.logger = logger.getLogger(logging.INFO,"tfidf.saver.log")
		# 获取进度,以便吻合发过来的ID
		# 这个里面获取saveID是有必要的,因为如果在恢复进度时出错,
		# 再次保存进度需要此ID
		saveID,saveIDs = getIDFromFile()
		self.logger.info("saver get ID and IDs:"+str(saveID)+"-"+str(saveIDs))	
		if saveID > 0:
			self.ID = saveID
			self.IDs = set(saveIDs)
		# 设置信号量
		signal.signal(signal.SIGTERM,self.exit)
		try:
			while(True):
				data = save_queue.get()
				if 0 == len(data):
					continue
				if -1 == data[0]:
					setIDToFile(self.ID,self.IDs)
					break
				self.saveData(data)
				self.IDs.add(data[0])
				self.logger.info("save over ID="+str(data[0]))
				self.ID,self.IDs = manageIndex(self.ID,self.IDs)
				setIDToFile(self.ID,self.IDs)
				#self.logger.info("saver storeID :"+str(self.ID)+"-"+str(self.IDs))
		except SystemExit:
			self.logger.info("process exit with sys.exit()")
			exit(0)
		except:
			setIDToFile(self.ID,self.IDs)
			self.logger.error("saver storeID :"+str(self.ID)+"-"+str(self.IDs))
			error = traceback.format_exc()
			self.logger.error("saver error")
			self.logger.error(error)
			exit(-1)
	def saveData(self,data):
		d1 = data[1]
		d2 = data[2]
		if 0 != len(d1):
			tfidfDB.updateWords(d1)
		if 0 != len(d2):
			tfidfDB.addWords(d2)
	def exit(self,arg1,arg2):
		self.logger.info("get SIGTERM exiting....")
		self.logger.info("saver storeID :"+str(self.ID)+"-"+str(self.IDs))
		setIDToFile(self.ID,self.IDs)
		sys.exit(0)
###############################################################
##
##	主程序以及全局变量
###############################################################
# 主进程的作用:
#	1.进程管理能力,当子进程出错返回后重启进程
#	2.在自己被关闭时,等待子进程保存进度
#	3.deamon化的进程关闭
#
################################################################
################################################################
##	 全局变量												####
################################################################
PROCESS_SIZE = 7 # 处理词所用进程数							####
# 获取数据库大小											####
DATA_MAXSIZE = rawdataDB.zl_project.select().count()		####
# 每次处理,储存,获取的大小.一旦开始不能随意更换				####
DATA_SIZE = 100# 试验性的,可以调大一点						####
# tests传输队列大小											####
QUEUE_MAXSIZE = 2											####
# datas存储传输队列大小										####
S_QUEUE_MAXSIZE =1											####
# 非空数据开始索引											####
startID = 3512466											####
															####
################################################################
################################################################

################################################################
# 重启process方法:
#
# Consumer : 可以直接用terminate直接终结,因为Consumer不用保存任
# 何现场
# Producer : 同上
# Consumer_save :
# 因为saver需要保存进度,所以不能直接终结,其进程会捕捉SIGTERM信号
# 量,保存后退出
# 
################################################################
################################################################
## 进程管理相关函数
################################################################
# 清空消息队列,现在已没有什么用
def clearQueue(queue):
	while not queue.empty():
		queue.get()
# 停止所有进程,除了需要保存进度的Consumer_saver,
# 统一使用SIGKILL终结
def stopProcesses(processes):
	clearQueue(save_queue)
	#save_queue.put([-1,None,None])方法废弃

	log_.info("stop processse")
	# 此部分将其属性的daemon设置成True,会自动终结
	# 有时会出问题,所以依然用SIGKILL终结
	for p in processes[0]:
		if p.is_alive():
			log_.info("stop p")
			pid = p.pid
			os.kill(pid,signal.SIGKILL)
			#p.terminate()
			#log_.info("join p")
			#p.join()
			#log_.info("join over p")
	
	if processes[1].is_alive():
		'''
		log_.info("stop producer")
		processes[1].terminate()
		log_.info("join Producer")
		processes[1].join()
		log_.info("join over Producer")
		'''
		# 此处因为Producer queue.put()后的block无法正确处理信号量的
		# bug,所以直接用9信号量,简单粗暴
		pid = processes[1].pid
		os.kill(pid,signal.SIGKILL)
	#print("等待saver保存现场")
	#process_saver.join()
	if processes[2].is_alive():
		log_.info("stop saver")
		processes[2].terminate()	
		log_.info("join saver")
		processes[2].join()
		log_.info("join over saver")
	
def startProcesses(processes):
	processes[2].start()
	processes[1].start()
	for p in processes[0]:
		p.start()

def initProcesses():
	process_list = []
	for i in xrange(PROCESS_SIZE):
		process = Consumer(queue,save_queue,str(i))
		process.daemon = True
		process_list.append(process)
	process_saver = Consumer_saver(save_queue)
	process_saver.daemon = True
	process_producer = Producer(queue,DATA_SIZE)
	process_producer.daemon = True
	return [process_list,process_producer,process_saver]
def restartProcesses(processes):
	stopProcesses(processes)
	processes = initProcesses()
	startProcesses(processes)
	return processes

############################################################
# 1 每次启动将pid存入tfidf.pid中,终止程序的时候利用存入的pid
# 终止程序
# 2 覆盖signal的SIGTERM,这样可以在退出之前保存一些进度信息
# 相应的Consumer_save也实现此信号量,这样可以保证退出时可以
# 保存进度
#############################################################
def getPidFromFile():
	with open("tfidf.pid") as f:
		pid = f.read()
		if pid.isdigit():
			pid = int(pid)
			return pid
		else:
			print("无法获取PID")
			sys.exit(-1)
def savePidToFile(pid):
	with open("tfidf.pid","w") as f:
		f.write(str(pid))
def killandExit(pid):
	try:
		pid = int(pid)
		os.kill(pid,signal.SIGTERM)
		while True:
		# 检测进程是否终结,直到终止退出
			os.kill(pid,0)
			time.sleep(1)
	except OSError:
			print("stop over")
			sys.exit(0)
###########################################################

# 选项 
#	-s 程序自己找到PID并且终止
#	--stop=PID 指定PID终止进程
#	注:
#	虽然实现了SIGTERM信号量,但是还是建议不要使用kill命令终结
#	进程
shortopt = 'sh'
longopt = ["stop="]
pid = -1
# 获得选项
optlist, argvs = getopt.getopt(sys.argv[1:],shortopt,longopt)
if 0 != argvs:
	for key ,value in optlist:
		if(key == "--stop"):
			if value.isdigit():
				print("stopping.....")
				killandExit(int(value))
			print("need PID")
			sys.exit(-1)
		elif(key == "-h"):
			print("fuck you , and read the code")
			sys.exit(0)
		elif(key == "-s"):
			pid = getPidFromFile()
			print("PID is:"+str(pid)+"\nstopping")
			killandExit(pid)





# SIGTERM信号量 对应函数 终止程序使用
def sigKillSelf(argv1,argv2):
	log_.info("exiting ....")
	stopProcesses(processes)
	log_.info("stoped")
	sys.exit(0)
# 获取PID存入文件,并绑定信号量
pid = os.getpid()
savePidToFile(pid)
signal.signal(signal.SIGTERM,sigKillSelf)

# Get Logger
log_ = logger.getLogger(logging.INFO,"tfidf.main.log")

log_.info("start process")

# init process
queue = multiprocessing.Queue(QUEUE_MAXSIZE)
save_queue = multiprocessing.Queue(S_QUEUE_MAXSIZE)
processes = initProcesses()
#process_list,process_producer,process_saver = initProcesses()
# start process
startProcesses(processes)

log_.info("start process over")

try:
	while True:
		for p in processes[0]:
			if not p.is_alive():
				log_.info("Consumer "+p.name+" is stoped Restart Process")
				processes = restartProcesses(processes)
				continue
		if not processes[1].is_alive():
			log_.info("Producer is stopped Restart")
			processes = restartProcesses(processes)
			continue
		if not processes[2].is_alive():
			log_.info("Saver is stopped Restart")
			processes = restartProcesses(processes)
			continue
		time.sleep(10)
except SystemExit:
	log_.info("process exit with sys.exit()")
	exit(0)

except:
	log_.error("get some error EXIT")
	log_.error(traceback.format_exc())
	stopProcesses(processes)
	sys.exit(-1)



# TODO 基本功能已经调试完毕,未完成部分:

# DOING: 
# 进程终止会打出一堆Traceback.去掉,因为这是已知异常,除了这个异
# 常,剩下的所有的都要打印到log中去.
# log文件的同一命名tfidf开头


# 保存进度是否完整可靠的验证
# 进行完上述测试后就可以直接部署到服务器了,参数设想是
# textsize 200 这个太大如果真的在跑的过程中出现问题,脏数据不会
# 造成太大影响
# 进程数 8个,毕竟8核 queue保持不变大了没用
# log文件设想是做成每1w个记录一组,否则一个文件过大,不容易debug



# 进度保存问题的解决:
# 上述问题现在的解决方法用的是重启所有process的方法,因为重启
# Consumer的方法还可能导致别的问题,可以遇见的就是整个进程重启
# 时,因为Consumer的index文件中可能上次没有处理的记录,这时
# Consumer会先处理这个记录的ID,但是在这种情况下使不能处理的,因为
# Producer还会给queue发送这个ID一次,导致Consumer_save储存两次,
# 不仅如此,还可能导致Consumer_save维护的IDs集合出问题(理论上应该
# 不会出问题,但谁知道呢).
# 解决上述描述的只是可能发生的问题,还有一些没有预见的问题,且解决
# 可遇见问题会更大的增加程序的复杂度(现在已经很大了!!!)可能会导致
# 更多的问题,成本太高,故用重启所有进程的方法.

