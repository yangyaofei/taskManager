# coding:utf-8
import ConfigParser
import common

path = common.getProjectPath()
path += "config.ini"
cp = ConfigParser.ConfigParser()
cp.read(path)


def get():
	config = {}
	for s in cp.items("global"):
		if s[1].isdigit():
			config[s[0]] = int(s[1])
		else:
			config[s[0]] = s[1]
	return config
