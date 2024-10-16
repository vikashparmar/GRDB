# methods to lookup keys and values from dictionaries
class DictLookup:

	@staticmethod
	def hasAllKeys(dict, keys, clean = False) -> bool:
		for key in keys:
			if clean:
				key = key.strip().lower()
			if key not in dict:
				return False
		return True

	@staticmethod
	def hasKey(dict, key, clean = False) -> bool:
		if key is None:
			return False
		if clean:
			key = key.strip().lower()
		return key in dict

	@staticmethod
	def hasKey2(dict, key1, key2, clean = False) -> bool:
		if key1 is None or key2 is None:
			return False
		if clean:
			key1 = key1.strip().lower()
			key2 = key2.strip().lower()
		key = key1 + "|" + key2
		return key in dict

	@staticmethod
	def hasKey3(dict, key1, key2, key3, clean = False) -> bool:
		if key1 is None or key2 is None or key3 is None:
			return False
		if clean:
			key1 = key1.strip().lower()
			key2 = key2.strip().lower()
			key3 = key3.strip().lower()
		key = key1 + "|" + key2 + "|" + key3
		return key in dict

	@staticmethod
	def hasKey4(dict, key1, key2, key3, key4, clean = False) -> bool:
		if key1 is None or key2 is None or key3 is None or key4 is None:
			return False
		if clean:
			key1 = key1.strip().lower()
			key2 = key2.strip().lower()
			key3 = key3.strip().lower()
			key4 = key4.strip().lower()
		key = key1 + "|" + key2 + "|" + key3 + "|" + key4
		return key in dict

	@staticmethod
	def getValue(dict, key, clean = False):
		if key is None:
			return None
		if clean:
			key = key.strip().lower()
		if key in dict:
			return dict[key]
		return None

	@staticmethod
	def getValue2(dict, key1, key2, clean = False):
		if key1 is None or key2 is None:
			return None
		if clean:
			key1 = key1.strip().lower()
			key2 = key2.strip().lower()
		key = key1 + "|" + key2
		if key in dict:
			return dict[key]
		return None

	@staticmethod
	def getValue3(dict, key1, key2, key3, clean = False):
		if key1 is None or key2 is None or key3 is None:
			return None
		if clean:
			key1 = key1.strip().lower()
			key2 = key2.strip().lower()
			key3 = key3.strip().lower()
		key = key1 + "|" + key2 + "|" + key3
		if key in dict:
			return dict[key]
		return None

	@staticmethod
	def getValue4(dict, key1, key2, key3, key4, clean = False):
		if key1 is None or key2 is None or key3 is None or key4 is None:
			return None
		if clean:
			key1 = key1.strip().lower()
			key2 = key2.strip().lower()
			key3 = key3.strip().lower()
			key4 = key4.strip().lower()
		key = key1 + "|" + key2 + "|" + key3 + "|" + key4
		if key in dict:
			return dict[key]
		return None

	
	@staticmethod
	def getValueAsStr(dict, prop, trim=False):
		if prop in dict and dict[prop] is not None:
			if trim:
				return str(dict[prop]).strip()
			else:
				return str(dict[prop])
		else:
			return None

	@staticmethod
	def getValueAsFloat(dict, prop):
		# WGP-841
		if prop in dict and dict[prop] is not None and dict[prop] != '':
			return float(dict[prop])
		else:
			return None

	@staticmethod
	def getValueAsBool(dict, prop):
		if prop in dict and dict[prop] is not None:

			# try parsing as string
			val = str(dict[prop]).lower()
			if val == 'y' or val == 'true' or val == '1' or val == 'yes':
				return True
			if val == 'n' or val == 'false' or val == '0' or val == 'no':
				return False

			# assume is bool
			return bool(dict[prop])
		else:
			return None
