import json
from json2xml import json2xml
from framework.formats.xml.XmlToJsonConverter import XmlToJsonConverter
from framework.grdb.core.AppDatabase import AppDatabase
class RestApiService:
		
	@staticmethod
	def headers():
		return {"Access-Control-Allow-Headers": "Content-Type",
		"Access-Control-Allow-Origin": "*",
		"Access-Control-Allow-Credentials": "true",
		"Access-Control-Allow-Methods": "OPTIONS,POST,GET",
		"Cache-control": "no-store",
		"Pragma": "no-cache"}


	# interpret the request in JSON/XML
	# returns (data, request_format, error_response)
	@staticmethod
	def decode_request(event, request_tag, response_tag):

		# get the data from request
		request_str = event['body']
		request_format = None
		if len(request_str) > 0 and request_str[0] == '<':
		
			#----------------------------------------
			#				XML ONLY
			#----------------------------------------
			request_format = 'XML'
			try:
				print("XML received in API request")
				# convert XML to JSON for processing
				data = XmlToJsonConverter.convert(request_str)
				# convert JSON to object
				data = json.loads(data)

				data = data[request_tag]
				# extract charges array
				# data['charges'] = data['charges']['charge']
				return data, request_format, None
			except Exception as e:
				# for invalid requests we return status 400
				return None, request_format, RestApiService.failure_response(400, request_format, response_tag, "Invalid XML request recieved. Please ensure the request is valid XML syntax.")
			
		elif len(request_str) > 0 and request_str[0] == '{':
		
			#----------------------------------------
			#				JSON ONLY
			#----------------------------------------
			request_format = 'JSON'
			try:
				print("JSON received in API request")
				data = json.loads(request_str)
				return data, request_format, None
			except Exception as e:
				# for invalid requests we return status 400
				return None, request_format, RestApiService.failure_response(400, request_format, response_tag, "Invalid JSON request recieved. Please ensure the request is valid JSON syntax.")
			
		else:
			#----------------------------------------
			#				UNKNOWN FORMAT
			#----------------------------------------
			return None, None, RestApiService.failure_response(400, 'JSON', response_tag, "Unknown request format. Request must be in XML or JSON format")


	# generate an error object in JSON/XML for a single schema error
	@staticmethod
	def schema_error_response(format, main_xml_tag, code, message):
		schema_errors = [{"charge":"envelope", "code":code, "message":message}]
		response = {"success":True,"schemaValid":False,"schemaErrors":schema_errors}
		return RestApiService.encode_response(400, format, main_xml_tag, response)
			

	# generate an error object in JSON/XML for multiple schema errors
	@staticmethod
	def schema_errors_response(format, main_xml_tag, schema_errors):
		response = {"success":True,"schemaValid":False,"schemaErrors":schema_errors}
		return RestApiService.encode_response(400, format, main_xml_tag, response)
			

	# generate an error object in JSON/XML for system exception with HTTP status 500
	@staticmethod
	def failure_response(http_code, format, main_xml_tag, message):
		response = {"success":False,"errorCode":http_code,"errorMessage":str(message)}
		return RestApiService.encode_response(http_code, format, main_xml_tag, response)
			

	# generate a response object in JSON/XML with given body dictionary
	@staticmethod
	def encode_response(http_code, format, main_xml_tag, body):
		if format == 'XML':
			response = json2xml.Json2xml(body, wrapper=main_xml_tag, attr_type=False).to_xml()
		elif format == 'JSON':
			print("Response: ", body)
			if (type(body) is dict) or (type(body) is list):
				# convert dict to string
				response = json.dumps(body)
			else:
				response = body
		AppDatabase.dispose()
		return {"statusCode":http_code, "headers": RestApiService.headers(), "body":response}
		