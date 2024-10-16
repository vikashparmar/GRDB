import json
import xmltodict

#----------------------------------------------------------
# NOTE: None of the methods in this file should use `pandas`
#----------------------------------------------------------

class XmlToJsonConverter:

	# CONVERT XML REQUEST INTO JSON DATA FOR PROCESSING
	@staticmethod
	def convert(data):
		data_dict = xmltodict.parse(data)
		json_data = json.dumps(data_dict)
		return json_data
