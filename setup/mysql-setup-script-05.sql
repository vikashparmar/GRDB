
-- Needed for GRDB Version 1.2.0 and higher


DROP TABLE `grdb_Rules`


-- WGP-245: New GRDB insertion tables

CREATE TABLE IF NOT EXISTS `grdb_OceanFreight_Charges_History` (
	`iOFRchargeHistoryID` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
	`iOceanFreightID` BIGINT(20) UNSIGNED NOT NULL DEFAULT '0',
	`iUploadlogID` BIGINT(20) NOT NULL DEFAULT '0',
	`cCustomeralias` VARCHAR(20) NOT NULL DEFAULT '',
	`cScaccode` VARCHAR(20) NOT NULL DEFAULT '',
	`cCurrency` VARCHAR(20) NOT NULL DEFAULT '',
	`cChargecode` VARCHAR(20) NOT NULL DEFAULT '',
	`cChargename` VARCHAR(20) NOT NULL DEFAULT '',
	`cAspect` VARCHAR(20) NOT NULL DEFAULT '',
	`iRate` DOUBLE NOT NULL DEFAULT '0',
	`cRatebasis` VARCHAR(20) NOT NULL DEFAULT '',
	`iMinimum` DECIMAL(10,3) NOT NULL DEFAULT '0.000',
	`iMaximum` DECIMAL(10,3) NOT NULL DEFAULT '0.000',
	`cScaleUOM` CHAR(2) NOT NULL DEFAULT '',
	`cFrom` VARCHAR(20) NOT NULL DEFAULT '',
	`cTo` VARCHAR(20) NULL DEFAULT '',
	`cNotes` TEXT NULL COLLATE utf8mb4_general_ci,
	`tEffectivedate` DATE NOT NULL DEFAULT '0000-00-00',
	`tExpirationdate` DATE NOT NULL DEFAULT '0000-00-00',
	`cConditional` CHAR(1) NOT NULL DEFAULT '',
	`iExportID` BIGINT(20) NOT NULL DEFAULT '0',
	`cVisible` ENUM('Y','N') NULL DEFAULT 'Y',
	`iStatus` INT(11) NOT NULL DEFAULT '0',
	`iActive` INT(4) NOT NULL DEFAULT '0',
	`iEnteredby` INT(11) NOT NULL DEFAULT '0',
	`tEntered` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	`iUpdatedby` INT(11) NOT NULL DEFAULT '0',
	`tUpdated` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	PRIMARY KEY (`iOFRchargeHistoryID`) USING BTREE,
	INDEX `IX_OFRCharge_iOceanFreightID` (`iActive`, `iOceanFreightID`) USING BTREE,
	INDEX `IX_OFRCharge_iStatus_iUploadlogID` (`iStatus`, `iUploadlogID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;


-- only cNotes needs to be UTF8, remaining columns can be ASCII
ALTER TABLE grdb_OceanFreight_Charges_History
MODIFY cNotes TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;




CREATE TABLE IF NOT EXISTS `grdb_OceanFreight_Charges_Write` (
	`iOFRchargeID` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
	`iUploadlogID` BIGINT(20) NOT NULL DEFAULT '0',
	`cCustomeralias` VARCHAR(20) NOT NULL DEFAULT '',
	`cScaccode` VARCHAR(20) NOT NULL DEFAULT '',
	`iOceanFreightID` BIGINT(20) UNSIGNED NOT NULL DEFAULT '0',
	`cCurrency` VARCHAR(20) NOT NULL DEFAULT '',
	`cChargecode` VARCHAR(20) NOT NULL DEFAULT '',
	`cChargename` VARCHAR(20) NOT NULL DEFAULT '',
	`cAspect` VARCHAR(20) NOT NULL DEFAULT '',
	`iRate` DOUBLE NOT NULL DEFAULT '0',
	`cRatebasis` VARCHAR(20) NOT NULL DEFAULT '',
	`iMinimum` DECIMAL(10,3) NOT NULL DEFAULT '0.000',
	`iMaximum` DECIMAL(10,3) NOT NULL DEFAULT '0.000',
	`cScaleUOM` CHAR(2) NOT NULL DEFAULT '',
	`cFrom` VARCHAR(20) NOT NULL DEFAULT '',
	`cTo` VARCHAR(20) NULL DEFAULT '',
	`cNotes` TEXT NULL,
	`tEffectivedate` DATE NOT NULL DEFAULT '0000-00-00',
	`tExpirationdate` DATE NOT NULL DEFAULT '0000-00-00',
	`cConditional` CHAR(1) NOT NULL DEFAULT '',
	`cVisible` ENUM('Y','N') NULL DEFAULT 'Y',
	`iStatus` INT(11) NOT NULL DEFAULT '0',
	`iActive` INT(4) NOT NULL DEFAULT '0',
	`iEnteredby` INT(11) NOT NULL DEFAULT '0',
	`tEntered` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	`iUpdatedby` INT(11) NOT NULL DEFAULT '0',
	`tUpdated` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',	
	PRIMARY KEY (`iOFRchargeID`) USING BTREE,
	INDEX `IX_OFRCharge_iActive` (`iActive`) USING BTREE,
	INDEX `IX_OFRCharge_iStatus_iUploadlogID` (`iStatus`, `iUploadlogID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;


-- only cNotes needs to be UTF8, remaining columns can be ASCII
ALTER TABLE grdb_OceanFreight_Charges_Write
MODIFY cNotes TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;





CREATE TABLE IF NOT EXISTS `grdb_OceanFreight_Write` (
	`iOceanFreightID` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`iUploadlogID` BIGINT(20) NOT NULL DEFAULT '0',
	`cCustomeralias` VARCHAR(30) NOT NULL DEFAULT '',
	`cScaccode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginRegioncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginCountrycode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginCFSUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginConsoleCFSUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginPortUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cTransshipment_1` VARCHAR(20) NOT NULL DEFAULT '',
	`cTransshipment_2` VARCHAR(20) NOT NULL DEFAULT '',
	`cTransshipment_3` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationRegioncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationCountrycode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationCFSUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationDeconsoleCFSUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationPortUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cQuotingregion` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cQuotingMember` VARCHAR(30) NOT NULL DEFAULT '',
	`cRoutingkey` VARCHAR(100) NOT NULL DEFAULT '',
	`iStatus` INT(11) NOT NULL DEFAULT '0',
	`iActive` INT(4) NOT NULL DEFAULT '0',
	`iEnteredby` INT(11) NOT NULL DEFAULT '0',
	`tEntered` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	`iUpdatedby` INT(11) NOT NULL DEFAULT '0',
	`tUpdated` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	PRIMARY KEY (`iOceanFreightID`) USING BTREE,
	INDEX `IX_OFR_iActive` (`iActive`) USING BTREE,
	INDEX `IX_OFR_iStatus` (`iStatus`, `iUploadlogID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;




CREATE TABLE IF NOT EXISTS `grdb_Postlanding_Charges_History` (
	`iPLCchargeHistoryID` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
	`iPostlandingID` BIGINT(20) UNSIGNED NOT NULL DEFAULT '0',
	`iUploadlogID` BIGINT(20) NOT NULL DEFAULT '0',
	`cCustomeralias` VARCHAR(20) NOT NULL DEFAULT '',
	`cScaccode` VARCHAR(20) NOT NULL DEFAULT '',
	`cCurrency` VARCHAR(20) NOT NULL DEFAULT '',
	`cChargecode` VARCHAR(20) NOT NULL DEFAULT '',
	`cChargename` VARCHAR(20) NOT NULL DEFAULT '',
	`cAspect` VARCHAR(20) NOT NULL DEFAULT '',
	`iRate` DOUBLE NOT NULL DEFAULT '0',
	`cRatebasis` VARCHAR(20) NOT NULL DEFAULT '',
	`iMinimum` DECIMAL(10,3) NOT NULL DEFAULT '0.000',
	`iMaximum` DECIMAL(10,3) NOT NULL DEFAULT '0.000',
	`cScaleUOM` CHAR(2) NOT NULL DEFAULT '',
	`cFrom` VARCHAR(20) NOT NULL DEFAULT '',
	`cTo` VARCHAR(20) NULL DEFAULT '',
	`cNotes` TEXT NULL,
	`tEffectivedate` DATE NOT NULL DEFAULT '0000-00-00',
	`tExpirationdate` DATE NOT NULL DEFAULT '0000-00-00',
	`cConditional` CHAR(1) NOT NULL DEFAULT '',
	`iExportID` BIGINT(20) NOT NULL DEFAULT '0',
	`cVisible` ENUM('Y','N') NULL DEFAULT 'Y',
	`iStatus` INT(11) NOT NULL DEFAULT '0',
	`iActive` INT(4) NOT NULL DEFAULT '0',
	`iEnteredby` INT(11) NOT NULL DEFAULT '0',
	`tEntered` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	`iUpdatedby` INT(11) NOT NULL DEFAULT '0',
	`tUpdated` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	PRIMARY KEY (`iPLCchargeHistoryID`) USING BTREE,
	INDEX `IX_OFRCharge_iPostlandingID` (`iActive`, `iPostlandingID`) USING BTREE,
	INDEX `IX_OFRCharge_iStatus_iUploadlogID` (`iStatus`, `iUploadlogID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;


-- only cNotes needs to be UTF8, remaining columns can be ASCII
ALTER TABLE grdb_Postlanding_Charges_History
MODIFY cNotes TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;




CREATE TABLE IF NOT EXISTS `grdb_Postlanding_Charges_Write` (
	`iPLCchargeID` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
	`iUploadlogID` BIGINT(20) NOT NULL DEFAULT '0',
	`cCustomeralias` VARCHAR(20) NOT NULL DEFAULT '',
	`cScaccode` VARCHAR(20) NOT NULL DEFAULT '',
	`iPostlandingID` BIGINT(20) UNSIGNED NOT NULL DEFAULT '0',
	`cCurrency` VARCHAR(20) NOT NULL DEFAULT '',
	`cChargecode` VARCHAR(20) NOT NULL DEFAULT '',
	`cChargename` VARCHAR(20) NOT NULL DEFAULT '',
	`cAspect` VARCHAR(20) NOT NULL DEFAULT '',
	`iRate` DOUBLE NOT NULL DEFAULT '0',
	`cRatebasis` VARCHAR(20) NOT NULL DEFAULT '',
	`iMinimum` DECIMAL(10,3) NOT NULL DEFAULT '0.000',
	`iMaximum` DECIMAL(10,3) NOT NULL DEFAULT '0.000',
	`cScaleUOM` CHAR(2) NOT NULL DEFAULT '',
	`cFrom` VARCHAR(20) NOT NULL DEFAULT '',
	`cTo` VARCHAR(20) NULL DEFAULT '',
	`cNotes` TEXT NULL,
	`tEffectivedate` DATE NOT NULL DEFAULT '0000-00-00',
	`tExpirationdate` DATE NOT NULL DEFAULT '0000-00-00',
	`cConditional` CHAR(1) NOT NULL DEFAULT '',
	`cVisible` ENUM('Y','N') NULL DEFAULT 'Y',
	`iStatus` INT(11) NOT NULL DEFAULT '0',
	`iActive` INT(4) NOT NULL DEFAULT '0',
	`iEnteredby` INT(11) NOT NULL DEFAULT '0',
	`tEntered` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	`iUpdatedby` INT(11) NOT NULL DEFAULT '0',
	`tUpdated` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',	
	PRIMARY KEY (`iPLCchargeID`) USING BTREE,
	INDEX `IX_OFRCharge_iActive` (`iActive`) USING BTREE,
	INDEX `IX_OFRCharge_iStatus_iUploadlogID` (`iStatus`, `iUploadlogID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;


-- only cNotes needs to be UTF8, remaining columns can be ASCII
ALTER TABLE grdb_Postlanding_Charges_Write
MODIFY cNotes TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;





CREATE TABLE IF NOT EXISTS `grdb_Postlanding_Write` (
    `iPostlandingID` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`iUploadlogID` BIGINT(20) NOT NULL DEFAULT '0',
	`cCustomeralias` VARCHAR(30) NOT NULL DEFAULT '',
	`cScaccode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginRegioncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginCountrycode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginCFSUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginConsoleCFSUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginPortUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cTransshipment_1` VARCHAR(20) NOT NULL DEFAULT '',
	`cTransshipment_2` VARCHAR(20) NOT NULL DEFAULT '',
	`cTransshipment_3` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationRegioncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationCountrycode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationCFSUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationDeconsoleCFSUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationPortUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cQuotingregion` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cQuotingMember` VARCHAR(30) NOT NULL DEFAULT '',
	`cRoutingkey` VARCHAR(100) NOT NULL DEFAULT '',
	`iStatus` INT(11) NOT NULL DEFAULT '0',
	`iActive` INT(4) NOT NULL DEFAULT '0',
	`iEnteredby` INT(11) NOT NULL DEFAULT '0',
	`tEntered` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	`iUpdatedby` INT(11) NOT NULL DEFAULT '0',
	`tUpdated` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	PRIMARY KEY (`iPostlandingID`) USING BTREE,
	INDEX `IX_OFR_iActive` (`iActive`) USING BTREE,
	INDEX `IX_OFR_iStatus` (`iStatus`, `iUploadlogID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;




CREATE TABLE IF NOT EXISTS `grdb_FreightOnBoard_Charges_History` (
  	`iFOBChargeHistoryID` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
	`iFreightOnBoardID` BIGINT(20) UNSIGNED NOT NULL DEFAULT '0',
	`iUploadlogID` BIGINT(20) NOT NULL DEFAULT '0',
	`cCustomeralias` VARCHAR(20) NOT NULL DEFAULT '',
	`cScaccode` VARCHAR(20) NOT NULL DEFAULT '',
	`cCurrency` VARCHAR(20) NOT NULL DEFAULT '',
	`cChargecode` VARCHAR(20) NOT NULL DEFAULT '',
	`cChargename` VARCHAR(20) NOT NULL DEFAULT '',
	`cAspect` VARCHAR(20) NOT NULL DEFAULT '',
	`iRate` DOUBLE NOT NULL DEFAULT '0',
	`cRatebasis` VARCHAR(20) NOT NULL DEFAULT '',
	`iMinimum` DECIMAL(10,3) NOT NULL DEFAULT '0.000',
	`iMaximum` DECIMAL(10,3) NOT NULL DEFAULT '0.000',
	`cScaleUOM` CHAR(2) NOT NULL DEFAULT '',
	`cFrom` VARCHAR(20) NOT NULL DEFAULT '',
	`cTo` VARCHAR(20) NULL DEFAULT '',
	`cNotes` TEXT NULL,
	`tEffectivedate` DATE NOT NULL DEFAULT '0000-00-00',
	`tExpirationdate` DATE NOT NULL DEFAULT '0000-00-00',
	`cConditional` CHAR(1) NOT NULL DEFAULT '',
	`iExportID` BIGINT(20) NOT NULL DEFAULT '0',
	`cVisible` ENUM('Y','N') NULL DEFAULT 'Y',
	`iStatus` INT(11) NOT NULL DEFAULT '0',
	`iActive` INT(4) NOT NULL DEFAULT '0',
	`iEnteredby` INT(11) NOT NULL DEFAULT '0',
	`tEntered` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	`iUpdatedby` INT(11) NOT NULL DEFAULT '0',
	`tUpdated` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	PRIMARY KEY (`iFOBChargeHistoryID`) USING BTREE,
	INDEX `IX_OFRCharge_iFreightOnBoardID` (`iActive`, `iFreightOnBoardID`) USING BTREE,
	INDEX `IX_OFRCharge_iStatus_iUploadlogID` (`iStatus`, `iUploadlogID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;


-- only cNotes needs to be UTF8, remaining columns can be ASCII
ALTER TABLE grdb_FreightOnBoard_Charges_History
MODIFY cNotes TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;




CREATE TABLE IF NOT EXISTS `grdb_FreightOnBoard_Charges_Write` (
  	`iFOBchargeID` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
	`iUploadlogID` BIGINT(20) NOT NULL DEFAULT '0',
	`cCustomeralias` VARCHAR(20) NOT NULL DEFAULT '',
	`cScaccode` VARCHAR(20) NOT NULL DEFAULT '',
	`iFreightOnBoardID` BIGINT(20) UNSIGNED NOT NULL DEFAULT '0',
	`cCurrency` VARCHAR(20) NOT NULL DEFAULT '',
	`cChargecode` VARCHAR(20) NOT NULL DEFAULT '',
	`cChargename` VARCHAR(20) NOT NULL DEFAULT '',
	`cAspect` VARCHAR(20) NOT NULL DEFAULT '',
	`iRate` DOUBLE NOT NULL DEFAULT '0',
	`cRatebasis` VARCHAR(20) NOT NULL DEFAULT '',
	`iMinimum` DECIMAL(10,3) NOT NULL DEFAULT '0.000',
	`iMaximum` DECIMAL(10,3) NOT NULL DEFAULT '0.000',
	`cScaleUOM` CHAR(2) NOT NULL DEFAULT '',
	`cFrom` VARCHAR(20) NOT NULL DEFAULT '',
	`cTo` VARCHAR(20) NULL DEFAULT '',
	`cNotes` TEXT NULL,
	`tEffectivedate` DATE NOT NULL DEFAULT '0000-00-00',
	`tExpirationdate` DATE NOT NULL DEFAULT '0000-00-00',
	`cConditional` CHAR(1) NOT NULL DEFAULT '',
	`cVisible` ENUM('Y','N') NULL DEFAULT 'Y',
	`iStatus` INT(11) NOT NULL DEFAULT '0',
	`iActive` INT(4) NOT NULL DEFAULT '0',
	`iEnteredby` INT(11) NOT NULL DEFAULT '0',
	`tEntered` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	`iUpdatedby` INT(11) NOT NULL DEFAULT '0',
	`tUpdated` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',	
	PRIMARY KEY (`iFOBchargeID`) USING BTREE,
	INDEX `IX_OFRCharge_iActive` (`iActive`) USING BTREE,
	INDEX `IX_OFRCharge_iStatus_iUploadlogID` (`iStatus`, `iUploadlogID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;


-- only cNotes needs to be UTF8, remaining columns can be ASCII
ALTER TABLE grdb_FreightOnBoard_Charges_Write
MODIFY cNotes TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;




CREATE TABLE IF NOT EXISTS `grdb_FreightOnBoard_Write` (
  	`iFreightOnBoardID` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`iUploadlogID` BIGINT(20) NOT NULL DEFAULT '0',
	`cCustomeralias` VARCHAR(30) NOT NULL DEFAULT '',
	`cScaccode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginRegioncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginCountrycode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginCFSUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginConsoleCFSUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginPortUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cTransshipment_1` VARCHAR(20) NOT NULL DEFAULT '',
	`cTransshipment_2` VARCHAR(20) NOT NULL DEFAULT '',
	`cTransshipment_3` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationRegioncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationCountrycode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationCFSUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationDeconsoleCFSUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationPortUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cQuotingregion` VARCHAR(20) NOT NULL DEFAULT '',
	`cOriginUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cDestinationUncode` VARCHAR(20) NOT NULL DEFAULT '',
	`cQuotingMember` VARCHAR(30) NOT NULL DEFAULT '',
	`cRoutingkey` VARCHAR(100) NOT NULL DEFAULT '',
	`iStatus` INT(11) NOT NULL DEFAULT '0',
	`iActive` INT(4) NOT NULL DEFAULT '0',
	`iEnteredby` INT(11) NOT NULL DEFAULT '0',
	`tEntered` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	`iUpdatedby` INT(11) NOT NULL DEFAULT '0',
	`tUpdated` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
	PRIMARY KEY (`iFreightOnBoardID`) USING BTREE,
	INDEX `IX_OFR_iActive` (`iActive`) USING BTREE,
	INDEX `IX_OFR_iStatus` (`iStatus`, `iUploadlogID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;



/* WGP-410: create new indices for FOB */

CREATE INDEX idx_fob_status on grdb_FreightOnBoard_Charges_Write (iFreightOnBoardID, iStatus)

CREATE INDEX idx_fob_exists_cols on grdb_FreightOnBoard_Charges_Write (iFreightOnBoardID, cChargecode, cRatebasis, cAspect, cScaleUOM, cFrom, cTo, tEffectivedate, iStatus)

CREATE INDEX idx_fob_exists_cols_II on grdb_FreightOnBoard_Charges_Write (iFreightOnBoardID, cChargecode, cRatebasis, cAspect, cScaleUOM, cFrom, cTo, tEffectivedate, tExpirationdate, iStatus)

CREATE INDEX idx_fob_exists_header on grdb_FreightOnBoard_Write (cCustomeralias, cScaccode, cOriginUncode, cDestinationUncode, iStatus)

CREATE INDEX idx_fob_header_id_status on grdb_FreightOnBoard_Write (iFreightOnBoardID, iStatus)

/* WGP-410: create new indices for OFR */

CREATE INDEX idx_ofr_status on grdb_OceanFreight_Charges_Write (iOceanFreightID, iStatus)

CREATE INDEX idx_ofr_exists_cols on grdb_OceanFreight_Charges_Write (iOceanFreightID, cChargecode, cRatebasis, cAspect, cScaleUOM, cFrom, cTo, tEffectivedate, iStatus)

CREATE INDEX idx_ofr_exists_cols_II on grdb_OceanFreight_Charges_Write (iOceanFreightID, cChargecode, cRatebasis, cAspect, cScaleUOM, cFrom, cTo, tEffectivedate, tExpirationdate, iStatus)

CREATE INDEX idx_ofr_exists_header on grdb_OceanFreight_Write (cCustomeralias, cScaccode, cOriginUncode, cDestinationUncode, iStatus)

CREATE INDEX idx_ofr_exists_header_id_status on grdb_OceanFreight_Write (iOceanFreightID, iStatus)

/* WGP-410: create new indices for PLC */

CREATE INDEX idx_plc_status on grdb_Postlanding_Charges_Write (iPostlandingID, iStatus)

CREATE INDEX idx_plc_exists_cols on grdb_Postlanding_Charges_Write (iPostlandingID, cChargecode, cRatebasis, cAspect, cScaleUOM, cFrom, cTo, tEffectivedate, iStatus)

CREATE INDEX idx_plc_exists_cols_II on grdb_Postlanding_Charges_Write (iPostlandingID, cChargecode, cRatebasis, cAspect, cScaleUOM, cFrom, cTo, tEffectivedate, tExpirationdate, iStatus)

CREATE INDEX idx_plc_exists_header on grdb_Postlanding_Write (cCustomeralias, cScaccode, cOriginUncode, cDestinationUncode, iStatus)

CREATE INDEX idx_plc_exists_header_id_status on grdb_Postlanding_Write (iPostlandingID, iStatus)