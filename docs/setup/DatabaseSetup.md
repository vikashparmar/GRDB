# Database Setup

## API Schema Validation configuration

### Overview
* We allow the client to configure which properties are mandatory in the request for each type of API, based on the version number given in the API request.
* Our system honors the data stored in `wbs_Webservice` and `wbs_Webservice_schema` tables within the Master DB, and accordingly ensures that the given properties are present in the request.
* All properties mentioned in the `cRequestSchema` column are treated as MANDATORY properties, so if they are missing in the API request, a validation error is thrown.
* This module does not check for "extra" properties, that is, if the caller adds extra properties like `"apple"` or `"orange"` that are not present in the said tables, it will not throw a validation error during this stage. (That check is done by another module)

### Configuration required
1. First you need to create entries in `wbs_Webservice` table for your APIs, create one entry per API and mention an appropriate value in the `cType` column:

	* Push Rate API: `globalrates_pushrate`
	* Bulk Rate API: `globalrates_bulkrate`
	* Expire Extend API: `globalrates_expireextend`
	* Markup Markdown API: `globalrates_markupmarkdown`
	* Markup Markdown Expire Extend API: `globalrates_markupmarkdownexpireextend`

2. Then in `wbs_Webservice_schema` table you have to create entries for your APIs along with JSON schema to validate.

	* You have to get the `iWebserviceID` of the entry you have created in `wbs_Webservice` table for your API, and store it in column with same name.

	* In `cVersion` column you have to mention the version of that API. For example `1.0`.

	* In `cRequestSchema` column you have to store the schema of required properties as a JSON-formatted string which must contain 3 properties:

		* `"envelop"` - List of mandatory top-level properties in the request
		* `"header"` - List of mandatory properties within the `header` element of the request
		* `"charge"` - List of mandatory properties in each charge inside `charges` element of the request
	
	* The JSON string for `PushRate` API is given below as example:

```json
{
	"envelop": ["type", "version", "senderID", "accessToken", "receiverID", "requestID", "header", "charges"], 
	"header" : ["customer", "memberSCAC", "memberOfficeCode", "originRegion", "originInlandCFS", "originConsolCFS", "portOfLoading", "destinationRegion", "portOfDischarge", "destinationConsolCFS", "destinationInlandCFS", "quotingRegion", "deleteAllRate"], 
	"charge" : ["chargeName", "chargeCode", "aspect", "currency", "rate", "basis", "minimum", "maximum", "effectiveDate", "expirationDate", "scaleUom", "from", "to", "notes", "delete", "conditional"]
}	
```


## Push Notification configuration

To enable `pushNotificationManager` to send notifications to the end user, follow the instruction.

1. Inside `config.yaml` file set `push:enable` to `true` 
2. Set the endpoint of the user inside `grdb_master.gen_Configuration` table.
    - set `cCode` to MEMBER_ENDPOINT
    - set `cValue` to the API endpoint receiving the push notifications
    - set `iProgramID` to RAG_API section id
	- set `userID` of the end user

## Email Notification configuration

There are two protocols for sending emails to the end user. (SMTP/SES)
Configure any one of the following to send emails to the end user.
##### 1. SES (Amazon Simple Email Service)
To send emails using SES, configure the settings in `config.yaml`.
- set `email:protocol` to `ses`
- set `email:sourceEmail` to your SES sender email address
- set `email:destEmail` to your receiver email address
- set `aws:region` to your region
- set `aws:accessKeyId` to your access key
- set `aws:secretAccessKey` to your secret key

##### 2. SMTP (Simple Mail Transfer Protocol)
To send emails using SMTP, configure the settings in `config.yaml`.
- set `email:protocol` to `smtp`
- set `email:sourceEmail` to your SMTP sender email address
- set `email:destEmail` to your receiver email address
- set `smtp:host` to your SMTP host
- set `smtp:port` to your SMTP port
- set `smtp:user` to your SMTP username
- set `smtp:pass` to your SMTP password

## Dashboard Permissions configuration
Two permissions must be added for the user in the `gen_Userpermission` table in order to access file and IT dashboard.
Find the `iSectionID` for GRDB Dashboard and IT Dashboard in the `gen_Section` table, then associate that `iSectionID` with the concerned user in the `gen_Userpermission` table to provide user access to the GRDB Dashboard.