
-- Needed for GRDB Version 1.1.0 and higher

ALTER TABLE `job`
	ADD COLUMN `new_status` VARCHAR(255) NOT NULL COLLATE 'utf8mb4_general_ci' AFTER `exceptions`,
	ADD COLUMN `wait_starttime` DATETIME(6) NULL DEFAULT NULL AFTER `new_status`,
	ADD COLUMN `wait_endtime` DATETIME(6) NULL DEFAULT NULL AFTER `wait_starttime`,
	ADD COLUMN `wait_processtime` TIME NULL DEFAULT NULL AFTER `wait_endtime`,
	ADD COLUMN `job_starttime` DATETIME(6) NULL DEFAULT NULL AFTER `wait_processtime`,
	ADD COLUMN `job_endtime` DATETIME(6) NULL DEFAULT NULL AFTER `job_starttime`,
	ADD COLUMN `job_processtime` TIME NULL DEFAULT NULL AFTER `job_endtime`,
	ADD COLUMN `app_version` VARCHAR(20) NULL DEFAULT NULL AFTER `job_processtime`,
	ADD COLUMN `wait_job_id` INT NULL DEFAULT NULL AFTER `app_version`;

-- This index makes GRDB data loading from gen_Location 300 times faster

CREATE INDEX IX_genLocation_iStatus_cActive_cOceanlocation ON gen_Location (iStatus, cActive, cOceanlocation);