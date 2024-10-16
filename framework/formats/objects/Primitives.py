class Primitives:

	@staticmethod
	def isStr(value): 
		return value is not None and isinstance(value, str)

	@staticmethod
	def isNumber(value): 
		return value is not None and (isinstance(value, float) or isinstance(value, int))

	@staticmethod
	def valueExists(value): 
		# WGP-842
		return value is not None and value != '' and value != 'null'

	@staticmethod
	def parseInt(value, defaultValue=0):

		# default value if invalid input
		if value is None or value == '':
			return defaultValue

		# check if natively int/float type
		if isinstance(value, int):
			return value
		if isinstance(value, float):
			return int(value)

		# convert to int
		try:
			return int(float(value))
		except:
			return defaultValue
			
	@staticmethod
	def parseFloat(value, defaultValue=0):

		# default value if invalid input
		if value is None or value == '':
			return defaultValue

		# check if natively int/float type
		if isinstance(value, float):
			return value
		if isinstance(value, int):
			return float(value)

		# convert to float
		try:
			return float(value)
		except:
			return defaultValue

	@staticmethod
	def lowercaseAny(value):
		if isinstance(value, int) or isinstance(value, float):
			return value
		else:
			return value.strip().lower()

	@staticmethod
	def isValidInt(value):

		# check if blank
		if value == '' or value is None:
			return False

		# check if natively int/float type
		if isinstance(value, int) or isinstance(value, float):
			return True

		# convert to int and check
		try:
			value = int(float(value))
		except:
			return False
		return True

	@staticmethod
	def isValidNumber(value):

		# check if blank
		if value == '' or value is None:
			return False

		# check if natively int/float type
		if isinstance(value, int) or isinstance(value, float):
			return True

		# convert to float and check
		try:
			value = float(value)
		except:
			return False
		return True

	@staticmethod
	def isValidBool(value):

		# check if blank
		if value == '' or value is None:
			return False

		# check if natively bool type
		if isinstance(value, bool):
			return True

		# convert to string and check
		try:
			value = str(value).strip().lower()
			return value == 'true' or value == 'false'
		except:
			pass
		return False


	@staticmethod
	def objHasProp(obj, prop):
		try:
			if hasattr(obj, prop):
				v = getattr(obj, prop)
				return v is not None and v != ""
			if prop in obj:
				v = obj[prop]
				return v is not None and v != ""
		except:
			pass
		return False

	# if the value is a float with value of 10.0 it will return 10
	@staticmethod
	def roundIfInteger(value):

		# default value if invalid input
		if value is None or value == '':
			return 0

		# check if natively int/float type
		fval = float(value)
		if float(round(fval)) == fval:
			return int(value)
		else:
			return fval

	@staticmethod
	def convert_to_xml_value(value):
		if value in [True, 'True']:
			return 'true'
		elif value in [False, 'False']:
			return 'false'
		elif value in [None, 'None', 'NONE']:
			return ''
		else:
			return value

	@staticmethod
	def roundIfInteger(value):

		# default value if invalid input
		if value is None or value == '':
			return 0

		# check if natively int/float type
		fval = float(value)
		if float(round(fval)) == fval:
			return int(value)
		else:
			return fval

	@staticmethod
	def getDefaultString(value, default_string=''):
		if value in [None, 'None']:
			return default_string		
		return value