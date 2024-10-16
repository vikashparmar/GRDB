### Validate User for API based on the configuration

- We validate Users for APIs, based on the data we have on `gen_Configuration` table.

#### The Process

- To check if the version of an API is allowed for an user, we match the iUserID, iProgramID, cCode as `VERSION` and cValue with the table.
- To check the data type, (i.e JSON or XML) is allowed for an user, we match the iUserID, iProgramID, cCode as `DATATYPE` and cValue with the table.
- To check, if an user is allowed for push notification, we match the iUserID, iProgramID, cCode as `MEMBER_ENDPOINT` and cValue with the table.
- To cheeck the email where we have to send email notification, we fetch cValue, by matching the iUserID, iProgramID, cCode as `NOTIFICATION_EMAIL` with the table.

### Implement Timeout for Token Expiry

- In our config file config.yaml, we have added a key `tokenExpirySeconds` inside `auth` section. Here you can add a timeout value in seconds.
- During token validation, we are validating current time against the timestamp we have for the token in `grdb_Gen_AuthToken` table. If current time exceeds the timeout value then the token will be expired.

## Logging Request and Response

### New table for logging all the request and responses

- The `grdb_API_requestLogs` table is created to store the request response from API.

#### The Process
- Once the request is received, usual validations and job table insertion take place
- Once schema validation is done for the request, a file with the original request is created and uploaded to S3 to the bucket stored in config `S3_API_ORIGINAL_REQUEST_BUCKET`
- A corresponding record is inserted in the table `grdb_API_requestLogs` with all the necessary fields.

