class Urls:

	@staticmethod
	def combine(path1, path2): 
		if path1.endswith('/'):
			path1 = path1[:-1] 
		
		if path2.startswith('/'):
			path2 = path2[1:]
		return path1 + '/' + path2