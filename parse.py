#coding:utf-8
import struct
import common
'''
python格式与二进制数据转换
+---------------+
|				|
|				|
|     version 	| uns int	版本 版本不对 返回version_err
|				|
+---------------+
|     request 	| char	请求的类别 
+---------------+
|				|
|    para-size	| uns int	请求的附加参数长度 0为没有 则结束
|				|		只决定参数长度,参数意义由request决定
|				|
+---------------+
|				|
/				/
/    parameter	/	char[pata-size]	
/				/	请求附加参数 可选 取决于 request
|				|
+---------------+

request:
大写为向服务器请求用,小写为服务器返回信息
如果只用返回ok即可的请求,para-size位置置为0 为成功

parameter:

A:addTask 
	为向web请求内容	
L:listTask 
	返回时需要:
	+-----------+-----------+
	|  task_no	|task_size	| 
	+-----------------------+
	/						/
	/		task_list		/
	+-----------------------+
	task_no		:	unsign int	ask个数
	task_size	:	unsign int	每个task item 大小
	task_item	:	task具体内容结构见下(会修改,以完善)
	+-----------+-----------+-----------+-----------+
	|task_ID	|task_status|task_date	|task_etc	|
	+-----------+-----------+-----------+-----------+
	task_ID		:	unsign int
	task_status	:	char[2]
	task_date	:	long POSIX timestamp
	task_etc	:	char[100] 描述任务 必须存在
G:getResult
	未编辑 
O:over
	收到之后直接关闭
E:err
	发送之后直接断开
'''
VERSION = 1
HEADER_FORMAT = "!IcI"
TASK_HEADER_FORMAT = "!II"
TASK_ITEM_FORMATE = "!I2sl100s"
# 主转换函数 转换主结构体 op 1为转换为python 0为转换为c type 数据
# data 在python中为一个列表
def parseTo(data,op):
	if op:
		d = struct.unpack_from(HEADER_FORMAT,data)
		assert(d[0] == VERSION)
		return d
	else:
		return struct.pack(HEADER_FORMAT,data[0],data[1],data[2])
def parseToBin(request,para_data):
	data = []
	data.append(VERSION)
	data.append(request)
	data.append(len(para_data))
	return parseTo(data,0)+para_data
def parseToList(data):
	offset = struct.calcsize(HEADER_FORMAT)
	header_data = struct.unpack_from(TASK_HEADER_FORMAT,data,offset)
	task_no = header_data[0]	
	task_size = header_data[1]
	if(task_size <> struct.calcsize(TASK_ITEM_FORMATE)):
		assert 0
	i = 0
	taskList = []
	offset += struct.calcsize(TASK_HEADER_FORMAT)
	while(i < task_no):
		task = struct.unpack_from(TASK_ITEM_FORMATE,data,offset)
		task = list(task)
		#task[3] = common.timestampToDatetime(task[3])
		taskList.append(task)
		offset += struct.calcsize(TASK_ITEM_FORMATE)
		i += 1
	return taskList

def parseToBinList(taskList):
	task_no = len(taskList)
	task_size = struct.calcsize(TASK_ITEM_FORMATE)
	data = struct.pack(TASK_HEADER_FORMAT,task_no,task_size)
	for	task in taskList:
		#task[2] = long(common.datetimeToTimestamp(task[2]))
		print("--------")
		print(task[2])
		print("--------")
		data += struct.pack(TASK_ITEM_FORMATE,task[0],task[1],task[2],task[3])
	return parseToBin("l",data)
def parseToAddTask(data):
	offset = struct.calcsize(HEADER_FORMAT)
	size = len(data)-offset
	return struct.unpack_from(str(size)+"s",data,offset)
def parseToBinAddTask(data):
	size = len(data)
	raw_data = struct.pack(str(size)+"s",data)
	return parseToBin("A",raw_data)	
# data 为处理好的数据 判断其中内容后直接执行相关请求
def routeRequest(data):
	data = parseTo(data,1)
	if(data[1]=="A"):
		addTask(data)
	if(data[1]=="L"):
		listTask(data)
	if(data[1]=="G"):
		getResult(data)
	if(data[1]=="O"):
		over(data)



