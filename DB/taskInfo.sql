--
-- Table structure for table `taskInfo`
--

DROP TABLE IF EXISTS `taskInfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taskInfo` (
  `task_ID` int(11) NOT NULL AUTO_INCREMENT,
  `task_name` varchar(50) NOT NULL,
  `task_create_time` timestamp NOT NULL,
  `task_finish_time` timestamp NOT NULL,
  `task_type` int(11) NOT NULL,
  `task_status` char(1) NOT NULL,
  `task_data` varchar(10000) DEFAULT NULL,
  `task_para` varchar(1000) NOT NULL,
  PRIMARY KEY (`task_ID`)
)CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

