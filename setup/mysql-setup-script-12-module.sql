-- remove unused column
ALTER TABLE grdb.grdb_Job DROP COLUMN iMemoryUsed;
ALTER TABLE grdb.grdb_Job DROP COLUMN cMessageID;

-- Origin and Destination e.g. USNYC_INAMD 
ALTER TABLE grdb_Job ADD cPortPair VARCHAR(255) NULL DEFAULT NULL;

-- add indexing on job table
CREATE INDEX IDX_PORT_PAIR ON grdb_Job(cPortPair);

-- delete table
DROP TABLE grdb_Gen_AuthToken;

-- delete all records
TRUNCATE grdb_Gen_UserAuthToken;

-- Make column changes
ALTER TABLE grdb_Gen_UserAuthToken
	DROP COLUMN `iAuthTokenID`,
    ADD COLUMN `cToken` VARCHAR(100) NULL DEFAULT NULL,
    ADD COLUMN `tCreated` DATETIME NULL DEFAULT CURRENT_TIMESTAMP;