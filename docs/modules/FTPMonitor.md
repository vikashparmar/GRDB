# FTP Monitor

A script has been made as FTP monitoring tool. As the name suggests, it checks a preconfigured file path on a ftp server, for files. 

- Script Path: GRDB/automation/monitorFtp.py

- It checks a preconfigured file path, to fetch files, and then it uploads the files to s3 bucket to get the files processed.

- Login to a FTP server
- Check for files
- Upload the files to S3 bucket for processing

#### The Algorithm

- Fetch the FTP details like host name, port, user name password etc
- Login to the FTP server using the details fetched
- Iterate through the all configured users
	- Iterate through the files that has been found
		- If the current file is .ok file
			- Now look for the original file by removing .ok extension
			- If the original file exists
				- If the file is zipped, find the real CSV filename
				- If we are not processing a job having same csv file and same date
					- Create an entry in job table for current file
					- If file size exceeded the allowed size limit then exit
					- If the file is zipped then unzip the file
					- Download the actual file into memory
					- Upload the file to S3 bucket
					- Delete files from FTP server	
