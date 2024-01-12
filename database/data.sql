-- MariaDB dump 10.19  Distrib 10.5.23-MariaDB, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: sample_handling
-- ------------------------------------------------------
-- Server version	10.9.7-MariaDB-1:10.9.7+maria~ubu2204

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Container`
--

DROP TABLE IF EXISTS `Container`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Container` (
  `containerId` int(11) NOT NULL AUTO_INCREMENT,
  `shipmentId` int(11) NOT NULL,
  `topLevelContainerId` int(11) DEFAULT NULL,
  `parentId` int(11) DEFAULT NULL,
  `name` varchar(40) NOT NULL,
  `type` enum('puck','falconTube','gridBox') NOT NULL,
  `capacity` smallint(6) DEFAULT NULL,
  `comments` varchar(255) DEFAULT NULL,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Generic additional details' CHECK (json_valid(`details`)),
  `requestedReturn` tinyint(1) NOT NULL,
  `externalId` int(11) DEFAULT NULL,
  `location` smallint(6) DEFAULT NULL,
  `registeredContainer` int(11) DEFAULT NULL,
  PRIMARY KEY (`containerId`),
  UNIQUE KEY `externalId` (`externalId`),
  KEY `parentId` (`parentId`),
  KEY `ix_Container_topLevelContainerId` (`topLevelContainerId`),
  KEY `ix_Container_shipmentId` (`shipmentId`),
  KEY `ix_Container_containerId` (`containerId`),
  CONSTRAINT `Container_ibfk_1` FOREIGN KEY (`shipmentId`) REFERENCES `Shipment` (`shipmentId`),
  CONSTRAINT `Container_ibfk_2` FOREIGN KEY (`parentId`) REFERENCES `Container` (`containerId`) ON DELETE SET NULL,
  CONSTRAINT `Container_ibfk_3` FOREIGN KEY (`topLevelContainerId`) REFERENCES `TopLevelContainer` (`topLevelContainerId`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=861 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Container`
--

LOCK TABLES `Container` WRITE;
/*!40000 ALTER TABLE `Container` DISABLE KEYS */;
INSERT INTO `Container` VALUES (1,1,1,NULL,'Container 01','puck',NULL,NULL,NULL,0,NULL,NULL,NULL),(2,1,NULL,1,'Grid Box 01','gridBox',4,'Test Comment!',NULL,0,NULL,2,NULL),(3,1,NULL,NULL,'Container 02','falconTube',NULL,NULL,NULL,0,NULL,NULL,NULL),(4,1,NULL,NULL,'Grid Box 02','gridBox',4,NULL,NULL,0,NULL,NULL,NULL),(5,1,NULL,NULL,'Grid Box 03','gridBox',4,NULL,NULL,0,NULL,NULL,NULL),(341,89,61,NULL,'Container 03','puck',NULL,NULL,NULL,0,10,NULL,NULL),(474,89,61,NULL,'Container 04','puck',NULL,NULL,NULL,0,15,NULL,NULL),(559,89,NULL,474,'Grid Box 04','gridBox',4,NULL,NULL,0,5,2,NULL);
/*!40000 ALTER TABLE `Container` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Sample`
--

DROP TABLE IF EXISTS `Sample`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Sample` (
  `sampleId` int(11) NOT NULL AUTO_INCREMENT,
  `shipmentId` int(11) NOT NULL,
  `proteinId` int(11) NOT NULL,
  `type` varchar(40) NOT NULL DEFAULT 'sample',
  `name` varchar(40) NOT NULL,
  `location` smallint(6) DEFAULT NULL,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Generic additional details' CHECK (json_valid(`details`)),
  `containerId` int(11) DEFAULT NULL,
  `externalId` int(11) DEFAULT NULL,
  `comments` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`sampleId`),
  UNIQUE KEY `externalId` (`externalId`),
  KEY `ix_Sample_shipmentId` (`shipmentId`),
  KEY `ix_Sample_containerId` (`containerId`),
  KEY `ix_Sample_sampleId` (`sampleId`),
  CONSTRAINT `Sample_ibfk_1` FOREIGN KEY (`shipmentId`) REFERENCES `Shipment` (`shipmentId`),
  CONSTRAINT `Sample_ibfk_2` FOREIGN KEY (`containerId`) REFERENCES `Container` (`containerId`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=699 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Sample`
--

LOCK TABLES `Sample` WRITE;
/*!40000 ALTER TABLE `Sample` DISABLE KEYS */;
INSERT INTO `Sample` VALUES (1,1,4407,'sample','Sample 01',1,'{\"details\": null, \"shipmentId\": 1, \"foil\": \"Quantifoil copper\", \"film\": \"Holey carbon\", \"mesh\": \"200\", \"hole\": \"R 0.6/1\", \"vitrification\": \"GP2\"}',2,NULL,NULL),(3,1,4407,'sample','Sample 03',1,'{\"details\": null, \"shipmentId\": 1, \"foil\": \"Quantifoil copper\", \"film\": \"Holey carbon\", \"mesh\": \"200\", \"hole\": \"R 0.6/1\", \"vitrification\": \"GP2\"}',4,NULL,NULL),(336,89,4407,'sample','Sample 04',NULL,NULL,341,10,NULL),(557,1,4380,'grid','Protein 01 4',NULL,'{\"buffer\": \"\", \"concentration\": \"\", \"foil\": \"Quantifoil copper\", \"film\": \"Holey carbon\", \"mesh\": \"200\", \"hole\": \"R 0.6/1\", \"vitrification\": \"GP2\", \"vitrificationConditions\": \"\", \"clipped\": false}',NULL,NULL,NULL);
/*!40000 ALTER TABLE `Sample` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Shipment`
--

DROP TABLE IF EXISTS `Shipment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Shipment` (
  `shipmentId` int(11) NOT NULL AUTO_INCREMENT,
  `proposalReference` varchar(10) NOT NULL,
  `name` varchar(40) NOT NULL,
  `comments` varchar(255) DEFAULT NULL,
  `creationDate` datetime NOT NULL DEFAULT current_timestamp(),
  `externalId` int(11) DEFAULT NULL,
  `shipmentRequest` int(11) DEFAULT NULL,
  `status` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`shipmentId`),
  UNIQUE KEY `externalId` (`externalId`),
  KEY `ix_Shipment_proposalReference` (`proposalReference`),
  KEY `ix_Shipment_shipmentId` (`shipmentId`)
) ENGINE=InnoDB AUTO_INCREMENT=189 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Shipment`
--

LOCK TABLES `Shipment` WRITE;
/*!40000 ALTER TABLE `Shipment` DISABLE KEYS */;
INSERT INTO `Shipment` VALUES (1,'cm00001','Shipment 01',NULL,'2023-08-21 08:16:56',NULL,NULL,''),(2,'cm00002','Shipment 02',NULL,'2023-08-22 14:21:43',123,NULL,NULL),(89,'cm00003','Shipment 03',NULL,'2024-01-05 15:12:44',256,NULL,'Booked');
/*!40000 ALTER TABLE `Shipment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TopLevelContainer`
--

DROP TABLE IF EXISTS `TopLevelContainer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TopLevelContainer` (
  `topLevelContainerId` int(11) NOT NULL AUTO_INCREMENT,
  `shipmentId` int(11) NOT NULL,
  `name` varchar(40) NOT NULL,
  `comments` varchar(255) DEFAULT NULL,
  `code` varchar(20) NOT NULL,
  `barCode` varchar(20) DEFAULT NULL,
  `type` enum('dewar','toolbox','parcel') NOT NULL,
  `externalId` int(11) DEFAULT NULL,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (`topLevelContainerId`),
  UNIQUE KEY `externalId` (`externalId`),
  KEY `ix_TopLevelContainer_shipmentId` (`shipmentId`),
  KEY `ix_TopLevelContainer_topLevelContainerId` (`topLevelContainerId`),
  CONSTRAINT `TopLevelContainer_ibfk_1` FOREIGN KEY (`shipmentId`) REFERENCES `Shipment` (`shipmentId`)
) ENGINE=InnoDB AUTO_INCREMENT=262 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TopLevelContainer`
--

LOCK TABLES `TopLevelContainer` WRITE;
/*!40000 ALTER TABLE `TopLevelContainer` DISABLE KEYS */;
INSERT INTO `TopLevelContainer` VALUES (1,1,'Dewar 01',NULL,'DLS-1','DLS-1','dewar',NULL,'{}'),(2,2,'Dewar 02',NULL,'DLS-2','DLS-2','dewar',NULL,'{}'),(3,2,'Dewar 03',NULL,'DLS-3','DLS-3','dewar',NULL,'{}'),(61,89,'Dewar 04',NULL,'DLS-4','DLS-4','dewar',10,NULL);
/*!40000 ALTER TABLE `TopLevelContainer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('4c06e878da70');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'sample_handling'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-12 14:35:16
