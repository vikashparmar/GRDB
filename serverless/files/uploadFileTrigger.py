# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import os
import json
from framework.cloud.storage.AwsS3Service import AwsS3Service
from framework.cloud.message.AwsSqsQueueService import AwsSqsQueueService
from framework.grdb.processor.InputFileMetadata import InputFileMetadata
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.AppConfig import AppConfig
from framework.grdb.core.tables.JobTable_Lambdas import JobTable_Lambdas
from framework.grdb.core.tables.JobTable_SQS import JobTable_SQS
from framework.grdb.core.AppDatabase import AppDatabase
	
# Trigger function for S3 bucket upload which adds job table record and SQS message


def send_sqs_message(job_id, bucket, key, current_queue):
	message = {"job_id": job_id, "bucket": bucket, "path": key}
	result = AwsSqsQueueService.send_message(current_queue, json.dumps(message), str(job_id))
	result = AwsSqsQueueService.send_message(AppConfig.SQS_INPUT_QUEUE, '{}', str(job_id))
	print(message)
	print(result)



def main(event, context):
	# Handler function for initial bucket trigger
	try:
	
		# find job ID and uploaded filename from S3 file metadata
		record = event['Records'][0]
		bucket = record['s3']['bucket']['name']		# example: dev-wwa-services
		key = record['s3']['object']['key'] 		# example: oganbhoj/SHPT_PLC_CUST_20210924_122734444.csv
		key_parts = key.split('/')
		key_username = key_parts[0]					# example: oganbhoj
		key_filename = key_parts[-1]				# example: SHPT_PLC_CUST_20210924_122734444.csv
		key_fileext = key_filename.split('.')[1]	# example: "csv" / "msgpack"

		# print job and file
		print(f"Detected newly uploaded file! Need to add entry in job table...")
		print(f"Bucket name: {bucket}")
		print(f"File path: {key}")
		print(f"File name: {key_filename}")
		
		# get environment vars (app settings)
		new_bucket = AppConfig.S3_PROCESSING_BUCKET
		resource_name = AppConfig.APP_RESOURCENAME


		# get uploaded file size
		file_size = AwsS3Service.get_file_size(bucket, key)

		# check if file is NOT in error folder
		if key_parts[-2] != 'error':

			status, customer_name, file_type, member, extension = InputFileMetadata.getFilenameMetadata(key_filename)

			# check if file format is supported
			file_format_supported = InputFileMetadata.fileExtSupported(extension)

			# create a unique file key for storing in processing bucket
			final_key = InputFileMetadata.generateFileKey(key_username, resource_name, key_filename, file_format_supported)
			job_status = "QUEUED" if file_format_supported else "FILE_FORMAT_ERROR"

			# connect to DB or exit with REST API error if unable to connect
			db, err = ApiDatabase.connect()
			if err is not None:
				return err

			# If the length of Priority Queue Urls does not match with the 
			# length of Priority Arrays then throw exception
			if AppConfig.PRIORITY_ARRAY_LIST is None:
				job_id = JobTable_Lambdas.onBucketUpload_insertOrUpdateJob(db,
				key_filename, key_username, job_status, member, file_type,
				customer_name, new_bucket, final_key, file_size, 0)	

				error_message = "Check the number of Priority queues and the number of priorities set in the config file. It should be same"
				JobTable_SQS.jobCrashed(db, job_id, error_message)
				print("Error: The length of Priority Queue Urls does not match with the length of Priority Arrays")

				AppDatabase.dispose()

				return 0


			# calculating Job priority based on customer
			current_queue = None
			current_priority = 0
			for i in range(len(AppConfig.SQS_PRIORITY_QUEUE_LIST)):
				if customer_name in AppConfig.PRIORITY_ARRAY_LIST[i]:
					current_queue = AppConfig.SQS_PRIORITY_QUEUE_LIST[i]
					current_priority = i+1

			# setting default priority and queue if customer is not found in arrays
			if current_queue is None:
				current_queue = AppConfig.SQS_NONPRIORITY_QUEUE
				current_priority = 0

			print(f"current queue is : {current_queue}")
			print(f"current priority is : {current_priority}")

			# create or update job in job table
			job_id = JobTable_Lambdas.onBucketUpload_insertOrUpdateJob(db,
				key_filename, key_username, job_status, member, file_type,
				customer_name, new_bucket, final_key, file_size, current_priority)			

		else:
			print("File uploaded to error folder, skipping job creation")

		# copy file from initial bucket to processing bucket
		print(f"Copying file {bucket}/{key} ==> {new_bucket}/{final_key}")
		AwsS3Service.copy_file(bucket, key, new_bucket, final_key)
		
		# check if file is NOT in error folder
		if key_parts[-2] != 'error':

			# Add SQS message so processing begins
			send_sqs_message(job_id, new_bucket, final_key, current_queue)

		AppDatabase.dispose()

	except Exception as e:
		print("Error while handling initial upload bucket trigger")
		print(e)
	return