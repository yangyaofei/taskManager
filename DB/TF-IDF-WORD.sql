CREATE table TFIDF_word(
	TFIDF_id int not null auto_increment,
	TFIDF_word varchar(50) not null,		-- 词
	TFIDF_frq int not null,					-- TFIDF 词频 每篇文章出现一次+1
	TFIDF_sum_frq int not null,				-- 总词频 +每篇文章的词频
	unique(TFIDF_word),
	primary key (TFIDF_id)
)CHARSET=utf8;
