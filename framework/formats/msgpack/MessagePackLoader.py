import io
import msgpack
from framework.cloud.storage.AwsS3Service import AwsS3Service
from framework.system.FileService import FileService
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService

class MessagePackLoader:

	# Load a MessagePack file from the local disk
	@staticmethod
	def load(path):
		bytes = FileService.read_bytes(path)
		size = len(bytes)
		result = msgpack.unpackb(bytes)
		return result, size

	# Load a MessagePack file either from S3 bucket (online mode)
	# or from the local disk (local testing mode)
	# The local input CSV path can be configured in `system_config.py`
	@staticmethod
	def load_cloud(bucket, filekey):

		# load the MessagePack file using msgpack module
		if AppConfig.LOCAL_TESTING:
			result, size = MessagePackLoader.load(AppConfig.LOCAL_INPUT_FILE)
		else:
			s3 = AwsS3Service.get_client()
			LogService.log(f"S3: Load MessagePack file from {str(bucket)} : {str(filekey)}")
			s3_file = s3.get_object(Bucket=bucket, Key=filekey)['Body'].read()
			bytes_io = io.BytesIO(s3_file)
			size = bytes_io.getbuffer().nbytes
			bytes = bytes_io.read()
			result = msgpack.unpackb(bytes)

		return result, size