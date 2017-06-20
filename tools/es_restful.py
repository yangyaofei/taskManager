# coding:utf-8
# 此模块用于elasticsearch的restful API接口数据的处理
import urllib2
import json


# 查询并返回格式化好的数据
# 没有对参数进行检查
# TODO 参数修改 index
def query(host, index, data):
    data = json.dumps(data)  # encode
    req = urllib2.Request(host+index, data)
    respon = urllib2.urlopen(req).read()
    # print respon
    json_data = json.loads(respon)
    return json_data


# 用Scroll获取所有数据
def scroll(host, index, data, size=100, timeout="1m"):
    first = True  # 是否是首次查询
    data["size"] = size
    data = json.dumps(data)  # encode

    scroll_id = ""

    while True:
        if first:
            # 获取数据,并转成JSON
            req = urllib2.Request(host+index+"?scroll="+timeout, data)
            response = urllib2.urlopen(req).read()
            json_data = json.loads(response)
            # 从返回数据中标记scroll_id
            scroll_id = json_data["_scroll_id"]
            first = False
        else:
            # 设置请求JSON
            scroll_data = {
                "scroll_id": scroll_id,
                "scroll": timeout
            }
            scroll_data = json.dumps(scroll_data)
            # 请求并转换成JSON
            scroll_req = urllib2.Request(host + "/_search/scroll", scroll_data)
            scroll_response = urllib2.urlopen(scroll_req).read()
            json_data = json.loads(scroll_response)
        # 若hits长度为0则证明数据已经全部获取,返回
        if len(json_data["hits"]["hits"]) == 0:
            break
        yield json_data
