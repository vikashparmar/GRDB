from zipfile import ZipFile
from io import BytesIO
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService

class ZipDecoder:
	
	# Read a single file from a ZIP archive, and return its bytes
	@staticmethod
	def getFileData(archive_bytes:bytes, filename_in_archive) -> bytes:
		try:
			# convert bytes to file-like object
			archive = BytesIO(archive_bytes)

			# unpack the ZIP archive
			with ZipFile(archive, 'r') as archive:

				# pick out specific file
				with archive.open(filename_in_archive) as file:

					# read file data as bytes
					data = file.read()
					return data

		except Exception as e:
			LogService.error("Error while unpacking ZIP to get file '"+filename_in_archive+"'", e)
			return None