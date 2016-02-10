#coding:utf-8
import parse
import taskDB 
# data 为处理好的数据 判断其中内容后直接执行相关请求
def routeRequest(raw_data):
	data = parse.parseTo(raw_data,1)	
	if(data[1]=="A"):
		return addTask(raw_data);
	if(data[1]=="L"):
		return listTask(raw_data);
	if(data[1]=="G"):
		return getResult(raw_data);
	if(data[1]=="O"):
		return over(raw_data);

def addTask(data):
	print("addTask")
	raw = parse.parseToBin("a",'')
	return raw
def listTask(data):
	taskList = taskDB.getTaskInfo()
	return parse.parseToBinList(taskList)
def getResult(data):
	print("gerResult")
def over(data):
	print("over")

