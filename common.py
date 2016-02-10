#coding:utf-8
import time
from datetime import datetime , date , tzinfo , timedelta 
import calendar
class UTC(tzinfo): 
	def __init__(self,offset = 0):
		self._offset = offset
	def utcoffset(self, dt):
		return timedelta(hours=self._offset)
	def tzname(self, dt):
		return "UTC +%s" % self._offset
	def dst(self, dt):
		return timedelta(hours=self._offset)


def datetimeToTimestamp(dt):
	return (dt-UTC(8).utcoffset(0) - datetime(1979,1,1)).total_seconds()

def timestampToDatetime(timesamp):
	return datetime.fromtimestamp(timesamp)

