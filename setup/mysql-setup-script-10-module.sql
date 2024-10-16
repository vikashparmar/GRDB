-- For 1.8.1 and higher

-- increase column size limits
ALTER TABLE grdb_FreightOnBoard_Charges_Write MODIFY COLUMN cScaleUOM varchar(10);
ALTER TABLE grdb_OceanFreight_Charges_Write MODIFY COLUMN cScaleUOM varchar(10);
ALTER TABLE grdb_Postlanding_Charges_Write MODIFY COLUMN cScaleUOM varchar(10);

-- change error data to binary to stored compressed data
ALTER TABLE `grdb_Job`
	CHANGE COLUMN `cValidateErrors` `cValidateErrors` LONGBLOB NULL AFTER `cRequestID`,
	CHANGE COLUMN `cValidateWarnings` `cValidateWarnings` LONGBLOB NULL AFTER `cValidateErrors`;

-- add indexing on job table
CREATE INDEX IDX_ISTATUS ON grdb_Job (iStatus);
CREATE INDEX IDX_IPRIORITY ON grdb_Job (iPriority);
CREATE INDEX IDX_JOBID_IPRIORITY ON grdb_Job (iJobID, iPriority);
CREATE INDEX IDX_JOBID_ISTATUS ON grdb_Job (iJobID, iStatus);