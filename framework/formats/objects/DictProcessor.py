import re

class DictProcessor:
	
	@staticmethod
	def reverse(dict:dict):
		new_dict:dict = {}
		for key in dict:
			val = dict[key]
			new_dict[val] = key
		return new_dict

	@staticmethod
	def replaceProps(dict:dict, replaceMap:dict, reverse=False):
		new_dict:dict = {}

		if reverse:
			replaceMap = DictProcessor.reverse(replaceMap)
		
		for key in dict:
			val = dict[key]
			if key in replaceMap:
				new_key = replaceMap[key]
				new_dict[new_key] = val
			else:
				new_dict[key] = val

		return new_dict

	@staticmethod
	def replaceStrProps(str:str, replaceMap:dict, reverse=False):
		new_str:str = str

		if reverse:
			replaceMap = DictProcessor.reverse(replaceMap)
		
		for old_key in replaceMap:
			new_key = replaceMap[old_key]

			# replace using 'whole words'
			new_str = re.sub(r"\b%s\b" % old_key, new_key, new_str)

		return new_str
