# Upload File Trigger

**A lambda function that executes whenever user uploads a file into the "upload bucket" on S3.**

Script: `serverless/files/uploadFileTrigger.py`

- Obtain information like user name, bucket, file size etc from uploaded file.
- If the file is NOT in the error folder:
	- Get metadata like customer name, file type from the file path
	- If found that the priority array is blank
		- Create an entry in the job table, assign an error message and exit
	- If the current customer is mentioned in a priority queue:
		- Select the given priority for this file
	- Else:
		- Select the last priority for this file
	- Create an entry in job table
- If the file is in the error folder:
	- Print an message
- Copy the file from upload bucket to processing bucket
- If the file is NOT in the error folder:
	- Add the job message into the selected queue
	- Add a dummy message into the common queue