DROP TABLE IF EXISTS `taskResult`;
CREATE TABLE `taskResult` (
  `task_id` int(11) NOT NULL,
  `word` varchar(50) COLLATE utf8_bin NOT NULL,
  `word_weight` int(11) NOT NULL,
  `weight_type` int(11) NOT NULL,
  PRIMARY KEY (`task_id`,`word`,`weight_type`)
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_bin;
