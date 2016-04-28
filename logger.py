#coding:utf-8
import logging


LOG_LEVEL = logging.INFO
# NOTSET < DEBUG < INFO < WARNING < ERROR < CRITICAL
LOG_TO = "logger.log"
format_str		= "[%(levelname)s][%(asctime)s][%(process)d:%(processName)s][%(filename)s->%(funcName)s]%(message)s"
format_str_d	= "[%(levelname)s][%(asctime)s][%(process)d:%(processName)s][%(filename)s->%(lineno)d:%(funcName)s]%(message)s"
logger = logging.getLogger('')
if(len(LOG_TO) == 0):
	handler = logging.StreamHandler()
else:
	handler = logging.FileHandler(LOG_TO)
logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)
if(LOG_LEVEL == logging.DEBUG):
	formatter_debug = logging.Formatter(format_str_d) 
	handler.setFormatter(formatter_debug)	
else:
	formatter = logging.Formatter(format_str)
	handler.setFormatter(formatter)

#TODO  以后有时间自己研究logging系统,现在写的这个有很多并不对

def getLogger(level,log_file):
	logger = logging.getLogger('')
	if(len(LOG_TO) == 0):
		handler = logging.StreamHandler()
	else:
		handler = logging.FileHandler(log_file)
	logger.addHandler(handler)
	logger.setLevel(level)
	if(level == logging.DEBUG):	
		formatter_debug = logging.Formatter(format_str_d) 
		handler.setFormatter(formatter_debug)	
	else:	
		formatter = logging.Formatter(format_str)
		handler.setFormatter(formatter)
	return logger
	
