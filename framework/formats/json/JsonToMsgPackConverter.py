import msgpack
import os
from datetime import date, datetime
from framework.formats.msgpack.MessagePackSaver import MessagePackSaver
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService

#----------------------------------------------------------
# NOTE: None of the methods in this file should use `pandas`
#----------------------------------------------------------


class JsonToMsgPackConverter:


	# CONVERT JSON REQUEST INTO MESSAGE PACK FILE AND SAVE INTO LOCAL FILE
	@staticmethod
	def convert(data):
		try:
		
			# create the file name as per the convention SHPT_TYPE_CUST_HHMMSSsss_FILENAME.msgpack
			today = date.today()
			server_date = today.strftime("%Y-%m-%d")
			timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
			timestamp = timestamp[:18]
			file_name = str(data['header']['memberSCAC']) + '_' + str(data['type']) + '_' + str(data['header']['customer']) + '_' + timestamp + '.msgpack'
			
			# save as msgpack
			(err, msg, fn, ofn) = MessagePackSaver.save(data, file_name)
			
			return (err, msg, fn, ofn)
			
		except Exception as e:
			print(e)
			return False, "Error while trying to convert JSON to msgpack", None, None
