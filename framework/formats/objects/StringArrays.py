from framework.formats.objects.Strings import Strings
from framework.formats.objects.Primitives import Primitives

#methods that operate on arrays of strings
class StringArrays:
	
	@staticmethod
	def lowercase(list:list[str]):
		new_list = []
		for v in list:
			new_list.append(v.strip().lower())
		return new_list

	@staticmethod
	def cleanPandasColnames(names:list[str]):
		result = []
		lastnum = 0
		for name in names:

			remove_suffix = False
			if '.' in name:
				suffix = Strings.afterLast(name,'.')

				if Primitives.isValidInt(suffix):
					remove_suffix = True

			if remove_suffix:
				result.append(Strings.beforeLast(name,'.'))
			else:
				result.append(name)
		return result
