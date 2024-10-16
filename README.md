# GRDB

## Contents

- [Overview](#overview)
- [Dashboard](#dashboard)
- [Lambdas](#lambdas)
- [Master Database](#master-database)
- [GRDB Database](#grdb-database)
- [FTP Monitor](/docs/modules/FTPMonitor.md)
- [Rest API](/docs/api/RestAPI.md)

## Reference

#### Module Reference

- [SQS Listener](/docs/modules/SqsListener.md)
- [Upload File Trigger](/docs/modules/UploadFileTrigger.md)

#### Setup Reference

- [Database Setup](/docs/setup/DatabaseSetup.md)
- [Developer Setup](/docs/setup/DeveloperSetup.md)

#### API Reference

- [Push Rate API](/docs/api/PushRate.md)
- [Bulk Rate API](/docs/api/BulkRate.md)
- [Expire Extend API](/docs/api/ExpireExtend.md)
- [Markup Markdown API](/docs/api/MarkupMarkdown.md)
- [Markup Markdown Expire Extend API](/docs/api/MarkupMarkdownExpireExtend.md)
- [Poll Job Status API](/docs/api/PollJobStatus.md)
- [Push Notification API](/docs/api/PushNotification.md)

# Overview

### Overall process flow

1. Files are added into the S3 input bucket or data is pushed using REST API
2. [Lambda trigger function](#upload-file-trigger) executes and adds an entry into the job table and SQS input queue
3. [SQS listener](#sqs-listener) running on EKS cluster responds to SQS queue entry and validates the file, inserts records into MySQL DB, and generates error log in CSV format

![workflow](/.github/images/system_architecture.png)

### Pod processing timeline

Multiple instances of the [SQS listener](#sqs-listener) are running on EKS cluster pods. One instance is running per pod. Each instance processes a single job at a time.

Assuming that 6 input jobs are added for customers called *Agility* and *Standard*:​

- M1. FOB for Agility
- M2. FOB for Agility
- M3. PLC for Agility​
- M4. FOB for Standard
- M5. OFR for Standard
- M6. OFR for Standard

This timeline depicts the order of execution as well as delays implemented to prevent simultaneous insertion of the same client's data, as processed by the [Wait Loop](#wait-loop).

![timeline](/.github/images/pod_execution_timeline.png)

### Job status flow

All [jobs](#job-table) move through the following states. The green and red colored states are "completed" states while the rest are "in progress" states.

![states](/.github/images/job_state_workflow.png)

### Project architecture 

This project is divided into 3 layers:

- **Service Layer** - Stored in folders `sqs-listener`, `serverless` and `automation`
- **Business Logic Layer** - Stored in folders `framework.grdb`
- **Data Access Layer** - Stored in folders `framework.system`, `framework.formats` and `framework.cloud`

![timeline](/.github/images/system_layers.png)




# Dashboard

The Executive Dashboard is developed in Angular and displays live stats of the running jobs, pending jobs and successful/failed jobs.

Component hierarchy:

- `dashboard`
  - `top-row`
  - `mid-row`
  - `last-row`
- `graphs`
- `reports-board`
- `upload-file`
- `white-boxes`

![dashboard](/.github/images/dashboard_screenshot.png)

## Charts View

![dashboard](/.github/images/dashboard_charts_screenshot.png)

## Files View

![dashboard](/.github/images/dashboard_files_screenshot.png)

## Log View

![dashboard](/.github/images/dashboard_log_screenshot.png)

## IT Dashboard

This view shows the live Kubernetes pod status and the details of individual pods.

![dashboard](/.github/images/dashboard_pods_screenshot.png)


# Types of files
### Horizontal CSV file
Horizontal-CSV filename format: `<MEMBER>_<RATE>_<CUSTOMER>_<DATE>_<TIME>_<NUM>.csv` 
Horizontal files are those that have multiple charge columns for each header.
| Header | Charge\_1 | Charge\_2 | Charge\_3 |
| ------------------- |-----------|-----------|-----------|
| ABC\_header         | ... | ... | ... |
| XYZ\_header         | ... | ... | ... |

### Vertical CSV file
Vertical-CSV filename format: `V_<MEMBER>_<RATE>_<CUSTOMER>_<DATE>_<TIME>_<NUM>.csv`
Vertical files are those that have only one charge column for each header.
| Header | Charge |
| ------------------- |-----------|
| ABC\_header         | charge_1 |
| ABC\_header         | charge_2 |
| ABC\_header         | charge_3 |
| XYZ\_header         | charge_1 |
| XYZ\_header         | charge_2 |
| XYZ\_header         | charge_3 |




# Lambdas

Index of all existing serverless functions deployed on AWS Lambda.

Directory: `serverless`

| Lambda function name                     | Lambda entry script                          | REST API route                        | Description                              |
| ---------------------------------------- | -------------------------------------------- | ------------------------------------- | ---------------------------------------- |
| loginMember                              | auth/loginMember.py                          | /login                                | Creation of auth token from credentials  |
| loginDashboard                           | auth/loginDashboard.py                       | /dashboard/login                      | To login user in GRDB File,IT Dashboard  |
| createPresignedUrl                       | files/createPresignedUrl.py                  | /create-presigned-url                 | Return presigned url to upload a file    |
| authenticateSftpUser                     | auth/authenticateSftpUser.py                 | /authenticate-sftp-user               |					     |
| authenticateSftpUserNew                  | auth/authenticateSftpUserNew.py              | /authenticate-sftp-user-test          |					     |
| authenticateSftpUserWithPassword         | auth/authenticateSftpUserWithPassword.py     | /authenticate-sftp-user-with-password |					     |
| downloadFile                             | files/downloadFile.py                        | /download-file                        | Download file from s3 from the full path |
| uploadFileTrigger                        | files/uploadFileTrigger.py                   | ---                                   | Internal trigger when file is uploaded   |
| getUploadLog                             | reports/getUploadLog.py                      | /report/uploadlog                     | Dashboard uploadlog report data endpoint |
| getLockingRatesLog                       | reports/getLockingRatesLog.py                | /report/lockingrate                   | Dashboard lockingrate data endpoint      |
| getJobLogs                               | dashboard/getJobLogs.py                      | /logs/jobs                            | Dashboard Job logs table data endpoint   |
| getErrorLogs                             | dashboard/getErrorLogs.py                    | /logs/errors                          | Dashboard error lob table data endpoint  |
| graphDataSourceProcessed                 | dashboard/graphDataSourceProcessed.py        | /timeseries/datasourceprocessed       | Dashboard source wise graph data endpoint|
| graphProcessedData                       | dashboard/graphProcessedData.py              | /timeseries/processed                 | Dashboard file size graph data endpoint  |
| getMetricsData                           | dashboard/getMetricsData.py                  | /metrics                              | Dashboard home page metrics data endpoint|
| filterCustomerName                       | dashboard/filterCustomerName.py              | /filterCustName                       | Dashboard customer name filter endpoint  |
| filterOfficeId                           | dashboard/filterOfficeId.py                  | /filterOfficeCode                     | Dashboard office code filter endpoint    |
| exportCsvUploadLog                       | reports/exportCsvUploadLog.py                | /uploadLog/exportcsv                  | Dashboard uploadlog report download API  |
| exportCsvLockingRates                    | reports/exportCsvLockingRates.py             | /lockingRates/exportcsv               | Dashboard lockingrate rep. download API  |
| pushRate                                 | rates/pushRate.py                            | /rates/pushRate                       | Push rates to system in JSON/XML API     |
| pollJobStatus                            | rates/pollJobStatus.py                       | /rates/pollJobStatus                  | Fetch job status with jobid/requestid    |
| bulkRate                                 | rate/bulkRate.py                             | /rates/bulkRate                       | Push bulk rates to system API            |
| expireExtend                             | rate/expireExtend.py                         | /rates/expireExtend                   | Push Expire Extend rates API             |
| markupMarkdown                           | rate/markupMarkdown.py                       | /rates/markupMarkdown                 | Push markup markdown rates API           |
| markupMarkdownExpireExtend               | rate/markupMarkdownExpireExtend.py           | /rates/markupMarkdownExpireExtend     | Push Expire Extend, markup/down rates API|



# Master Database

Only used for read-only constants, that are loaded at app start and stored in the `AppGlobal` object.

| Table name | Purpose and usage | Sample values |
|-------------|-------------------|---------------|
| `gen_Basis` |  List of rate basis (units of measurement used to measure shipping cargo) | by Weight, by Measure, Per Pound, Per Container.. |
| `gen_Carrier` | List of shipping carriers (cargo companies) and their details  |
| `gen_Chargecode` | List of charge codes and the corresponding charge names  | `GLA` refers to `Low Tide Surcharge`, `CUSG` refers to `Customs Clearance (Garments)` |
| `gen_Configuration` | List of all configuration or settings  | valid Data type for API, valid version, valid File format |
| `gen_Country` | List of all countries, their names, UN-country-codes and shipping configuration |
| `gen_Currency` | List of currencies used to measure financial value of cargo  | `USD`, `CHF`, `GBP` |
| `gen_Currency_exchange_rate` | Daily currency exchange rates to convert between USD and various currencies  |
| `gen_Customer_alias` |  List of short names used to uniquely identify a WWA Customer | `THUNDMD` refers to `Thunderbolt Global Logistics` |
| `gen_Location` |  List of all the ports, their names, UN-port-codes, geo-location and shipping configuration |
| `gen_Program` |  List of all program ids, used to fetch configuration from `gen_Configuration` table | ID of `RAG`, ID of `RAG_API` |
| `gen_Region` | List of major shipping regions | Europe, Asia, Middle East..  |
| `gen_Section` | List of sections to be displayed in the dashboard |
| `gen_Setting_Code` | List of codes of all settings that are in use in `gen_Configuration` table | `USERTYPE` and `WO/WE` |
| `gen_User` | List of details of all users, like username, password, ID, email ID etc |  |
| `gen_Userpermission` | List of users and sections they are authorized to view in reports |
| `sei_Member` | List of values which helps to find export to customer records |  |
| `wbs_Webservice` | In this table we can create entries for APIs for which we want to validate the schema |  |
| `wbs_Webservice_schema` | In this table we can store JSON schema for APIs with which we can validate the schema |  |
# GRDB Database

### Configuration Tables

Only used for read-only constants, that are loaded at app start and stored in the `AppGlobal` object.

| Table name | Purpose and usage |
|-------------|-------------------|
| `grdb_Locking_Customers` |  List of allowed/denied rate types for specific WWA customers   |
| `grdb_Routing_Customer_Mapping` |  List of acceptable shipping routes, keyed by 3 properties (WWA customer code, origin UN-code, destination UN-code) |
| `grdb_Upload_Validation_Changes` | List of substitution that [Macro Validation](#macro-validation) must make  |
| `grdb_Spreadsheet_map` |  List of acceptable CSV column headers for horizontal-CSV or vertical-CSV files |
| `grdb_Aspect` |  List of valid aspect values |
| `rat_global_Charge_setting` |  List of values, using which we can detect that a charge is conditional or mandatory |
| `grdb_zerovaluenotes` |  List of notes for zero value rates, where we set the configuration for file type, portpair and notes that has to be imported |
| `grdb_zerovaluenotes_customer` |  List of configuration for zero value notes for customers |
| `grdb_Routing_guide` |  List of all routing guide business rules |
| `grdb_Locking_tradelanes` |  List of all trade lanes that are locked for specific customers |

### Insertion Tables

The main output of the GRDB engine is stored here. GRDB reads the input files and inserts the rate charges into these tables. They are used in read/write mode.

| Table name | Purpose and usage |
|-------------|-------------------|
| `grdb_FreightOnBoard_Write` | FOB - Charges are first inserted into this table  |
| `grdb_FreightOnBoard_Charges_Write` |  FOB - Charges from 1st table are moved to this table |
| `grdb_FreightOnBoard_Charges_History` | FOB - Charges from 2nd table are moved to this table for archival |
| `grdb_OceanFreight_Write` |  OFR - Charges are first inserted into this table |
| `grdb_OceanFreight_Charges_Write` |  OFR - Charges from 1st table are moved to this table |
| `grdb_OceanFreight_Charges_History` |  OFR - Charges from 2nd table are moved to this table for archival |
| `grdb_Postlanding_Write` |  PLC - Charges are first inserted into this table |
| `grdb_Postlanding_Charges_Write` |  PLC - Charges from 1st table are moved to this table |
| `grdb_Postlanding_Charges_History` |  PLC - Charges from 2nd table are moved to this table for archival |


### Info Tables

The tables we use to store information to understand the status or condition of processing.

| Table name | Purpose and usage |
|-------------|-------------------|
| `grdb_Job` | In this table we store all job related metadata |
| `grdb_Pod` | In this table we store all pod related metadata |
| `grdb_API_requestLogs` | In this table we store all API related metadata including the request and response |
| `tra_Error_Log` | In this table we store all validation errors, generated during processing a file |


### Job Table

The job table `grdb_Job` is the main state management system used for tracking queued jobs, in-progress jobs and completed/failed jobs. Every incoming file is treated as one job, and has one entry in the job table.

| Column name | Purpose and usage | Sample values or Enum name |
|-------------|-------------------|--------|
| `iJobID` | Primary key of the job, always an auto-incrementing integer |
| `cAppVersion` | Version of SQS listener which processed this job. Only filled once the pod picks up the job. |
| `cUserName` | Username based on the S3 bucket folder name, indicating who uploaded it |
| `cStatus` | Current status of the job | Enum: `JobStatus` |
| `cOldStatus` | (Outdated) Older status of the job | Enum: `JobOldStatus` |
| `cProcessStatus` | (Outdated) Status of data insertion | Enum: `JobProcessStatus` |
| `cDataInserted` | Boolean to indicate if data insertion is complete | `Y` or `N` |
| `cSource` | Where did the job originate from? | Enum: `Job_Source` |
| `cOriginalFilename` | Original filename and extension | 
| `cFilePath` | Full S3 bucket filepath within processing bucket | 
| `cFileName` | Full filename within processing bucket |
| `cSheetType` | Type of data in sheet | `FOB` or `PLC` or `OFR` |
| `cFileType` | Type of insertion required | `accurate` or `online` |
| `cCustomerName` | The WWA customer name | Sample: `AGILITY`, `STANDARD`, `FEDEXTRADE` |
| `cMemberCode` | Usually always `SHPT` |
| `tCreated` | Timestamp when the job was created |
| `tLastUpdated` | Timestamp when the job was last updated (not accurate) |
| `iFileSize` | File size of the input file in bytes |
| `iTotalRowCount` | Total row count of input file |
| `iErrorRowCount` | Failed row count of the input file |
| `iValidatedRowCount` | Correct row count of the input file |
| `cErrorLogFilepath` | FTP filepath of the error log (only filled after job is complete) |
| `cCorrectLogFilepath` | FTP filepath of the correct log (only filled after job is complete) |
| `tJobStart` | Timestamp when the SQS listener started processing the job |
| `tJobEnd` | Timestamp when the SQS listener completed processing the job |
| `tJobDuration` | Duration the job took to process in SQS listener |
| `tFormatValStart` | Timestamp when [Format Validation](#format-validation) begun |
| `tFormatValEnd` | Timestamp when Format Validation ended |
| `tFormatValDuration` | Duration of Format Validation |
| `tValidateStart` | Timestamp when [Rule Validation](#rule-validation) begun |
| `tValidateEnd` | Timestamp when Rule Validation ended |
| `tValidateDuration` | Duration of Rule Validation |
| `tWaitStart` | Timestamp when [Wait Loop](#wait-loop) begun |
| `tWaitEnd` | Timestamp when Wait Loop ended |
| `tWaitDuration` | Duration of Wait Loop |
| `iWaitJobID` | The Job ID of the previous job which we are/were waiting for (value is not cleared even after waiting is complete, to preserve it for historical record) |
| `tInsertStart` | Timestamp when [Rate Insertion](#rate-insertion) begun |
| `tInsertEnd` | Timestamp when Rate Insertion ended |
| `tInsertDuration` | Duration of Rate Insertion |
| `cExceptions` | (Outdated) Only stores the text output of [Format Validation](#format-validation) exceptions |
| `cPodName` | The name of the pod that processed the JOb |
| `cMessageID` | To store the Message ID if we have it with the message that we processed |
| `cContainerID` | Id of Container |
| `tHeartbeat` | Timestamp when the Job was active for the last time |
| `iMemoryUsed` | Amount of memory used to process the Job |
| `tOriginalDateModified` |  |
| `cRequestID` | The request ID we got from an API |
| `cValidateErrors` | The JSON of all validation errors |
| `cValidateWarnings` | The JSON of all validation warnings | 
| `cFileFormat` | The File Format that is allowed for current user |
| `cUserType` | The Online or Accurate (WE / WO) value which is allowed for current user |
| `iStatus` | To check whether a job is active or not |
| `iPriority` | The priority of the current Job |

