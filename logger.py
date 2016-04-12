#coding:utf-8
import logging


LOG_LEVEL = logging.INFO
# NOTSET < DEBUG < INFO < WARNING < ERROR < CRITICAL
LOG_TO = "logger.log"

logger = logging.getLogger('')
if(len(LOG_TO) == 0):
	handler = logging.StreamHandler()
else:
	handler = logging.FileHandler(LOG_TO)
formatter = logging.Formatter("[%(levelname)s][%(pathname)s][%(funcName)s][%(asctime)s]%(message)s")
format_debug = "[%(levelname)s][%(pathname)s][%(funcName)s][%(lineno)d][%(thread)d][%(threadName)s][%(process)d][%(asctime)s]%(message)s%(lineno)d"
formatter_debug = logging.Formatter(format_debug) 
logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)
if(LOG_LEVEL == logging.DEBUG):
	handler.setFormatter(formatter_debug)	
else:
	handler.setFormatter(formatter)



	
