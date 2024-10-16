
-- Needed for GRDB Version 1.7 and higher

ALTER TABLE grdb.grdb_Job MODIFY cValidateErrors LONGTEXT;

ALTER TABLE grdb.grdb_Job MODIFY cValidateWarnings LONGTEXT;