#  coding:utf-8
#  此模块用于获取需要处理数据的IDs

import urllib
import urllib2
import hashlib
import json
import time

url = "http://server2.zhchtd.com:22280/getprojectjson"
KEY = "zhuanlikey"
ID = -1
MAX_QUEUE = 1000


def getData(values):
	# logger.info("get data from :"+url)
	# values = values.encode("utf-8")
	data = urllib.urlencode(values)
	req = urllib2.Request(url, data)
	return json.loads(urllib2.urlopen(req).read())


def generateCode(time):
	key = hashlib.md5((str(time) + KEY).encode("utf-8")).hexdigest()
	key = hashlib.md5(key.encode("utf-8")).hexdigest()
	return key


def generateValues(sql):
	ts = long(time.time())
	key = generateCode(ts)
	values = {
		"code": key,
		"time": str(ts),
		"where": sql
	}
	return values


def getIDs(reqdata):
	if int(reqdata["status"]) == 0:
		return reqdata["list"]
	else:
		# print(reqdata["message"])
		return []
