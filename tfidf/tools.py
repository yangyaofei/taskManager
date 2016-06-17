# coding:utf8

# 此文件提供所有数据的通用处理和封装


class tfidf_key:
		word = "TFIDF_word"
		frq = "TFIDF_frq"
		sum_frq = "TFIDF_sum_frq"


# 从切词结果得到词组成的list
# 只需要名词
# TODO 此处可能使用工具自带方法可以加快速度
def getWordList(words):
	l = []
	for i in words:
		if i.flag.find("n") != -1:
			l.append(i.word)
	return l


# 将d1,d2数据合并
# 返回值为两个,第一个是两个的并集部分并将词频相加,第二个是补集 d2-d1 部分
def mergeWordDict(d1, d2):
	s1 = set(d1.keys())
	s2 = set(d2.keys())

	s3 = s2 - s1
	s4 = s2 + s1
	d3 = {}
	d4 = {}
	for i in set(s3):
		d3[i] = d2[i]
	for i in set(s4):
		if i in s1 and i in s2:
			d4[i][tfidf_key.frq] = d1[i][tfidf_key.frq] + d2[i][tfidf_key.frq]
			d4[i][tfidf_key.sum_frq] = d1[i][tfidf_key.sum_frq] \
				+ d2[i][tfidf_key.sum_frq]
		if i in s1 and i not in s2:
			d4[i][tfidf_key.frq] = d1[i][tfidf_key.frq]
			d4[i][tfidf_key.sum_frq] = d1[i][tfidf_key.sum_frq]
		if i not in s1 and i in s2:
			d4[i][tfidf_key.frq] = d2[i][tfidf_key.frq]
			d4[i][tfidf_key.sum_frq] = d2[i][tfidf_key.sum_frq]
	return d1, d3


# 列表 如果第二个参数值,则加入到字典中,并返回
def addWordDict(texts, wordsDict=None):
	newWordDict = makeWordDict(texts)
	if wordsDict is not None:
		for i in newWordDict:
			if i in wordsDict:
				wordsDict[i][tfidf_key.sum_frq] +=\
					newWordDict[i][tfidf_key.sum_frq]
				wordsDict[i][tfidf_key.frq] += 1
			else:
				wordsDict[i] = {}
				wordsDict[i][tfidf_key.sum_frq] =\
					newWordDict[i][tfidf_key.sum_frq]
				wordsDict[i][tfidf_key.frq] = 1
				wordsDict[i][tfidf_key.word] = i
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
			wordsDict[i][tfidf_key.sum_frq] += 1
		else:
			wordsDict[i] = {}
			wordsDict[i][tfidf_key.sum_frq] = 1
			wordsDict[i][tfidf_key.frq] = 1
			wordsDict[i][tfidf_key.word] = i
	return wordsDict
