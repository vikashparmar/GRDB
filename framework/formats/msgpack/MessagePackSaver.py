import os
import json
from framework.AppConfig import AppConfig
import msgpack
from datetime import datetime
class MessagePackSaver:

	# CONVERT JSON REQUEST INTO MESSAGE PACK FILE AND SAVE INTO LOCAL FILE
	@staticmethod
	def save(data, file_name):
		try:
		
			original_file_name = file_name
			
			# /tmp/ is needed to create files in aws environment. AWS is readonly, /tmp/ is a temp folder to create files 
			file_name = '/tmp/' + file_name
			dirname = os.path.dirname(file_name)
			if not os.path.exists(dirname):
				os.makedirs(dirname)
			
			# create a file and write to msg pack 
			with open(file_name, "wb") as outfile:
				packed = msgpack.packb(data)
				outfile.write(packed)

			return True, "Converted JSON to msgpack", file_name, str(original_file_name)
			
		except Exception as e:
			print(e)
			return False, "Error while trying to convert JSON to msgpack", None, None
	
	@staticmethod
	def saveOriginalRequest(data, schema_response, file_name):
		try:

			original_file_name = file_name

			# /tmp/ is needed to create files in aws environment. AWS is readonly, /tmp/ is a temp folder to create files 
			file_name = '/tmp/' + file_name
			dirname = os.path.dirname(file_name)
			if not os.path.exists(dirname):
				os.makedirs(dirname)

			# create a file and write to msg pack 
			with open(file_name, "w") as outfile:
				final_data ={"request":data,"response":schema_response}
				if AppConfig.ENCODE_REQUEST_LOGGING_FILE == True:
					packed = msgpack.packb(final_data)
				else:
					packed =  json.dumps(final_data)
				outfile.write(str(packed))
			return True, "Converted JSON to msgpack", file_name, str(original_file_name)

		except Exception as e:
			print(e)
			return False, "Error while trying to convert JSON to msgpack", None, None