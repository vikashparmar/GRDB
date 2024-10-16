-- Update constraints of column
ALTER TABLE grdb_Job modify cFileFormat enum('HORIZONTALACCURATE','HORIZONTALONLINE','VERTICAL','JSON') COLLATE ascii_bin DEFAULT NULL;

-- Add index for locking rate API
CREATE INDEX IDX_GET_LOCKING_RATE ON grdb_Job(cCustomerName, cSheetType, cFileType, cOriginalFilename, iFileSize, tCreated, cUserName, cFilePath, cErrorLogFilepath, cStatus);
