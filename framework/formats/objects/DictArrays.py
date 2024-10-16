import datetime
from framework.formats.objects.DictProcessor import DictProcessor


class DictArrays:

	@staticmethod
	def replaceProps(dicts, replaceMap, reverse=False):
		new_dicts:list = []

		if reverse:
			replaceMap = DictProcessor.reverse(replaceMap)
		
		for obj in dicts:
			new_dicts.append(DictProcessor.replaceProps(obj, replaceMap))

		return new_dicts

	@staticmethod
	def fillValues(values, multiple):
		if multiple:
			for value in values:
				for key, val in value.items():
					if val is None:
						value.update({key : ''})
					elif isinstance(val, datetime.datetime):
						value.update({key : str(val)})

		else:
			for key, val in values.items():
				if val is None:
					values.update({key : ''})
				elif isinstance(val, datetime.datetime):
					values.update({key : str(val)})

		return values