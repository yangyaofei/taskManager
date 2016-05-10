#coding:utf-8
from peewee import *
from playhouse import shortcuts
import config
db_config = config.getTFIDF()
db = MySQLDatabase(**db_config)
class TFIDF_word(Model):
	TFIDF_id		= PrimaryKeyField()
	TFIDF_word		= CharField()
	TFIDF_frq		= IntegerField()
	TFIDF_sum_frq	= IntegerField()
	class Meta:
		db_table = "TFIDF_word"
		database = db
def getFromWord(word):
	if len(word) == 0:
		return []
	TFIDF_word.select().where(TFIDF_word.TFIDF_word == word).get()
def getFromWords(words):
	#print(TFIDF_word.select().where(TFIDF_word.TFIDF_word << words).sql())
	return TFIDF_word.select().where(TFIDF_word.TFIDF_word << words)
def tranDataToDict(datas):#转换数据成直接可以利用的数据
	word_dict = {}
	for i in datas:
		word_dict[i.TFIDF_word] = {}
		word_dict[i.TFIDF_word]["TFIDF_frq"] = i.TFIDF_frq
		word_dict[i.TFIDF_word]["TFIDF_sum_frq"] = i.TFIDF_sum_frq
		word_dict[i.TFIDF_word]["TFIDF_word"] = i.TFIDF_word
	return word_dict
	
#def addWord(data):
#	word = TFIDF_word()
#	word.TFIDF_word		= data[0]
#	word.TFIDF_frq		= data[1]
#	word.TFIDF_sum_frq	= data[2]
#	word.save()


def addWords(words):
	if 0 == len(words):
		return 
	words = words.values()
	#print(words)	
	with db.atomic():
		#for idx in xrange(0, len(data_source), 1000):
		#print(TFIDF_word.insert_many(words).sql())
		TFIDF_word.insert_many(words).execute()


def updateWords(words):	# 字典 key word		value TFIDF_word TFIDF_frq TFIDF_sum_frq 的字典
						# 两个key都是words,value为频率
	if 0 == len(words):
		return
	w = words.keys()
	frq = words.values()
	w_frq = []
	w_sum_frq = []
	#print(frq)
	for i in frq:
		#print(i)
		w_frq.append(i["TFIDF_frq"])
		w_sum_frq.append(i["TFIDF_sum_frq"])
	w_frq = dict(zip(w,w_frq))
	w_sum_frq = dict(zip(w,w_sum_frq))
	case_frq = shortcuts.case(TFIDF_word.TFIDF_word,w_frq.items())
	case_sum_frq = shortcuts.case(TFIDF_word.TFIDF_word,w_sum_frq.items())
	query = TFIDF_word.update(TFIDF_frq = case_frq,TFIDF_sum_frq = case_sum_frq).where(TFIDF_word.TFIDF_word << w)
	#query_sum_frq =  TFIDF_word.update(TFIDF_sun_frq = case_sum_frq).where(TFIDF_word.TFIDF_word << words_frq.keys())
	query.execute()
	#query_sum_frq.execute()
