# coding:utf-8
import ConfigParser
import os

realpath = os.path.realpath(__file__).split("db_config")[0]
cp = ConfigParser.ConfigParser()
cp.read(realpath + "db_config.ini")


def getDict(section):
	config = {}
	for s in cp.items(section):
		if s[1].isdigit():
			config[s[0]] = int(s[1])
		else:
			config[s[0]] = s[1]
	return config


def getTFIDF():
	return getDict("tfidf")


def getRaw():
	return getDict("raw")


def getTaskResult():
	return getDict("taskResult")
