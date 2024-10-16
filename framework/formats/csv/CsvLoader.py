import io
import pandas
import time
from framework.cloud.storage.AwsS3Service import AwsS3Service
from framework.AppConfig import AppConfig
from framework.system.FileService import FileService
from framework.system.LogService import LogService

#-----------------------------------------------------
# NOTE: This file adds a dependency to `pandas` library
#-----------------------------------------------------


class CsvLoader:

	# Load a CSV file from the local disk
	@staticmethod
	def load(path):
		data_frame = pandas.read_csv(path, dtype='str')
		# data_frame = CsvLoader._removeUnnamedCols(data_frame)
		size = FileService.file_size(path)
		return data_frame, size


	# Load a CSV file either from S3 bucket (online mode)
	# or from the local disk (local testing mode)
	# The local input CSV path can be configured in `system_config.py`
	@staticmethod
	def load_cloud(bucket, filekey):

		# load the CSV file using pandas, all cells as strings
		if AppConfig.LOCAL_TESTING:
			data_frame, size = CsvLoader.load(AppConfig.LOCAL_INPUT_FILE)
		else:
			s3 = AwsS3Service.get_client()
			LogService.log(f"S3: Load CSV file from {str(bucket)} : {str(filekey)}")
			s3_file = s3.get_object(Bucket=bucket, Key=filekey)['Body'].read()
			bytes_io = io.BytesIO(s3_file)
			size = bytes_io.getbuffer().nbytes
			data_frame = pandas.read_csv(bytes_io, dtype='str')
			# data_frame = CsvLoader._removeUnnamedCols(data_frame)

		return data_frame, size

	@staticmethod
	def load_cloud_retry_loop(retries, bucket, filekey):
		
		# retry 15 times x 2 seconds so retries for 30 seconds
		for retry in range(1,retries):
			try:
				data_frame, size = CsvLoader.load_cloud(bucket, filekey)
				
				if data_frame is not None:
					return data_frame, size
				
			except Exception as e:

				# log error and retry
				LogService.error(f"Error loading CSV file! Attempt: {retry}", e)
			
			# pause 10 seconds
			time.sleep(10)

		# if unable to connect to DB, log error and fail app
		LogService.error("Exhausted all attempts to load CSV file")

		raise
