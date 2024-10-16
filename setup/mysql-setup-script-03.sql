
-- Needed for GRDB Version 1.1.2 and higher



-- Rename old tables so that newer tables can be created without conflicts

ALTER TABLE `auth_token` RENAME `grdb_Old_auth_token`;
ALTER TABLE `error_log` RENAME `grdb_Old_error_log`;
ALTER TABLE `job` RENAME `grdb_Old_job`;
ALTER TABLE `resources` RENAME `grdb_Old_resources`;
ALTER TABLE `rules` RENAME `grdb_Old_rules`;
ALTER TABLE `user_auth_token` RENAME `grdb_Old_user_auth_token`;




-- For following tables only the table names and column names are changed according to client standards

-- previous table: auth_token
CREATE TABLE `grdb_Gen_AuthToken` (
	`iAuthTokenID` INT(10) NOT NULL AUTO_INCREMENT,
	`cToken` VARCHAR(100) NULL DEFAULT NULL,
	`tCreated` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`iAuthTokenID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;


-- previous table: user_auth_token
CREATE TABLE `grdb_Gen_UserAuthToken` (
	`iUATID` INT(10) NOT NULL AUTO_INCREMENT,
	`cUserName` VARCHAR(100) NULL DEFAULT NULL,
	`iAuthTokenID` INT(10) NULL DEFAULT NULL,
	PRIMARY KEY (`iUATID`) USING BTREE,
	INDEX `IX_UAT_iAuthTokenID` (`iAuthTokenID`) USING BTREE,
	CONSTRAINT `CX_UAT_ibfk_1` FOREIGN KEY (`iAuthTokenID`) REFERENCES `grdb`.`grdb_Gen_AuthToken` (`iAuthTokenID`) ON UPDATE NO ACTION ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;


-- previous table: error_log
CREATE TABLE `tra_Error_Log` (
	`iErrorLogID` INT(10) NOT NULL AUTO_INCREMENT,
	`iTestID` INT(10) NOT NULL,
	`iJobID` INT(10) NOT NULL,
	`cFileType` VARCHAR(45) NOT NULL,
	`cSpreadsheetName` VARCHAR(45) NOT NULL,
	`cFileName` VARCHAR(200) NOT NULL,
	`iErrorRowCount` INT(10) NOT NULL,
	`cComment` TEXT NOT NULL,
	`cLink` VARCHAR(200) NOT NULL,
	`tProcessStart` DATETIME(6) NOT NULL,
	`tProcessEnd` DATETIME(6) NOT NULL,
	`tUpdated` DATETIME(6) NOT NULL,
	`cWarnings` VARCHAR(500) NULL DEFAULT NULL,
	PRIMARY KEY (`iErrorLogID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;

-- only some cols need to be UTF8, remaining columns can be ASCII
ALTER TABLE tra_Error_Log
MODIFY cWarnings TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
ALTER TABLE tra_Error_Log
MODIFY cComment TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;




-- previous table: job
CREATE TABLE `grdb_Job` (
	`iJobID` INT(10) NOT NULL AUTO_INCREMENT,
	`cAppVersion` VARCHAR(20) NULL DEFAULT NULL,
	`cUserName` VARCHAR(255) NOT NULL,
	`cStatus` VARCHAR(255) NOT NULL,
	`cOldStatus` VARCHAR(255) NOT NULL,
	`cProcessStatus` VARCHAR(45) NULL DEFAULT NULL,
	`cDataInserted` ENUM('Y','N','E') NULL DEFAULT 'N',
	`cSource` VARCHAR(255) NOT NULL,
	`cFilePath` VARCHAR(255) NOT NULL,
	`cFileName` VARCHAR(225) NULL DEFAULT NULL,
	`cSheetType` VARCHAR(255) NULL DEFAULT NULL,
	`cFileType` VARCHAR(45) NULL DEFAULT NULL,
	`cOriginalFilename` VARCHAR(255) NULL DEFAULT NULL,
	`cCustomerName` VARCHAR(255) NOT NULL,
	`cMemberCode` VARCHAR(255) NULL DEFAULT NULL,
	`tCreated` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
	`tLastUpdated` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
	`iFileSize` BIGINT(19) NULL DEFAULT NULL,
	`iTotalRowCount` INT(10) NULL DEFAULT NULL,
	`iErrorRowCount` INT(10) NULL DEFAULT NULL,
	`iValidatedRowCount` INT(10) NULL DEFAULT NULL,
	`cErrorLogFilepath` VARCHAR(255) NULL DEFAULT NULL,
	`cCorrectLogFilepath` VARCHAR(255) NULL DEFAULT NULL,
	`tJobStart` DATETIME(6) NULL DEFAULT NULL,
	`tJobEnd` DATETIME(6) NULL DEFAULT NULL,
	`tJobDuration` TIME NULL DEFAULT NULL,
	`tFormatValStart` DATETIME(6) NULL DEFAULT NULL,
	`tFormatValEnd` DATETIME(6) NULL DEFAULT NULL,
	`tFormatValDuration` TIME NULL DEFAULT NULL,
	`tValidateStart` DATETIME(6) NULL DEFAULT NULL,
	`tValidateEnd` DATETIME(6) NULL DEFAULT NULL,
	`tValidateDuration` TIME NULL DEFAULT NULL,
	`tWaitStart` DATETIME(6) NULL DEFAULT NULL,
	`tWaitEnd` DATETIME(6) NULL DEFAULT NULL,
	`tWaitDuration` TIME NULL DEFAULT NULL,
	`iWaitJobID` INT(10) NULL DEFAULT NULL,
	`tInsertStart` DATETIME(6) NULL DEFAULT NULL,
	`tInsertEnd` DATETIME(6) NULL DEFAULT NULL,
	`tInsertDuration` TIME NULL DEFAULT NULL,
	`cExceptions` VARCHAR(500) NULL DEFAULT NULL,
	PRIMARY KEY (`iJobID`) USING BTREE,
	INDEX `IX_Job_cFilePath` (`cFilePath`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;

-- only some cols need to be UTF8, remaining columns can be ASCII
ALTER TABLE grdb_Job
MODIFY cExceptions TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;




-- previous table: resources
CREATE TABLE `grdb_Resources` (
	`iResourceID` INT(10) NOT NULL AUTO_INCREMENT,
	`cModule` VARCHAR(100) NULL DEFAULT NULL,
	`cType` VARCHAR(100) NULL DEFAULT NULL,
	`cResourceName` VARCHAR(100) NULL DEFAULT NULL,
	`tCreated` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`iResourceID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;


-- previous table: rules
CREATE TABLE `grdb_Rules` (
	`iRuleID` INT(10) NOT NULL AUTO_INCREMENT,
	`cRuleName` VARCHAR(100) NOT NULL,
	`cRuleDescription` VARCHAR(2000) NOT NULL,
	`cRuleFor` VARCHAR(100) NOT NULL,
	`cTableName` VARCHAR(100) NULL DEFAULT NULL,
	`cTableColNames` VARCHAR(250) NULL DEFAULT NULL,
	`cSheetColName` TEXT NULL DEFAULT NULL,
	`cValType` ENUM('BASIC_VAL','DB_VAL') NULL DEFAULT 'BASIC_VAL',
	PRIMARY KEY (`iRuleID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;
