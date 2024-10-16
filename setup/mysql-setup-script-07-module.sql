
-- Needed for GRDB Version 1.7 and higher


-- For Job table 

ALTER TABLE grdb_Job ADD COLUMN cFileFormat enum('HORIZONTALACCURATE','HORIZONTALONLINE','VERTICAL') COLLATE ascii_bin DEFAULT NULL;

ALTER TABLE grdb_Job ADD COLUMN cUserType enum('WO','WE','WS') COLLATE ascii_bin DEFAULT NULL;
  
ALTER TABLE grdb_Job ADD COLUMN iStatus int(11) DEFAULT 0;

ALTER TABLE grdb_Job ADD COLUMN iPriority int(11) DEFAULT NULL;

ALTER TABLE `gen_User` ADD `cRequestID` VARCHAR(255) DEFAULT NULL;


-- For grdb_exported_header_log table

ALTER TABLE grdb_exported_header_log ALTER cOption1 SET DEFAULT '';

ALTER TABLE grdb_exported_header_log ALTER cOption2 SET DEFAULT '';

ALTER TABLE grdb_exported_header_log ALTER cOption3 SET DEFAULT '';