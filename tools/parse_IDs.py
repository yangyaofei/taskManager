#  coding:utf-8
#  此模块用于获取需要处理数据的IDs
import urllib
import urllib2
import hashlib
import json
import time
import es_restful
import config

url = "http://server2.zhchtd.com:22280/getprojectjson"
KEY = "zhuanlikey"
ID = -1
MAX_QUEUE = 1000


# 生成验证key 并返回key和timestamp
def generate_code():
	ts = long(time.time())
	key = hashlib.md5((str(ts) + KEY).encode("utf-8")).hexdigest()
	key = hashlib.md5(key.encode("utf-8")).hexdigest()
	return ts,key


# 生成查询 检索式->ES restful 的JSON
def generate_values(sql):
	ts,key = generate_code()
	values = {
		"code": key,
		"time": str(ts),
		"where": sql
	}
	return values


# 获取返回JSON数据,并且解析,输入为检索式
def get_es_query(sql):
	data = generate_values(sql)
	data = urllib.urlencode(data)  # encode
	req = urllib2.Request(url, data)
	response = urllib2.urlopen(req).read()
	json_data = json.loads(response)
	if 1000 == int(json_data["status"]):
		return {"query": json_data["query"]}
	else:
		return []


# 获取原始数据JSON,去掉es上的信息
def get_raw(sql, size=100):
	es_query = get_es_query(sql)
	if len(es_query) == 0:
		# raise Exception("SQL get fail")  # TODO Exception implement
		yield [],"get ES query fail"
		return
	es_config = config.get_elasticsearch()
	es_url = "http://" + es_config["host"]+":"+str(es_config["port"])
	es_index = es_config["index"]
	for item in es_restful.scroll(es_url, es_index,es_query,size=size):
		yield item['hits']["hits"],item["hits"]["total"]
