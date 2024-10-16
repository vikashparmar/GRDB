import pandas
import os
from framework.cloud.storage.AwsS3Service import AwsS3Service
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService

#-----------------------------------------------------
# NOTE: This file adds a dependency to `pandas` library
#-----------------------------------------------------


class JsonToCsvConverter:

	def convert(bucket, key):
		
		# CREATING THE S3 CLIENT
		s3_client = AwsS3Service.get_client()

		# BUCKET AND KEY(FILE NAME WITH PATH) PASSED AS ARGUMENTS
		object_name_json = key
		bucket = bucket
		object_name = object_name_json.replace(".json", ".csv")
		print("New File Name after conversion to CSV = " + object_name)

		# RETRIEVING FILE EXTENSION FROM FILE PATH
		file_extension = key.split('/')[len(key.split('/')) - 1].split('.')[1]

		if file_extension == 'json':
			try:
				print("JSON file uploaded. Starting conversion to CSV format.")

				# GETTING THE JSON FILE FROM S3		
				obj = s3_client.get_object(
					Bucket=bucket,
					Key=object_name_json
				)

				# READING DATA OF THE JSON FILE
				data = obj['Body']
				print("Starting to read the json file")
				df = pandas.read_json(data)
				print("Starting to write to csv file")

				export_name = '/tmp/export.csv'
				dirname = os.path.dirname(export_name)
				if not os.path.exists(dirname):
					os.makedirs(dirname)

				# CONVERTING TO CSV FILE
				df.to_csv(export_name, index=None)
				print("Starting to upload the csv file to s3")
				response = s3_client.upload_file(export_name, bucket, object_name)
				print("Starting to delete json file from s3")
				response = s3_client.delete_object(Bucket=bucket, Key=object_name_json)
				print(response)
				return object_name

			except Exception as e:
				print("Error while converting json to csv")
				print(e)
				return object_name_json

		else:
			print("Not a json file. No need of conversion.")
			return object_name_json