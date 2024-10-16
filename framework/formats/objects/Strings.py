class Strings:

	@staticmethod
	def exists(value): 
		return value is not None and isinstance(value, str) and len(value) > 0

	@staticmethod
	def ensure(value, default_value = ''): 
		if value is None:
			return default_value
		else:
			return value

	@staticmethod
	def beforeLast(str, sep, return_all = True):
		index = str.rfind(sep)
		if index > -1:
			return str[0:index]
		elif return_all:
			return str
		else:
			return ''

	@staticmethod
	def beforeFirst(str, sep, return_all = True):
		index = str.find(sep)
		if index > -1:
			return str[0:index]
		elif return_all:
			return str
		else:
			return ''

	@staticmethod
	def afterLast(str, sep, return_all = True):
		index = str.rfind(sep)
		if index > -1:
			return str[index+len(sep):]
		elif return_all:
			return str
		else:
			return ''

	@staticmethod
	def afterFirst(str, sep, return_all = True):
		index = str.find(sep)
		if index > -1:
			return str[index+len(sep):]
		elif return_all:
			return str
		else:
			return ''

	@staticmethod
	def replaceTemplated(template:str, var_name:str, defaultValue:str, value):

		value = str(value)

		# reset default value if not exists
		if value == '' or value is None or str(value) == '[None]':
			value = defaultValue

		# replace templated var
		return template.replace(var_name, value)

	# Get the parts of a file path, by splitting on \ or / char
	@staticmethod
	def splitPath(path):
		if '/' in path:
			return path.split('/')
		elif '\\' in path:
			return path.split('\\')
		else:
			return [path]
		
	@staticmethod
	def exceptBetween(str:str, start:str, end:str) -> str:
		startIndex = str.find(start)
		endIndex = str.rfind(end)
		if startIndex > -1 and endIndex > -1:
			result =str.replace(str[(startIndex + len(start)) :endIndex], '')
			return result
		else:
			return str