import io
import json
import msgpack
from framework.cloud.storage.AwsS3Service import AwsS3Service
from framework.system.FileService import FileService
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService

class JsonLoader:

	# Load a JSON file from the local disk
	@staticmethod
	def load(path):
		bytes = FileService.read_bytes(path)
		size = len(bytes)
		result = json.loads(bytes)
		return result, size

	# Load a JSON file either from S3 bucket (online mode)
	# or from the local disk (local testing mode)
	# The local input CSV path can be configured in `system_config.py`
	@staticmethod
	def load_cloud(bucket, filekey):

		# load the JSON file using JSON module
		if AppConfig.LOCAL_TESTING:
			result, size = JsonLoader.load(AppConfig.LOCAL_INPUT_FILE)
		else:
			s3 = AwsS3Service.get_client()
			LogService.log(f"S3: Load JSON file from {str(bucket)} : {str(filekey)}")
			content = s3.get_object(Bucket=bucket, Key=filekey)['Body'].read()
			bytes_io = io.BytesIO(content)
			size = bytes_io.getbuffer().nbytes
			result = json.loads(content)

		return result, size