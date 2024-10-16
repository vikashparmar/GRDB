
-- Needed for GRDB Version 1.7 and higher

-- Adding entries in wbs_Webservice table for APIs 

INSERT INTO wbs_Webservice
(cType, cName, cCurrenctVersion, iStatus, iEnteredby, tEntered, iUpdatedby, tUpdated)
VALUES('globalrates_bulkrate', '', '', 0, 0, '2021-04-06 06:14:52', 0, '0000-00-00 00:00:00');

INSERT INTO wbs_Webservice
(cType, cName, cCurrenctVersion, iStatus, iEnteredby, tEntered, iUpdatedby, tUpdated)
VALUES('globalrates_pushrate', '', '', 0, 0, '2021-04-06 06:14:52', 0, '0000-00-00 00:00:00');

INSERT INTO wbs_Webservice
(cType, cName, cCurrenctVersion, iStatus, iEnteredby, tEntered, iUpdatedby, tUpdated)
VALUES('globalrates_expireextend', '', '', 0, 0, '2021-04-06 06:14:52', 0, '0000-00-00 00:00:00');

INSERT INTO wbs_Webservice
(cType, cName, cCurrenctVersion, iStatus, iEnteredby, tEntered, iUpdatedby, tUpdated)
VALUES('globalrates_markupmarkdown', '', '', 0, 0, '2021-04-06 06:14:52', 0, '0000-00-00 00:00:00');

INSERT INTO wbs_Webservice
(cType, cName, cCurrenctVersion, iStatus, iEnteredby, tEntered, iUpdatedby, tUpdated)
VALUES('globalrates_markupmarkdownexpireextend', '', '', 0, 0, '2021-04-06 06:14:52', 0, '0000-00-00 00:00:00');


-- Fetching require ids
SET @pushrate_id = (SELECT iWebserviceID FROM wbs_Webservice WHERE cType='globalrates_pushrate')
SET @bulkrate_id = (SELECT iWebserviceID FROM wbs_Webservice WHERE cType='globalrates_bulkrate')
SET @expire_extend_id = (SELECT iWebserviceID FROM wbs_Webservice WHERE cType='globalrates_expireextend')
SET @markup_markdown_id = (SELECT iWebserviceID FROM wbs_Webservice WHERE cType='globalrates_markupmarkdown')
SET @markupmarkdownexpireextend_id = (SELECT iWebserviceID FROM wbs_Webservice WHERE cType='globalrates_markupmarkdownexpireextend')


-- Adding new columns 

ALTER TABLE wbs_Webservice_schema ADD COLUMN cRequestSchema TEXT;


-- Adding entries in wbs_Webservice_schema table 


INSERT INTO wbs_Webservice_schema
(iWebserviceID, cVersion, cSchema, cFieldList, cXmltagList, cVersionsupport, cSchemaType, iStatus, iEnteredby, tEntered, iUpdatedby, tUpdated, cRequestSchema)
VALUES(@pushrate_id, '1.0', '', '', '', 'Y', 'O', 0, 0, '0000-00-00 00:00:00', 0, '0000-00-00 00:00:00', '{"envelop": ["type", "version", "senderID", "accessToken", "receiverID", "requestID", "header", "charges"], "header" : ["customer", "memberSCAC", "memberOfficeCode", "originRegion", "originInlandCFS", "originConsolCFS", "portOfLoading", "destinationRegion", "portOfDischarge", "destinationConsolCFS", "destinationInlandCFS", "quotingRegion", "deleteAllRate"], "charge" : ["chargeName", "chargeCode", "aspect", "currency", "rate", "basis", "minimum", "maximum", "effectiveDate", "expirationDate", "scaleUom", "from", "to", "notes", "delete", "conditional"]}');


INSERT INTO wbs_Webservice_schema
(iWebserviceID, cVersion, cSchema, cFieldList, cXmltagList, cVersionsupport, cSchemaType, iStatus, iEnteredby, tEntered, iUpdatedby, tUpdated, cRequestSchema)
VALUES(@bulkrate_id, '1.0', '', '', '', 'Y', 'O', 0, 0, '0000-00-00 00:00:00', 0, '0000-00-00 00:00:00', '{"envelop": ["type", "version", "senderID", "accessToken", "receiverID", "requestID", "header", "charges"], "header" : ["customer", "memberSCAC", "memberOfficeCode", "quotingRegion", "originDestination", "exclude", "deleteAllRate"], "originDestination": ["originCountry", "originLocation", "destinationCountry", "destinationLocation"], "exclude": ["originCountry", "originLocation", "destinationCountry", "destinationLocation"], "charge": ["chargeName", "chargeCode", "aspect", "currency", "rate", "basis", "minimum", "maximum", "effectiveDate", "expirationDate", "scaleUom", "from", "to", "notes", "delete", "conditional", "insertIfNotFound"]}');


INSERT INTO wbs_Webservice_schema
(iWebserviceID, cVersion, cSchema, cFieldList, cXmltagList, cVersionsupport, cSchemaType, iStatus, iEnteredby, tEntered, iUpdatedby, tUpdated, cRequestSchema)
VALUES(@expire_extend_id, '1.0', '', '', '', 'Y', 'O', 0, 0, '0000-00-00 00:00:00', 0, '0000-00-00 00:00:00', '{"envelop": ["type", "version", "senderID", "accessToken", "receiverID", "requestID", "header", "charges"], "header" : ["customer", "memberSCAC", "memberOfficeCode", "quotingRegion", "originDestination", "exclude"], "originDestination": ["originCountry", "originLocation", "destinationCountry", "destinationLocation"], "exclude": ["originCountry", "originLocation", "destinationCountry", "destinationLocation"], "charge": ["chargeName", "chargeCode", "aspect", "currency", "rate", "basis", "minimum", "maximum", "effectiveDate", "expirationDate", "oldExpirationDate", "scaleUom", "from", "to", "notes", "conditional"]}');


INSERT INTO wbs_Webservice_schema
(iWebserviceID, cVersion, cSchema, cFieldList, cXmltagList, cVersionsupport, cSchemaType, iStatus, iEnteredby, tEntered, iUpdatedby, tUpdated, cRequestSchema)
VALUES(@markup_markdown_id, '1.0', '', '', '', 'Y', 'O', 0, 0, '0000-00-00 00:00:00', 0, '0000-00-00 00:00:00', '{"envelop": ["type", "version", "senderID", "accessToken", "receiverID", "requestID", "header", "charges"], "header" : ["customer", "memberSCAC", "memberOfficeCode", "quotingRegion", "originDestination", "exclude"], "originDestination": ["originCountry", "originLocation", "destinationCountry", "destinationLocation"], "exclude": ["originCountry", "originLocation", "destinationCountry", "destinationLocation"], "charge": ["chargeName", "chargeCode", "aspect", "currency", "markupType", "rate", "basis", "minimum", "maximum", "effectiveDate", "expirationDate", "scaleUom", "from", "to", "notes", "conditional"]}');


INSERT INTO wbs_Webservice_schema
(iWebserviceID, cVersion, cSchema, cFieldList, cXmltagList, cVersionsupport, cSchemaType, iStatus, iEnteredby, tEntered, iUpdatedby, tUpdated, cRequestSchema)
VALUES(@markupmarkdownexpireextend_id, '1.0', '', '', '', 'Y', 'O', 0, 0, '0000-00-00 00:00:00', 0, '0000-00-00 00:00:00', '{"envelop": ["type", "version", "senderID", "accessToken", "receiverID", "requestID", "header", "charges"], "header" : ["customer", "memberSCAC", "memberOfficeCode", "quotingRegion", "originDestination", "exclude"], "originDestination": ["originCountry", "originLocation", "destinationCountry", "destinationLocation"], "exclude": ["originCountry", "originLocation", "destinationCountry", "destinationLocation"], "charge": ["chargeName", "chargeCode", "aspect", "currency", "markupType", "rate", "basis", "minimum", "maximum", "oldExpirationDate", "effectiveDate", "expirationDate", "scaleUom", "from", "to", "notes", "conditional"]}');

