
-- Needed for GRDB Version 1.6 and higher

ALTER TABLE `grdb_Job`
	ADD COLUMN `cPodName` VARCHAR(255) NULL DEFAULT NULL COLLATE 'ascii_bin' AFTER `cExceptions`,
	ADD COLUMN `cMessageID` VARCHAR(255) NULL DEFAULT NULL COLLATE 'ascii_bin' AFTER `cPodName`,
	ADD COLUMN `cContainerID` VARCHAR(255) NULL DEFAULT NULL COLLATE 'ascii_bin' AFTER `cMessageID`,
	ADD COLUMN `tHeartbeat` DATETIME NULL DEFAULT NULL AFTER `cContainerID`,
	ADD COLUMN `iMemoryUsed` INT(10) NULL DEFAULT NULL AFTER `tHeartbeat`,
	ADD COLUMN `tOriginalDateModified` DATETIME NULL AFTER `iMemoryUsed`,
	ADD COLUMN `cRequestID` VARCHAR(1000) NULL DEFAULT NULL COLLATE 'ascii_bin' AFTER `tOriginalDateModified`,
	ADD COLUMN `cValidateErrors` TEXT NULL AFTER `cRequestID`,
	ADD COLUMN `cValidateWarnings` TEXT NULL AFTER `cValidateErrors`;

CREATE TABLE IF NOT EXISTS `grdb_Aspect` (
	`iAspectCodeID` INT(10) NOT NULL AUTO_INCREMENT,
	`cAspectCode` VARCHAR(20) NOT NULL COLLATE 'ascii_bin',
	`cAspectDescription` VARCHAR(250) NOT NULL COLLATE 'ascii_bin',
	`iStatus` INT(10) NOT NULL DEFAULT '0',
	`iActive` INT(10) NOT NULL DEFAULT '0',
	`iEnteredby` INT(10) NOT NULL DEFAULT '0',
	`tEntered` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	`iUpdatedby` INT(10) NOT NULL DEFAULT '0',
	`tUpdated` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	PRIMARY KEY (`iAspectCodeID`) USING BTREE,
	INDEX `idx_aspect_status` (`cAspectCode`, `iStatus`) USING BTREE
)
COLLATE='ascii_bin'
ENGINE=InnoDB
AUTO_INCREMENT=7
;

CREATE TABLE IF NOT EXISTS `grdb_Pod` (
	`cPodName` VARCHAR(255) NOT NULL COLLATE 'ascii_bin',
	`cNodeId` VARCHAR(255) NULL DEFAULT NULL COLLATE 'ascii_bin',
	`cIP` VARCHAR(255) NULL DEFAULT NULL COLLATE 'ascii_bin',
	`cPodStatus` VARCHAR(255) NULL DEFAULT NULL COLLATE 'ascii_bin',
	`tAge` VARCHAR(255) NULL DEFAULT NULL COLLATE 'ascii_bin',
	`cAction` VARCHAR(255) NULL DEFAULT NULL COLLATE 'ascii_bin',
	PRIMARY KEY (`cPodName`) USING BTREE
)
COLLATE='ascii_bin'
ENGINE=InnoDB
;


-- Fixes for MariaDB

ALTER TABLE `grdb_Job`
	CHANGE COLUMN `cOldStatus` `cOldStatus` VARCHAR(255) NULL COLLATE 'ascii_bin' AFTER `cStatus`,
	CHANGE COLUMN `cCustomerName` `cCustomerName` VARCHAR(255) NULL COLLATE 'ascii_bin' AFTER `cOriginalFilename`;
	
ALTER TABLE `grdb_Job`
	CHANGE COLUMN `cFilePath` `cFilePath` VARCHAR(255) NULL COLLATE 'ascii_bin' AFTER `cSource`;

ALTER TABLE `tra_Error_Log`
	CHANGE COLUMN `iTestID` `iTestID` INT(11) NULL AFTER `iErrorLogID`;

ALTER TABLE grdb_Postlanding_Charges_Write
	MODIFY cChargename varchar(100);

ALTER TABLE grdb_OceanFreight_Charges_Write
	MODIFY cChargename varchar(100);

ALTER TABLE grdb_FreightOnBoard_Charges_Write
	MODIFY cChargename varchar(100);

ALTER TABLE grdb_Postlanding_Charges_History
	MODIFY cChargename varchar(100);

ALTER TABLE grdb_OceanFreight_Charges_History
	MODIFY cChargename varchar(100);

ALTER TABLE grdb_FreightOnBoard_Charges_History
	MODIFY cChargename varchar(100);