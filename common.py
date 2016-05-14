# coding:utf-8
from datetime import datetime, date, tzinfo, timedelta
import json


class UTC(tzinfo):
	def __init__(self, offset=0):
		self._offset = offset

	def utcoffset(self, dt):
		return timedelta(hours=self._offset)

	def tzname(self, dt):
		return "UTC +%s" % self._offset

	def dst(self, dt):
		return timedelta(hours=self._offset)


def datetimeToTimestamp(dt):
	return (dt - UTC(8).utcoffset(0) - datetime(1979, 1, 1)).total_seconds()


def timestampToDatetime(timesamp):
	return datetime.fromtimestamp(timesamp)


class JsonEncoder(json.JSONEncoder):

	def default(self, obj):
		if isinstance(obj, datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		elif isinstance(obj, date):
			return obj.strftime('%Y-%m-%d')
		else:
			return json.JSONEncoder.default(self, obj)
#
# copy from shadowsocks common.py
# convert bytes and str in daemon.py
#


def to_bytes(s):
	if bytes != str:
		if type(s) == str:
			return s.encode('utf-8')
	return s


def to_str(s):
	if bytes != str:
		if type(s) == bytes:
			return s.decode('utf-8')
	return s
