import shutil
from gzip import GzipFile
from io import BytesIO
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService

class GZipEncoder:

	# Compress the given bytes into a GZIP archive
	@staticmethod
	def encode(data):
		try:
			stream = BytesIO()

			with GzipFile(fileobj=stream, mode='wb') as gz:
				shutil.copyfileobj(data, gz)
			
			stream.seek(0)

			return stream
		except Exception as e:
			LogService.error("Error while encoding GZIP", e)
			return None
