
-- Needed for GRDB Version 1.7 and higher

CREATE TABLE `grdb_API_requestLogs` (
	`iApiLogID` INT(11) NULL DEFAULT NULL,
	`cUserIP` VARCHAR(255) NULL DEFAULT NULL,
	`cJobInputFilepath` VARCHAR(255) NULL DEFAULT NULL,
	`iJobID` INT(11) NULL DEFAULT NULL,
	`cAuthToken` VARCHAR(255) NULL DEFAULT NULL,
	`cApiURL` VARCHAR(255) NULL DEFAULT NULL,
	`tRequestDate` DATETIME NULL DEFAULT NULL,
	`iRequestLength` INT(11) NULL DEFAULT NULL,
	`cRequestValid` VARCHAR(255) NULL DEFAULT NULL,
	`iResponseLength` INT(11) NULL DEFAULT NULL,
	`iProcessError` INT(11) NULL DEFAULT NULL,
	`tProcessDuration` TIME NULL DEFAULT NULL,
	`iStatus` INT(11) NULL DEFAULT NULL,
	`iEnteredBy` INT(11) NULL DEFAULT NULL,
	`tEntered` DATETIME NULL DEFAULT NULL,
	`iUpdatedBy` INT(11) NULL DEFAULT NULL,
	`tUpdated` DATETIME NULL DEFAULT NULL,
	`iProgramID` INT(11) NULL DEFAULT NULL,
	`cUsername` VARCHAR(255) NULL DEFAULT NULL,
	`iApiURLLength` INT(11) NULL DEFAULT NULL,
	`cRequestBody` VARCHAR(255) NULL DEFAULT NULL,
	`cResponseBody` VARCHAR(255) NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;
