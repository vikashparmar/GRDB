
# extend this class to provide app-specific templated processing
class BaseEmailProcessor:
	
	def process(self, body:str, templateData:dict, metadata:dict):
		return body