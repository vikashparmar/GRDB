import zlib
from framework.system.LogService import LogService

class ZLibDecoder:

	# Decompress the given Zlib stream into the actual text
	@staticmethod
	def decodeText(stream:bytes) -> str:
		try:
			return str(zlib.decompress(stream), 'utf-8')

		except Exception as e:
			LogService.error("Error while decoding ZLIB", e)
			return None


# test code:
#
#	sample = '{"data": [{"rate": 1, "charge": "header", "message": "Member code is incorrect (The Correct Member Code is \'SHPT\') ", "code": 1009}, {"rate": 1, "charge": "header", "message": "Restricted port pair for Auto Transmission. ", "code": 1003}, {"rate": 2, "charge": "header", "message": "Member code is incorrect (The Correct Member Code is \'SHPT\') ", "code": 1009}, {"rate": 2, "charge": "header", "message": "Restricted port pair for Auto Transmission. ", "code": 1003}, {"rate": 3, "charge": "header", "message": "Member code is incorrect (The Correct Member Code is \'SHPT\') ", "code": 1009}, {"rate": 3, "charge": "header", "message": "Restricted port pair for Auto Transmission. ", "code": 1003}, {"rate": 4, "charge": "header", "message": "Member code is incorrect (The Correct Member Code is \'SHPT\') ", "code": 1009}, {"rate": 4, "charge": "header", "message": "Restricted port pair for Auto Transmission. ", "code": 1003}, {"rate": 5, "charge": "header", "message": "Member code is incorrect (The Correct Member Code is \'SHPT\') ", "code": 1009}, {"rate": 5, "charge": "header", "message": "'
#	
#	b = ZLibEncoder.encodeText(sample)
#	t = ZLibDecoder.decodeText(b)
#	
#	if b == t:
#		a = 3