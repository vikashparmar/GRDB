from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService

class ZipEncoder:

	# Compress the given bytes into a ZIP archive
	@staticmethod
	def encode(data, filename_in_archive):
		try:
			stream = BytesIO()

			with ZipFile(stream, 'w', ZIP_DEFLATED) as zip:
				zip.writestr(filename_in_archive, data)
			
			stream.seek(0)

			return stream
		except Exception as e:
			LogService.error("Error while encoding ZIP", e)
			return None