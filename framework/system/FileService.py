import os
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService

class FileService:


	# Read file as bytes
	@staticmethod
	def read_bytes(path, max_bytes=0):
		try:
			in_file = open(path, "rb") # opening for [r]eading as [b]inary
			if max_bytes > 0:
				data = in_file.read(max_bytes)
			else:
				data = in_file.read()
			in_file.close()
			return data
		except Exception as e:
			LogService.error("Error while reading binary file", e)
			return None


	# Write file as bytes
	@staticmethod
	def write_bytes(path, data):
		try:
			out_file = open(path, "wb") # open for [w]riting as [b]inary
			out_file.write(data)
			out_file.close()
		except Exception as e:
			LogService.error("Error while writing binary file", e)
			return None


	# Returns true if the given local filepath exists
	@staticmethod
	def file_exists(path):
		return os.path.exists(path)

	# Returns the local file size in bytes
	@staticmethod
	def file_size(path):
		return os.path.getsize(path)
