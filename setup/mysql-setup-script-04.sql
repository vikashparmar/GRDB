
-- Needed for GRDB Version 1.2.1 and higher

ALTER TABLE `grdb_Gen_UserAuthToken`
DROP CONSTRAINT `CX_UAT_ibfk_1`;

DROP TABLE `grdb_Rules`;