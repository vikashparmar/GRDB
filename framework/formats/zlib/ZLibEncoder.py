import zlib
from framework.system.LogService import LogService

class ZLibEncoder:

	# Compress the given text into a Zlib stream
	@staticmethod
	def encodeText(text:str) -> bytes:
		try:
			return zlib.compress(text.encode('utf-8'))

		except Exception as e:
			LogService.error("Error while encoding ZLIB", e)
			return None
