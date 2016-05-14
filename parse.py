# coding:utf-8
import common
import json
'''
python格式与二进制数据转换
+---------------+
|				|
|				|
|	 version 	| uns int	版本 版本不对 返回version_err
|				|
+---------------+
|	 request 	| char	请求的类别
+---------------+
|				|
|	para-size	| uns int	请求的附加参数长度 0为没有 则结束
|				|		只决定参数长度,参数意义由request决定
|				|
+---------------+
|				|
/				/
/	parameter	/	char[pata-size]
/				/	请求附加参数 可选 取决于 request
|				|
+---------------+

request:
大写为向服务器请求用,小写为服务器返回信息
如果只用返回ok即可的请求,para-size位置置为0 为成功

request and parameter:

A:addTask
	+---------------+
	| task_type		| unsigned char
	+---------------+
	| task_name		|
	+---------------+
	/ para_data		/ 自定义 根据type
	/				/
	+---------------+
L:listTask
	返回时需要:
	+-----------------------+
	|		task_no			|
	+-----------------------+
	/						/
	/		task_list		/
	+-----------------------+
	task_no		:	unsign int	task个数
	task_item	:	task具体内容结构见下
	+-------+-------+-----------+-----------+-------+-------+-------+-------+
	|ID		|name	|create_time|finish_time|type	|status	|data	|para	|
	+-------+-------+-----------+-----------+-------+-------+-------+-------+
	ID			:	unsign int
	name		:	char[50]
	create_time	:	long POSIX timestamp
	finish_time	:	long POSIX timestamp
	type		:	unsigned char(DataBase int)
	status		:   char
	size		:	unsigned int
	data		:	char[size]
	para_size	:	unsigned int
	para		:	根据不同type定义不同(现阶段为string)
	--------
		status 状态转换所有标识:
		正常执行	a->s->p->c
		重启后		e->a
		编辑后		e->a or a->a

		a:addTask	任务添加,addTask后为a状态,必须手动开始任务才可以,避免重复提交,瞬间执行多个任务
		s:startTasK	开启任务,并做一定的前期准备工作,1 检查参数正确性 2根据参数获取数据,数据获取成功后转入p状态
		p:process	执行中,因为有两个char,第二个char可以表示执行过程中的过程)
		c:complete	任务完成,任务完成后,task_date转换为任务完成时间
		e:error		出错,可以用 getResult 获取为何出错信息, s和p都可以转换为e.改：error的信息可以在task上直接
					看到，但是考虑到可能一个task可以执行多次，并不是每次的结果都一样，所以，在result里面也写入
		u:pause		后期实现 暂停状态,仅p状态下可用
只需要ID的:
	+-----------+
	|	task_ID	|
	+-----------+
B:startTask(Begain) ID -> ok
S:stopTask		   ID -> ok
	停止任务,结束相关进程和线程,删除数据库中内容
	必须在s , p 状态下停止
R:restartTask
	重启任务,e状态可用
>I:editTask
	编辑任务,在e,a状态下可用,编辑完成后状态为a
	'''
# 还需要编写请求部分
'''
>>>F:deleteTask'''
# 忘记了，还没实现
'''
>>>P:pauseTask
	'''
# 暂停任务,后期实现<><><><>
'''
>G:getResult
	获取结果,e状态获取出错信息
	'''
# 还需要编写response部分
'''
D:deleteResult
	删除结果,并删除相关任务 in Database

'''
# 先保留 不知道是否这个设计有意义,未实现
'''
>>>O:over
	收到之后直接关闭
>>>E:err
	发送之后直接断开
'''
VERSION = 3
MAIN_KEY = ["version", "request", "paramenter"]
MAIN_TASK = ["task_list"]
TASK_KEY = [
	"task_ID", "task_name", "task_create_time", "task_finish_time",
	"task_type", "task_status", "task_paramenter", "task_data"]
TASK_ADD = ["taks_type", "task_name", "para_data"]
TASK_ID = "task_ID"

# 主转换函数
# data 在python中为一个列表


def parseTo(data):
	return json.loads(data)


def parseToJson(request, para_data=""):
	data = {}
	data[MAIN_KEY[0]] = VERSION
	data[MAIN_KEY[1]] = request
	if 0 != len(para_data):
		data[MAIN_KEY[2]] = para_data
	return json.dumps(data, cls=common.JsonEncoder)
# 函数命名规则
# client --> server
# 	client	:	parseToBin+***	 data	>>>	bindata
# 	server	:	parseTo+***		bindata	>>>	data
# server --> client
# 	client	:	parseTo+***		bindata	>>>	data
# 	server	:	respose+***		data	>>> bindata
# 参数:data为整个的rawdata


def parseToList(data):  # JSON to Dict
	data = parseTo(data)
	if MAIN_KEY[2] not in data:
		return []
	return data[MAIN_KEY[2]][MAIN_TASK[0]]


def resposeListTask(taskList):  # 参数是task的dict的list
	data = {}
	data[MAIN_TASK[0]] = taskList
	return parseToJson("l", data)


def parseToAddTask(data):
	if MAIN_KEY[2] not in data:
		return None
	return data[MAIN_KEY[2]]


def parseToBinAddTask(task_type, task_name, para_data):
	data = {
		TASK_ADD[0]: task_type,
		TASK_ADD[1]: task_name,
		TASK_ADD[2]: para_data
	}
	return parseToJson("A", data)
# 多个仅发送ID的请求，合并处理


def parseToBinwithID(task_ID, request):
	data = {TASK_ID: task_ID}
	return parseToJson(request, data)


def parseToBinStartTask(task_ID):
	return parseToBinwithID(task_ID, "B")


def parseToBinStopTask(task_ID):
	return parseToBinwithID(task_ID, "S")


def parseToBinRestartTask(task_ID):
	return parseToBinwithID(task_ID, "R")


def parseToBinDeleteTask(task_ID):
	return parseToBinwithID(task_ID, "F")


def parseToBinGetResult(task_ID):
	return parseToBinwithID(task_ID, "G")


def parseToBinDeleteResult(task_ID):
	return parseToBinwithID(task_ID, "D")
# 对应上述仅发送的请求的解析


def paresID(data):
	if MAIN_KEY[2] not in data:
		return None
	return data[MAIN_KEY[2]][TASK_ID]

# 为了统一函数 下面使request不需要参数的部分
# TODO 列出Task以后会分类,使列出所有,还是正在进行的,还是已完成的


def parseToBinListTask():
	return parseToJson("L", '')
# 将返回OK的都写下来，用字符到处写不好


def resposeAddTask():
	return parseToJson("a", '')


def resposeStartTask():
	return parseToJson("b", "")


def resposeStopTask():
	return parseToJson("s", "")


def resposeRestartTask():
	return parseToJson("r", "")


def resposeDeleteResult():
	return parseToJson("d", "")


def resposeError():
	return parseToJson("e", '')
