import json
from json2xml import json2xml
import requests
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService

class PushService:

	_JSON_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

	@staticmethod
	def send(title:str, request:dict, url:str, data_format:str):
		try:
			response = ''
			# skip if no URL provided
			if url is None:
				LogService.log(f"Push: Skipped sending push notification '{title}' to '{str(url)}'")
				return

			# send push notification
			LogService.log(f"Push: Sending push notification '{title}' to '{str(url)}'")
			
			if data_format == 'XML':
				response = str(json2xml.Json2xml(request, wrapper="pushNotification", attr_type=False).to_xml())
			elif data_format == 'JSON':
				response = json.dumps(request)

			json_data = response
			response = requests.post(url, data=json_data, headers=PushService._JSON_HEADERS)
			if response.status_code == 200:
				return True, str(response.text)
			else:
				return False, str(response.text)

		except Exception as e:
			LogService.error("Error in sending push notification", e)
			return False, str(e)
