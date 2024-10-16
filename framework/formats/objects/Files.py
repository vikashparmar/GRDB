import os
from io import BytesIO
from framework.formats.objects.Primitives import Primitives

class Files:

	@staticmethod
	def saveOutputFile(filenameExt, data):

		# create output dir
		if not os.path.exists('output'):
			os.makedirs('output')

		# get flat bytes
		if isinstance(data, BytesIO):
			data = data.getbuffer()

		# save file locally
		if Primitives.isStr(data):
			option = "w"
		else:
			option = "wb"
		with open("output/" + filenameExt, option) as file:
			file.write(data)