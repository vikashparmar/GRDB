from framework.formats.objects.Strings import Strings

class FilePaths:

	@staticmethod
	def getExt(path): 
		return Strings.afterLast(path, '.').lower()

	@staticmethod
	def getFilenameExt(path): 
		if '\\' in path:
			return Strings.afterLast(path, '\\')
			
		if '/' in path:
			return Strings.afterLast(path, '/')
			
		return path

	@staticmethod
	def removeExt(path): 
		return Strings.beforeLast(path, '.')
