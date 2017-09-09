CREATE TABLE `bj_new_house_price` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `district_name` varchar(45) DEFAULT NULL,
  `block_name` varchar(45) DEFAULT NULL,
  `address` varchar(45) DEFAULT NULL,
  `price` int(11) DEFAULT NULL,
  `house_key` varchar(45) DEFAULT NULL,
  `created_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `location` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key_UNIQUE` (`house_key`)
) ENGINE=InnoDB AUTO_INCREMENT=521 DEFAULT CHARSET=gb2312