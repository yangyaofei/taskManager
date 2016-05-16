# coding:utf-8
import sys
# 使此脚本在任何目录下都可以检测到上一层目录
# 此处使用一个小技巧,sys.path的第一个地址是当前目录
# 将其改变即可

sys.path[0] = sys.path[0].replace("/client", "")
