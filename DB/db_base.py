#  coding:utf-8
from peewee import MySQLDatabase
from playhouse.shortcuts import RetryOperationalError


class MySQLDatabaseRetry(RetryOperationalError, MySQLDatabase):
    def sequence_exists(self, seq):
        pass
