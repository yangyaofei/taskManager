#  coding:utf-8
from peewee import Model, MySQLDatabase, PrimaryKeyField, CharField, TextField
from peewee import IntegerField
import config


class zl_project_data:
	def __init__(self, zl_project):
		self.id = zl_project.id
		self.zl_type = zl_project.zl_type
		self.apply_num = zl_project.apply_num
		self.apply_day = zl_project.apply_day
		self.public_num = zl_project.public_num
		self.public_day = zl_project.public_day
		self.name = zl_project.name
		self.main_classnum = zl_project.main_classnum
		self.classnum = zl_project.classnum
		self.priority = zl_project.priority
		self.apply_people = zl_project.apply_people
		self.cp_num = zl_project.cp_num
		self.inventor = zl_project.inventor
		self.international_apply = zl_project.international_apply
		self.international_public = zl_project.international_public
		self.intocountday_day = zl_project.intocountday_day
		self.agency = zl_project.agency
		self.agent = zl_project.agent
		self.category_class = zl_project.category_class
		self.former_applynum = zl_project.former_applynum
		self.award_day = zl_project.award_day
		self.abstractcontent = zl_project.abstractcontent
		self.dominion = zl_project.dominion
		self.apatent_family = zl_project.apatent_family
		self.patent_num = zl_project.patent_num
		self.examinant = zl_project.examinant
		self.instructpic_pagenum = zl_project.instructpic_pagenum
		self.instruction_pagenum = zl_project.instruction_pagenum
		self.require_pagenum = zl_project.require_pagenum
		self.instruction_pic = zl_project.instruction_pic
		self.instruction = zl_project.instruction
		self.right_require = zl_project.right_require
		self.reference_document = zl_project.reference_document
		self.apply_source = zl_project.apply_source
		self.agent_type = zl_project.agent_type
		self.appcountry_num = zl_project.appcountry_num
		self.page_num = zl_project.page_num
		self.release_path = zl_project.release_path
		self.country_classnum = zl_project.country_classnum
		self.country_mainclassnum = zl_project.country_mainclassnum
		self.europe_classnum = zl_project.europe_classnum
		self.europe_mainclassnum = zl_project.europe_mainclassnum
		self.abstractpic_path = zl_project.abstractpic_path
		self.pdfdownloadurl = zl_project.pdfdownloadurl
		self.typenum = zl_project.typenum

		self.field1 = zl_project.field1
		self.field2 = zl_project.field2
		self.field3 = zl_project.field3
		self.field4 = zl_project.field4
		self.field5 = zl_project.field5
		self.field6 = zl_project.field6
		self.field7 = zl_project.field7
		self.field8 = zl_project.field8
		self.field9 = zl_project.field9
		self.field10 = zl_project.field10
		self.title1 = zl_project.title1
		self.title2 = zl_project.title2
		self.title3 = zl_project.title3
		self.title4 = zl_project.title4
		self.title5 = zl_project.title5
		self.title6 = zl_project.title6
		self.content1 = zl_project.content1
		self.content2 = zl_project.content2
		self.content3 = zl_project.content3
		self.content4 = zl_project.content4
		self.content5 = zl_project.content5
		self.content6 = zl_project.content6
		self.alltext = zl_project.alltext

db_config = config.getRaw()
db = MySQLDatabase(**db_config)


class zl_project(Model):

	id = PrimaryKeyField()
	zl_type = CharField()
	apply_num = CharField()					# 申请（专利）号
	apply_day = CharField()					# 申请日
	public_num = CharField()				# 公开（公告）号
	public_day = CharField()				# 公开（公告）日
	name = CharField()						# 名称
	main_classnum = CharField()				# 主分类号
	classnum = TextField()					# 分类号
	priority = TextField()					# 优先权
	apply_people = CharField()				# 申请（专利权）人
	cp_num = CharField()					# 国省代码
	inventor = CharField()					# 发明（设计）人
	international_apply = CharField()		# 国际申请
	international_public = CharField()		# 国际公布
	intocountday_day = CharField()			# 进入国家日
	agency = CharField()					# 专利代理机构
	agent = CharField()						# 代理人
	category_class = CharField()			# 范畴分类
	former_applynum = CharField()			# 分案原申请号
	award_day = CharField()					# 颁证日
	abstractcontent = TextField()			# 摘要
	dominion = TextField()					# 主权项
	apatent_family = TextField()			# 同组专利项
	patent_num = CharField()				# 专利号
	examinant = CharField()					# 审查员
	instructpic_pagenum = CharField()		# 说明书附图页数
	instruction_pagenum = CharField()		# 说明书页数
	require_pagenum = CharField()			# 权利要求页数
	instruction_pic = TextField()			# 说明书附图
	instruction = TextField()				# 说明书
	right_require = TextField()				# 权利要求书
	reference_document = TextField()		# 参考文献
	apply_source = CharField()				# 申请来源
	agent_type = CharField()				# 专利类型
	appcountry_num = CharField()			# 申请国代码
	page_num = CharField()					# 页数
	release_path = CharField()				# 发布路径
	country_classnum = CharField()			# 本国分类号
	country_mainclassnum = CharField()		# 本国主分类号
	europe_classnum = CharField()			# 欧洲分类号
	europe_mainclassnum = CharField()		# 欧洲主分类号
	abstractpic_path = TextField()			# 摘要附图存储路径
	pdfdownloadurl = CharField()			# pdf下载路径
	typenum = IntegerField()

	field1 = CharField()
	field2 = CharField()
	field3 = CharField()
	field4 = CharField()
	field5 = CharField()
	field6 = CharField()
	field7 = CharField()
	field8 = CharField()
	field9 = CharField()
	field10 = CharField()
	title1 = CharField()     # 小标题1
	title2 = CharField()     # 小标题2
	title3 = CharField()     # 小标题3
	title4 = CharField()     # 小标题4
	title5 = CharField()     # 小标题5
	title6 = CharField()     # 小标题6
	content1 = TextField()     # 小标题1的内容
	content2 = TextField()     # 小标题2的内容
	content3 = TextField()     # 小标题3的内容
	content4 = TextField()     # 小标题4的内容
	content5 = TextField()     # 小标题5的内容
	content6 = TextField()     # 小标题6的内容
	alltext = TextField()     # xml全文

	class Meta:
		db_table = 'zl_project'
		database = db


def getFromID(ID):
	return zl_project.select().where(zl_project.id == ID).get()


def getFromIDs(IDs):
	datas = []
	raw_datas = zl_project.select().where(zl_project.id << IDs)
	for data in raw_datas:
		datas.append(zl_project_data(data))
	return datas
