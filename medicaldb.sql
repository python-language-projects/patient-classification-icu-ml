
DROP TABLE IF EXISTS `tbladmin`;

CREATE TABLE `tbladmin` (
  `adminid` varchar(50) NOT NULL,
  `password` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`adminid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `tbladmin` */

insert  into `tbladmin`(`adminid`,`password`) values 
('admin','123');

/*Table structure for table `tblmembers` */

DROP TABLE IF EXISTS `tblmembers`;

CREATE TABLE `tblmembers` (
  `memberid` varchar(50) NOT NULL,
  `password` varchar(50) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `mobile` varchar(50) DEFAULT NULL,
  `emailid` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`memberid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `tblmembers` */

insert  into `tblmembers`(`memberid`,`password`,`name`,`mobile`,`emailid`) values 
('1','123','Anil Kumar','7899900294','Anilkumar@gmail.com');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
