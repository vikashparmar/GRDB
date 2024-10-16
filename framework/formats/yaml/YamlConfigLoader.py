import yaml

class YamlConfigLoader:

	def __init__(self, filename) -> None:
		with open(filename) as f:
			self.data = yaml.safe_load(f)

	def getBool(self, group, name, default_value = False):
		data = self.data
		if group in data and name in data[group]:

			# load and return if boolean value
			val = data[group][name]
			if isinstance(val, bool):
				return val

			# if not boolean the parse as string
			str_val = str(val).strip().lower()
			return str_val == "1" or str_val == "true" or str_val == "yes"

		return default_value

	def getStr(self, group, name, default_value = ''):
		data = self.data
		if group in data and name in data[group]:

			# load and return string value trimmed
			val = data[group][name]
			str_val = str(val).strip()
			return str_val

		return default_value

	def getInt(self, group, name, default_value = 0):
		data = self.data
		if group in data and name in data[group]:

			# load and return if numeric value
			val = data[group][name]
			if isinstance(val, float) or isinstance(val, int):
				return val

			# if not boolean the parse as integer
			str_val = str(val).strip()
			return int(str_val)

		return default_value


	def getDict(self, group):
		data = self.data
		if group in data:

			# load and return if dict
			val = data[group]
			if isinstance(val, dict):
				return val

		# by default return empty dict
		return {}

	
	def getList(self, group, name):
		data = self.data
		val_array = []
		value_string = None

		# if the key has been found on that group
		if group in data and name in data[group]:
			
			# load the data
			value_string = self.getStr(group, name)
			if value_string:
				value_string = value_string.split(',')
				val_array = [value.strip() for value in value_string if value]

		return val_array
			

	def getMultilineList(self, group, name):
		data = self.data
		if group in data and name in data[group]:

			# load and return if list
			val = data[group][name]
			if isinstance(val, list):
				return val

		# by default return empty list
		return []