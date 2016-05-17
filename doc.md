## 一 请求以及回应解释和规定

### 1 汇总
	
	addTask
	deleteTask
	editTask
	getTask
	listTask
	startTask
	stopTask
	restartTask

### addTask

向database添加相应字段,task_status="a"
cgi处理,json通讯,参数为task_name,task_type,task_para

### deleteTask

只有处于精致状态的任务才能被删除
cgi处理,json通讯,参数task_ID

### editTask

只有处于静止状态的任务才能被修改
cgi处理,json通讯,参数为task_ID,task_name,task_type,task_para

### getTask

cgi处理,json通讯,参数为task_ID

### listTask

cgi处,json通讯,参数list_type,返回json,参数同字段名词

	list_type:
	a : 所有
	s : 静止状态的
	p :	运行状态的
	c : 完成的
	e : 出错的

### startTask

只有处于"a"状态的任务才能被启动
传入socket Server 参数task_ID,通讯成功即可返回

### stopTask

只有处于运行状态的任务才能被停止
传入socket Server 参数task_ID,通讯成功即可返回

### restartTask

只有处于"e"出错状态的任务才能被重启,重启后任务状态为"a"
cgi处理,json通讯,参数task_ID

### task状态定义

	静止状态: a e
	运行状态: p c

## task字段定义

	task_ID				: unsign int
	task_name			: char[50]
	task_create_time	: timestamp
	task_finish_time	: timestamp
	task_type			: int
	task_status			: char
	task_data			: char[size]
	task_para			: 根据不同type定义不同(现阶段为string)
	初始需要 name type para

### task_type定义

	1	:	TFIDF关键词提取,需要para为查询式

### task_status定义以及状态转换

		正常执行	a->s->p->c
		重启后		e->a
		编辑后		e->a or a->a
		a:addTask	任务添加,addTask后为a状态,必须手动开始任务才可以,避免重复提交,瞬间执行多个任务
		s:startTasK	开启任务,并做一定的前期准备工作,1 检查参数正确性 2根据参数获取数据,数据获取成功后转入p状态
		p:process	执行中,因为有两个char,第二个char可以表示执行过程中的过程)
		c:complete	任务完成,任务完成后,task_date转换为任务完成时间
		e:error		出错,可以用 getResult 获取为何出错信息, s和p都可以转换为e.改：error的信息可以在task上直接
					看到，但是考虑到可能一个task可以执行多次，并不是每次的结果都一样，所以，在result里面也写入
		u:pause		后期实现 暂停状态,仅p状态下可用

## Socket server通讯字段定义

	version		uns int	版本 版本不对 返回version_err
	request		char	请求的类别
	parameter	请求附加参数 可选 取决于 request

上述字段用json传输

### request字段解释

	注:前台请求区分也用此字段
	
	大写为向服务器请求用,小写为服务器返回信息

	cgi部分用OK来返回正确error返回错误
	A:addTask
	L:listTask
	C:getTask
	B:startTask
	S:stopTask
	R:restartTask
	I:editTask
	F:deleteTask
	P:pauseTask
	G:getResult
	D:deleteResult
	O:OK
	E:error

