#coding:utf-8 
from peewee import *
#from datetime import datetime , date , tzinfo , timedelta 

db_config = {
     'host': 'server2.zhchtd.com',
     'port': 23306,
     'user': 'zhchtd',
     'password': 'zhchtd123',
     'database': 'patent'
 }
db = MySQLDatabase(**db_config)
class zl_project(Model):

	id						=	PrimaryKeyField()
	zl_type					=	CharField()
	apply_num				=	CharField()	#申请（专利）号
	apply_day				=	CharField()	#申请日
	public_num				=	CharField()	#公开（公告）号
	public_day				=	CharField()	#公开（公告）日
	name					=	CharField()	#名称
	main_classnum			=	CharField()	#主分类号
	classnum				=	TextField()	#分类号
	priority				=	TextField()	#优先权
	apply_people			=	CharField()	#申请（专利权）人
	cp_num					=	CharField()	#国省代码
	inventor				=	CharField()	#发明（设计）人
	international_apply		=	CharField()	#国际申请
	international_public	=	CharField()	#国际公布
	intocountday_day		=	CharField()	#进入国家日
	agency					=	CharField()	#专利代理机构
	agent					=	CharField()	#代理人
	category_class			=	CharField()	#范畴分类
	former_applynum			=	CharField()	#分案原申请号
	award_day				=	CharField()	#颁证日
	abstractcontent			=	TextField()	#摘要
	dominion				=	TextField()	#主权项
	apatent_family			=	TextField()	#同组专利项
	patent_num				=	CharField()	#专利号
	examinant				=	CharField()	#审查员
	instructpic_pagenum		=	CharField()	#说明书附图页数
	instruction_pagenum		=	CharField()	#说明书页数
	require_pagenum			=	CharField()	#权利要求页数
	instruction_pic			=	TextField()	#说明书附图
	instruction				=	TextField()	#说明书
	right_require			=	TextField()	#权利要求书
	reference_document		=	TextField()	#参考文献
	apply_source			=	CharField()	#申请来源
	agent_type				=	CharField()	#专利类型
	appcountry_num			=	CharField()	#申请国代码
	page_num				=	CharField()	#页数
	release_path			=	CharField()	#发布路径
	country_classnum		=	CharField()	#本国分类号
	country_mainclassnum	=	CharField()	#本国主分类号
	europe_classnum			=	CharField()	#欧洲分类号
	europe_mainclassnum		=	CharField()	#欧洲主分类号
	abstractpic_path		=	TextField()	#摘要附图存储路径
	pdfdownloadurl			=	CharField()	#pdf下载路径
	typenum					=	IntegerField()	
	
	field1		=	CharField()	
	field2		=	CharField()	
	field3		=	CharField()	
	field4		=	CharField()	
	field5		=	CharField()	
	field6		=	CharField()	
	field7		=	CharField()	
	field8		=	CharField()	
	field9		=	CharField()	
	field10		=	CharField()	
	title1		=	CharField()	#小标题1
	title2		=	CharField()	#小标题2
	title3		=	CharField()	#小标题3
	title4		=	CharField()	#小标题4
	title5		=	CharField()	#小标题5
	title6		=	CharField()	#小标题6
	content1	=	TextField()	#小标题1的内容
	content2	=	TextField()	#小标题2的内容
	content3	=	TextField()	#小标题3的内容
	content4	=	TextField()	#小标题4的内容
	content5	=	TextField()	#小标题5的内容
	content6	=	TextField()	#小标题6的内容
	alltext		=	TextField()	#xml全文
	class Meta:
		db_table = 'zl_project'
		database = db

def getFromID(ID):
	return zl_project.select().where(zl_project.id == ID)

def getFromIDs(IDs):
	return zl_project.select().where(zl_project.id << IDs)

