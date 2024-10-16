-- keep the count of number of job retries
ALTER TABLE grdb_Job ADD iRetriesCount INTEGER DEFAULT 0;

-- add indexing on job table
CREATE INDEX IDX_FILENAME_DATEMODIFIED ON grdb.grdb_Job(cOriginalFilename,tOriginalDateModified);

-- changed column contraint to primary key
ALTER TABLE grdb.grdb_API_requestLogs modify iApiLogID INT PRIMARY KEY AUTO_INCREMENT;

