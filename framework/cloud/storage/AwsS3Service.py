import boto3
from botocore.client import Config
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService

class AwsS3Service:


	client = None
	resource = None


	# Returns an S3 client, by creating the client on the first call
	# and reusing the same client for all the other calls
	@staticmethod
	def get_client(new_resource=False):

		if new_resource:
			if AwsS3Service.resource is None:
				try:
					AwsS3Service.resource = boto3.resource('s3',
						region_name=AppConfig.AWS_REGION,
						aws_access_key_id=AppConfig.AWS_KEY1,
						aws_secret_access_key=AppConfig.AWS_KEY2,
						config=Config(signature_version='s3v4'),
						endpoint_url='https://s3.{}.amazonaws.com'.format(AppConfig.AWS_REGION))
				except Exception as e:
					LogService.error("S3: Cannot connect to S3 Resource", e)
					return False
				LogService.log("S3: Successfully created S3 Resource")
			return AwsS3Service.resource

		else:
			if AwsS3Service.client is None:
				try:
					if AppConfig.IS_LAMBDA:
						AwsS3Service.client = boto3.client('s3',
							region_name=AppConfig.AWS_REGION,
							aws_access_key_id=AppConfig.AWS_KEY1,
							aws_secret_access_key=AppConfig.AWS_KEY2,
							config=Config(signature_version='s3v4'),
							endpoint_url='https://s3.{}.amazonaws.com'.format(AppConfig.AWS_REGION))
					else:
						AwsS3Service.client = boto3.client('s3',
							region_name=AppConfig.AWS_REGION,
							aws_access_key_id=AppConfig.AWS_KEY1,
							aws_secret_access_key=AppConfig.AWS_KEY2)
				except Exception as e:
					LogService.error("S3: Cannot connect to S3", e)
					return False
				LogService.log("S3: Successfully created S3 client")
			return AwsS3Service.client




	# Moves a file within an S3 bucket from one path to another
	@staticmethod
	def move_file(bucket, old_file_path, new_file_path):
		try:
			s3 = AwsS3Service.get_client()
			copy_source = {'Bucket': bucket, 'Key': old_file_path}
			LogService.log(f"S3: Move file from {str(bucket)} : {str(old_file_path)} to {str(new_file_path)}")
			s3.copy_object(CopySource=copy_source, Bucket=bucket, Key=new_file_path)
			s3.delete_object(Bucket=bucket, Key=old_file_path)
			LogService.log(f"S3: Successfully moved file to S3 bucket: {bucket}")
			return True
		except Exception as e:
			LogService.error(f"S3: Error while moving file to S3 bucket: {bucket}", e)
			return False


	# Copies a file within an S3 bucket from one path to another
	@staticmethod
	def copy_file(src_bucket, old_file_path, destination_bucket, new_file_path):
		try:
			s3 = AwsS3Service.get_client()
			copy_source = {'Bucket': src_bucket, 'Key': old_file_path}
			s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=new_file_path)
			print(f"Successfully copied file to {destination_bucket}/{new_file_path}")
			return True
		except Exception as e:
			LogService.error("S3: Error while copying file to processing bucket", e)
			return False



	# Upload a file from local file system into S3 bucket
	@staticmethod
	def uploadFileFromDisk(file_name, object_name, bucket_name=None):
		
		print(file_name,object_name,bucket_name)
		s3 = AwsS3Service.get_client()
		try:
			response = s3.upload_file(file_name, bucket_name, object_name)
			return True
		except Exception as e:
			LogService.error("S3: Error uploading local file '"+file_name+"' to S3 as '"+bucket_name + "/" + object_name+"'", e)
			return False



	# Upload a file-like object from memory into S3 bucket
	@staticmethod
	def uploadFileFromMemory(file_data, object_name, bucket_name=None):
		s3 = AwsS3Service.get_client()
		try:
			response = s3.upload_fileobj(file_data, bucket_name, object_name)
			return True
		except Exception as e:
			LogService.error("S3: Error uploading File-Like object to S3 as '"+bucket_name + "/" + object_name+"'", e)
			return False



	# Get the file size of a file in S3 bucket
	@staticmethod
	def get_file_size(bucket, key):
		try:
			s3 = AwsS3Service.get_client(True)
			objectins3 = s3.Object(bucket, key)
			try:
				print(f"Detected file size: {str(objectins3.content_length)} bytes")
				file_size = objectins3.content_length
				return file_size
			except Exception as e:
				print(e)
				return None
		except Exception as e:
			LogService.error("S3: Error getting file size of S3 object '"+bucket + "/" + key+"'", e)
			return None