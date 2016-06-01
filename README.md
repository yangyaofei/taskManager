此程序是一个用于数据处理的程序,为了方便进行数据处理,写了如下几个部分:

+ 简易的任务队列,以及多进程处理和管理部分
+ cgi脚本和相关网页和js脚本,用于在网页上操作进行数据处理
+ 任务队列和cgi脚本通讯的socket程序
+ 用于访问数据库的相应脚本
+ 用于tfidf的数据处理程序

## 程序初始配置
程序初始配置需要配置两个部分:
+ config.ini
+ DB/db_config.ini

### config.ini
此配置文件配置如下:
	
	[global]
	socket_port = 8001		# cgi和任务队列进行通讯的端口
	socket_buffer = 1024	# 通讯时socket缓存大小
	queue = 10				# 任务队列大小
	# 下列配置文件意义见`web`文件夹下的说明
	result_path = /var/www/html/result/
	result_path_web = /result/

### db_config.ini

此文件是数据库相关配置,具体参数如下:

	[raw]
	host = server2.zhchtd.com	# 数据库位置
	port = 23306				# 数据库端口
	user = zhchtd				# 用户名
	password = zhchtd123		# 密码
	database = patent			# 锁连接的数据库
	# 如上的配置需要配置四个,其余是
	[tfidf]
	[task]
	[taskResult]

### 数据库创建

需要创建3个数据库
+ tfidf
+ task
+ taskResult
其中tfidf是数据处理使用的数据库,非必要,剩下两个使必要数据库.
具体定义见`DB`文件夹下的`sql`文件

### server.py 启动可以选择daemon形式运行,具体见代码opt部分,很简洁

### log 见`log`文件夹下的`logger.log`文件

## 文件格式

python文件请遵守pep8规范,但是请使用TAB替代space

## log文件权限配置

如果cig脚本出现permission denied 
将log文件夹下的的log文件加入a+w权限即可

## 具体工程相关借口定义见`doc.md`文件
