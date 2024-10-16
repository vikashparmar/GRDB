# SQS Listener

The main data processing engine of GRDB, it handles reading the files, validation and insertion of correct rows.



## Main Program 

- At startup, the SQS input queue is checked for messages.
  - If no messages are found, the program exits
  - If messages are found, then the [Global Data](#global-data) is loaded and the following steps are done

- These steps are done per message received in SQS input queue:

  - Read the job metadata and check the [job status](#job-status-flow)
    - If the job status is `CREATED` or `QUEUED` then go to next step
    - If job is any other status:
	   - &#x1F538; Abort this job and all further steps
       - This is done to prevent the same job being executed multiple times by different pods
  
  - Perform [File Name Validation](#file-name-validation)
  
    - If the filename is invalid:
  	   - Set the job status to `FILE_NAME_FORMAT_ERROR` in `grdb_Job` table  
  	   - Move the CSV file into the `error` bucket 
  	   - &#x1F538; Abort this job and all further steps
  	
    - If the filename is valid, then go to next step
      
  - Load the input file from the input S3 bucket and convert it into an [Object Model](#object-model)
  - Perform [Macro Validation](#macro-validation)
  
  - Perform [Format Validation](#format-validation)
  
    - If the format is invalid:
       - Send an email using template `rate_upload_errors`
  	   - Add the job into `tra_Error_Log` table 
  	   - Set the job status to `FILE_FORMAT_ERROR` in `grdb_Job` table  
  	   - Move the CSV file into the `error` bucket 
  	   - &#x1F538; Abort this job and all further steps
  
    - If the format is correct:
      - Perform [Rule Validation](#rule-validation)
  	    - If the rule validation has passed for at least one rate:
           - Perform [Wait Loop](#wait-loop)
           - Perform [Rate Insertion](#rate-insertion)
  
      - Generate the following outputs:
      
      	- Correct log (list of correct rows) 
      	- Error log (list of incorrect rows) 
      
      - Move the CSV file into a bucket based on the number of correct/invalid rates: 
      
      	- `fully-correct` - all rows were valid 
      
      	- `fully-incorrect` - all rows were invalid 
      
      	- `partially-correct` - some rows were valid, and some invalid 
      
      - Perform [Log Upload](#log-upload)
  	

	
	
## Error Handling

### Component-wise

- SQS Listener
   - Central job error handling is implemented within the job loop, handle all errors properly and change job status.
- App Job
   - The getting of job metadata should NOT have try/except so that the top level handler catches it.
- Business Logic
   - All insertion functions should NOT have try/except so that the top level handler catches it.
   - All validation functions should NOT have try/except so that the top level handler catches it.

### Critical failure handling

- All AppGlobal failures SHOULD crash the job and go into ERROR state
- All AppJob init failures SHOULD crash the job and go into ERROR state
- All validation failures SHOULD crash the job and go into ERROR state
- All insertion failures SHOULD crash the job and go into ERROR state

### Non-critical failure handling

- All failures of Push Notify should NOT crash the job and it should be handled - job should resume perfectly
- All failures of Email/SMTP/SES should NOT crash the job and it should be handled - job should resume perfectly
- All failures to delete the job SQS messages should NOT crash the job
- All failures to move the job file from one S3 bucket to another should NOT crash the job
- All failures to update the job status to ERROR should NOT crash the job
- All failures to update the job heartbeat should NOT crash the job

	
	
## Global Data

`AppGlobal` is a static class that loads globally required constants from the database, and caches it in memory, so that the validation and insertion can refer to them instantaneously.

Following data sources are loaded:

1. [Master Database](#master-database)
2. [Configuration Tables](#configuration-tables) from GRDB Database 




## Object Model

All files are first converted to an object model in the following format:

- Job data
   - Multiple rates per job
      - Single header per rate
      - Multiple charges per rate

- `AppJob` class
   - `RateRecord` class
      - `RateHeader` class
      - `RateCharge` class
	  
	  



## File Name Validation

Input filename must be in the following format, for Horizontal-CSV and MessagePack Files:

- Expectation: `<MEMBER>_<RATE>_<CUSTOMER>_<DATE>_<TIME>_<NUM>`
- Example:  `SHPT_OFR_EMOUSA_20210823_114006980_1`

Input filename must be in the following format, for Vertical-CSV Files:

- Expectation: `V_<MEMBER>_<RATE>_<CUSTOMER>_<DATE>_<TIME>_<NUM>`
- Example:  `V_SHPT_OFR_STANDARD_20210910_153748932`

### Macro Validation on File Name

[Macro Validation](#macro-validation) (substitution of incorrect value with correct value) is performed for the `<MEMBER>` component of the filename. It is called `memberSCAC` and substituted according to the `cscaccode` set in the `grdb_Upload_Validation_Changes` table.





## Format Validation

For message pack files:

- No format validation (because input request is already validated by the Push Rate / Bulk Rate API)

For Horizontal-CSV files:

1. File type is detected, either `accurate` or `online` (`accurate` if the first column is `Status`)
2. All rate records' `customer` must match the `<CUSTOMER>` field in filename
3. Headers must match the data given in the `grdb_Spreadsheet_map` filtered by `cVersion = 2.0`

For Vertical-CSV files:

1. Vertical files are always `online`
2. All rate records' `customer` must match the `<CUSTOMER>` field in filename
3. Headers must match the data given in the `grdb_Spreadsheet_map` filtered by `cVersion = 3.0`





## Macro Validation

Macro validation is performed directly on the object model (ie. `RateRecord` entries within the job)

It is a misnomer and is not really validation, it is actually substitution. Incorrect values are detected and substituted without throwing any validation errors. This is done to automatically fix some slightly-incorrect input data. For example in `currency` column, the value `U$D` is macro-validated to `USD`.

Macro validation rules are loaded from the table `grdb_Upload_Validation_Changes`.

There are different rate types as per the `cRateType` column in the table `grdb_Upload_Validation_Changes`. Each property will fall into a single rate type. For example the property `originInlandCFS` is a UN-Code so it will use the `uncode` rate type.

### Header Rule Validation

Following substitution are performed on the rate header (`RateHeader` object)


| `RateHeader` Property | Rate type <BR> (`cRateType` column) |
|-----------|------------|
| `memberSCAC` | `cscaccode` |
| `originRegion` | `regioncode` |
| `originInlandCFS` | `uncode` |
| `originConsolCFS` | `uncode` |
| `portOfLoading` | `uncode` |
| `transhipment1` | `uncode` |
| `transhipment2` | `uncode` |
| `transhipment3` | `uncode` |
| `destinationRegion` | `regioncode` |
| `portOfDischarge` | `uncode` |
| `destinationConsolCFS` | `uncode` |
| `destinationInlandCFS` | `uncode` |


### Charge Rule Validation

Following substitution are performed on the rate charges (`RateCharge` object)

| `RateCharge` Property | Rate type <BR> (`cRateType` column) |
|-----------|------------|
| `basis` | `ratebasis` |
| `currency` | `currency` |
| `minimumAmount` | `minimum` |
| `maximumAmount` | `maximum` |




## Rule Validation

Rule validation is performed directly on the object model (ie. `RateRecord` entries within the job)

### Header Rule Validation

Following validation rules are performed on the rate header (each rate has one header), represented by the `RateHeader` object.

| Rule Name  | Class name | Description |
|------------|-------------------------|--------------
| Status rule | `HeaderStatusChargeRule` | Only allows 'N' or 'D' in status column |
| Member SCAC rule |  `HeaderMemberScacRule` | We have to match the member SCAC with `gen_Carrier` table |
| Origin CFS rule | `HeaderOriginCfsRule` | The origin inland CFS and consol CFS value should match with the `gen_Region` table |
| Destination CFS rule | `HeaderDestCfsRule` | The destination inland CFS and deconsol CFS value should match with the `gen_Region` table |
| Port rule | `HeaderPortRule` | The port of loading and port of discharge should match with the `gen_Location` table |
| Transhipment rule | `HeaderTranshipmentRule` | All transhipment values should match with the `gen_Location` table |
| Origin Region rule | `HeaderOriginRegionRule` | The value of origin region should match with the `gen_Location` table |
| Destination Region rule | `HeaderDestRegionRule` |  The value of destination region should match with the `gen_Region` table |
| Customer Code rule | `HeaderCustomerCodeRule` | The customer code should be validated against the data we have in `gen_Customer_alias` table |
| Origin Destination rule | `HeaderBulkOriginDestinationRule` | All rules related to Origin Destination section for some APIs |
| OFR Status rule | `HeaderOfrStatusRule` | Disallows multiple currency for OFR rates in same file. |


### Charge Rule Validation

Following validation rules are performed on the rate charges (each rate has MULTIPLE charges), represented by the `RateCharge` object.

| Rule Name  | Class name for the rule | Description |
|------------|-------------------------|--------------
| Currency rule | `ChargeCurrencyRule` | All currency should be validated against `gen_Currency_exchange_rate` table data |
| Conditional column rule | `ChargeConditionalRule` | The conditional value can be 'C' or 'M' |
| Aspect code rule | `ChargeAspectRule` | Aspect code should be validated against `grdb_Aspect` table data |
| Scale UOM rule | `ChargeScaleUOMRule` | Scale UOM value should be validated against configured data |
| Charge Code rule | `ChargeCodeRule` | The Charge code value should be validated against `gen_Chargecode` table data |
| Charge name rule | `ChargeNameRule` | This is required field |
| Rate rule | `ChargeRateAmountRule` | This should be a numeric value |
| Rule for Maximum value | `ChargeMaxRateRule` | This should be a numeric value |
| Rule for Minimum value | `ChargeMinRateRule` | This should be a numeric value |
| Rate basis rule | `ChargeRateBasisRule` | This value should be validated against `gen_Basis` table data |
| Rule for IM20 | `ChargeRateBasisIm20Rule` | Rate basis from WM group is only allowed for IM20 |
| Effective and Expiration date rule | `ChargeEffectiveExpiryRule` | Effective Date should not be larger than Expiration Date |
| Rule related to From and To | `ChargeFromToRule` | This should be a numeric value |


### Wait Loop

Before records are inserted, we have to wait for any conflicting jobs to finish as per the [Pod processing timeline](#pod-processing-timeline). The wait-loop engine handles this.

**Behavior:**
- In local mode immediately insert the rates
- In cloud mode insert rates after waiting for previous conflicting jobs to complete insertion

**Algorithm:**
- Get any conflicting jobs that are before this job (any jobs that match the following criteria)
  - Jobs with the SAME WWA customer
  - Jobs with the SAME sheet type (FOB / PLC / OFR)
  - Jobs which have been created BEFORE this job (by comparing the job ID column which is 100% deterministic)
  - Jobs which have been started (not in CREATED state)
  - Jobs which are not already complete (either COMPLETED or any of the error states)
- Get the last conflicted entry that we need to wait on (each job only waits on the previous job in the conflict-set)
- Mark this job status as WAITING
- Every 5 seconds, check if the previous job is complete (status is either COMPLETED or any of the error states)
  - If the previous job is complete, then mark this job status as INSERTING and end the wait loop
  - If the previous job is not complete, keep waiting





## Rate Insertion

- All insertion logic is implemented in `RateInsertManager`, and divided into these parts:

* Insertion Logic - `insert()`
* Insertion Logic for Markup/Markdown/Expire/Extend - `markup_markdown_expire_extend()`
* Insertion Logic for Future Date/Back Date Cases - `future_date_back_date_cases()`
* Insertion Logic for Charge History - `insert_charge_history()`
* Insertion Logic for Rate Deletion - `rate_delete() `

### Insertion Logic

- If current job has came from markUpMarkDown or expireExtend related APIs 
	- Then send the current job to `markup_markdown_expire_extend()` 
- Iterate through all rates:
	- If rate is not valid then skip the current rate 
	- Check if header is existing one or not for current rate 
	- If header exists then add to update_header var 
		- Check if it’s an "all delete" case
		- If not an "all delete" case:
			- Iterate through all charges in current rate 
				- If current charge is not valid then skip it 
				- Check if charge exists or not 
				- Check if it is a single charge delete case 
				- Send charge value, and header value to `future_date_back_date_cases()` to get insert array and update array for charge 
		- If all delete case or valid charge found 
			- Send existing charges to `insert_charge_history()` to insert existing charges to charge history table 
			- If this is an all delete or single delete case send charge ids to `rate_delete()`
			- Calculating `iActive` value for header 
			- If the current header is existing, one then update header or insert a new header 
			- Check for export header case
			- If it’s a export header case then inserts header info in export header log table 
			- If update array for charge exists 
				- Iterate through the array and update charges 
			- If insert array for charge exists 
				- Iterate through the array and insert charges 


### Insertion Logic for Markup/Markdown/Expire/Extend

- Iterate through all rates:
	- If rate is not valid then skip the current rate 
	- Check if current header exists or not 
	- If current header exists:
		- Iterate through all charges in current rate 
			- If current charge is not valid then skip it 
			- If current API type is `MarkupMarkdown`
				- Fetch existing charge using usual fields
			- Else:
				- Fetch existing charge using usual fields along with `oldExpirationDate` (we got from API) as `tExpirationdate` in table 
			- Iterate through fetched charges: 
				- If current API type is `MarkupMarkdownExpireExtend`:
					- Calculate MarkUpMarkDown values for charge dict 
					- Send current charge and header dict to `future_date_back_date_cases()` to get update charge query array and insert charge query array 
				- If current API type is `ExpireExtend`:
					- Send current charge and header dict to `future_date_back_date_cases()`
					- To get update charge query array and insert charge query array 
				- If current API type is `MarkupMarkdown`:
					- Calculate MarkUpMarkDown values for charge dict 
					- Update charge write table 
	- Send matching charges to `insert_charge_history_archive()`
	- Update header table 
	- If Update charge array exists 
		- Iterate through update charge queries and execute them 
	- If Insert Charge array exists 
		- Iterate through insert charge queries and execute them 


### Insertion Logic for Future Date/Back Date Cases

- Check if duplicate charge exists or not 
- If duplicate record exists 
	- Prepare Update array
- If duplicate record does not exist:
	- Check if charge with matching effective date exists or not 
	- If record exists with matching effective date 
		- Check for records with overlapping dates 
		- If records with overlapping dates do not exists 
			- Prepare Update array
		- If records with overlapping dates exist 
			- new expiry date will be old effective date – 1 day 
			- Prepare Update array with new expiry date
	- If record do not exist with matching effective date 
		- If record with overlapping future date exists 
			- Old expiry date will be new effective date (from file) - 1 day 
			- Prepare Update array with old expiry date
		- If record with overlapping future date does not exists 
			- Check if overlapping record exists or not 
			- If overlapping record exists 
				- New expiry date will be new effective date – 1 day 
				- Prepare Update array with new expiry date
		- If record with overlapping back date exists 
			- new expiry date will be old effective date – 1 day 
			- Prepare Update array with new expiry date
		- If record with overlapping back date does not exist 
			- Check if overlapping record exists or not 
			- If overlapping record exists 
				- new expiry date will be old effective date – 1 day 
		- Prepare Insert array

- return update array and Insert array


### Insertion Logic for Charge History

- Iterate through matching charge ID list 
	- For each charge ID fetch records from charge write table 
	- And insert each record to charge history table 

### Insertion Logic for Rate Deletion

- If header ID found to delete
	- Then it is a case for all rate delete
	- Delete all records from charge write table having the same header ID 
	- Fetch the list of charge history ID 
- If list of charge ids found to delete 
	- Then it may not be a case for all rate delete
	- Delete all records from charge write table matching the charge ids 
- Return delete case and list of charge history ID 

### Insertion Logic For Dashboard Unique Lane

- Insertion in the `Dashboard_Unique_Lane` table. The conditions are mentioned below.
	- If we already have a record for current Customer then exit
	- If we don't have a record with current customer then insert a record
	- Make the exist column 0 based on the rate type. For example, for OFR we will make `iOFRExist` column 0.
	- Also record other header related data, like scac code, origin, destination etc.

### Insertion Charge Processing

* If min < irate for WM rate basis the Min should be updated with irate. For this we have to check the following conditions
	- If Min column value is lesser than the value in iRate column, then min column value should NOTbe changed. For eg: If irate = 10 and min 5 then irate = 10 and min will be = 5 (No Change)
	- If min is either (0 or blank), then replace the value in Min with the iRate value.

- We have to specify value for conditional column in case of Horizontal files.
	- We have to execute a query in `rat_global_Charge_setting` table.
	- If we found the value of `bMandatory` column as 'Y' we will set the conditional column as 'M'
	- In all other cases we will set the value as 'C'.

## Retrying Hung Jobs

If the current pod is waiting on a previous job which has hung, then we:
1. Kill the pod executing the hung job using the lookup in `grdb_Job` table
2. Process the hung job first
3. Then process the current job
4. Then quit the pod based on `HealthService`

### Definition of Hung Job

The following criteria should match with a job to consider it as a hung job or dead job.

- We should be waiting for that job based on the waitloop system.
- The customer name of that job should match with current customer.
- The sheet type (FOB / PLC / OFR) of that job should match with current sheet type
- The time stamp of `tHeartbeat` column in job table should be older more than the value of `heartbeatFrequency` configured in `config.yaml` file

###  Algorithm

- Fetch message from SQS queue
- If we can process the message
	- Declare an array jobs_to_do for job ids to process
	- Create main job object from current job ID
	- Check if we have a hung job
	- If we have a hung job then add the hung job ID to the array to process
	- Add the current job ID to the same array
	- Iterate through the array of job IDs
		- If the job is already picked up by other pod then skip it
		- If the job is not active
			- Set the job status as inactive
			- Delete the message from queue
			- Skip the current job ID
		- Process the current job
- Delete all processed messages from queues


## Prioritized Job Processing

We have to prioritize a job based on the customer name, which will be configured by the client.

- In `config.yaml` file, we have two sections that is `sqsPriority` and `priority`.
- In `sqsPriority` section we have to add the url of priority queues, that is already created. The number of priority queues you can have is virtually unlimited.
	For example: 
	-	`priority1QueueUrl: https://sqs.XXXXXXXXXXXXXXXXXXXXXXX.amazonaws.com/XXXXXXXXXXXXXXXXXXXXXXX/grdb-priority-jobs-1`
  	-	`priority2QueueUrl: https://sqs.XXXXXXXXXXXXXXXXXXXXXXX.amazonaws.com/XXXXXXXXXXXXXXXXXXXXXXX/grdb-priority-jobs-2`
- In `priority` section we have to add a list of customer names on priority number based on our requirements.
	For Example:
	-	`priority1: AGILITY, STANDARD`
  	-	`priority2: FEDEX`


### Lambda Trigger Prioritization
- The number of priority queues and the number of priority URLs should match otherwise it will show an error
- The lambda trigger for upload files will check the priority of current customer and add the job message to the appropriate priority SQS queue.
- The trigger will also add a dummy message to common queue to ensure WPA scales up the pods.

### SQS Listener Prioritization
- The SQS listener will look for jobs in order of priority (eg: first check priority 1 queue, then check priority 2 queue, etc)
-  Whenever it can find a message it will fetch the message from the appropriate priority queue, and also fetch a message from the common queue
- Once the processing is done we delete the message from the priority queue, as well as delete any dummy message from the common queue

### Algorithm

- Start an infinite loop
	- Iterate through SQS queue list
		- if found a message
			- Get out of the iteration
	- Maintain a list of receipt handles from current queue as well as from common queue
	- Process the message to get required information like job ID, file path etc
	- If we can process the message
		- Create object of AppGlobal class
		- Create main job object of AppJob class with current job ID
		- Check if we have a hung job
		- If we have a hung job 
			- Then add the job ID in the list of jobs to process
		- Add the current job ID in the list of jobs to process
		- Iterate through the list of job ids
			- If any other pod is processing it
				- Go to the start of the loop
			- If current job is not active 
				- Change the status of the current job
				- Delete all receipt handles
				- Go to the start of the loop
			- Start processing the current job
	- Delete all receipt handles
	


## Log Output

> Note: This is different from [Logging](#logging)!

### Correct Log 

Correct Log is a CSV file that contains a list of all the correct rows as per [Rule Validation](#rule-validation).

- It will always be in vertical-CSV format.
- Filename format: `/root/<uploader>/folder/<csv_name>_success.zip `
- ZIP file will contain: `<csv_name>_success.csv`

#### Algorithm of Correct log
- Iterate through all rates
	- if current rate is validated
		- prepare a list of header fields value
		- if rate has charges
			- iterate through all charges
				- if charge is valid
					- then prepare a list of current charge fields value
					- merge the list of header and charge values. e.g. [header + charge]
					- append the merged list to correct logs list
		- else if rate has no charges
			- append the only list of header fields value to correct logs list
- Now, encode the correct logs list to CSV
### Error Log

Error Log is a CSV file that contains a list of all the invalid rows as per [Rule Validation](#rule-validation).

- It will be in vertical-CSV or horizontal-CSV format, depending on the input type.
- Filename format: `/root/<uploader>/folder/<csv_name>_error.zip `
- ZIP file will contain: `<csv_name>_error.csv`

#### Algorithm of Error log
- Iterate through all rates
	- if current rate has errors or waring's
		- Concatenate the error and warning messages of current rate and store in the dictionary with key `Exception Details`.
		- Get macrovalidated values of current rate (prepare a dictionary object where key is the csv column field name and value is the macrovalidated value of that field)
		- Finally, append the generated dictionary object to the error logs list
	
## Log Upload

> Note: This is different from [Logging](#logging)!

Log Upload handles uploading of the above [Log Output](#log-output) to a third party FTP server.

It only happens if the user who uploaded the job is authorized to upload to the FTP server (if the bucket folder is mentioned in the `config.yaml` > `externalUsers` list)

- If any correct log was generated, save that into FTP 

- If any error log was generated, save that into FTP 




## Logging

Extensive logging is available. More logs are printed during local testing than on cloud, to reduce the log data generated and prevent junk and redundant information from going into permanent cloud log storage.

Logs are in the following format:

- `Memory Used` - `Module`: `Message`

Sample logs during insertion of records:
```
Info: 199 MB - Insertion: Starting to insert 6680 PLC rates
Info: 199 MB - Inserting PLC row 1 of 6680 - AGILITY - 0 sec - 0 reads, 0 writes
Info: 199 MB - Inserting PLC row 2 of 6680 - AGILITY - 10 sec - 11 reads, 3 writes
Info: 199 MB - Inserting PLC row 3 of 6680 - AGILITY - 40 sec - 46 reads, 3 writes
Info: 199 MB - Inserting PLC row 4 of 6680 - AGILITY - 40 sec - 46 reads, 3 writes
```


## Debug and Release

**Debugging** is easily done on local machine using VS Code and its integrated Python debugger:

- Local testing pipeline has been developed which allows you to specifically check any local CSV or data file and run the entire processing on it.
- Logs will be printed to the debug console.
- For setup see the last sections of this readme.

**Releases** are done on AWS Kubernetes cluster:

- Deployment is done from a deployment machine that runs the deployment scripts (see Installation Guide for more info).
- Deployment consists of: creating a docker image of python SQS listener and pushing to AWS ECR (Lambda functions are deployed separately)
- Logging is sent to CloudWatch and can be seen under the log group name of the latest cluster.
- See FAQ Q2 and Q9 in Troubleshooting Guide for steps on viewing SQS listener logs.


