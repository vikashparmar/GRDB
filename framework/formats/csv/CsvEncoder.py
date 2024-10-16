from framework.AppConfig import AppConfig
from framework.system.LogService import LogService

class CsvEncoder:

	# Encode 2D array of cells as CSV string
	@staticmethod
	def encode_csv_list(headers, rows):
		result = []
	
		# output the headers
		for header in headers:
			result.append(header)
			result.append(',')
	
		result.append('\n')
	
		# per row
		for row in rows:
	
			# per cell
			for value in row:
				vs = str(value)
				if value is None or vs == 'nan' or len(vs) == 0:
					result.append(',')
				else:
	
					# correctly escape values if they contain special characters
					if '"' in vs:
	
						# escape quotes and add quotes around cell
						result.append('"')
						result.append(vs.replace('"', '""'))
						result.append('",')
	
					elif ',' in vs:
	
						# add quotes around cell
						result.append('"')
						result.append(vs)
						result.append('",')
	
					else:
						result.append(vs)
						result.append(',')
	
			result.append('\n')
	
		return str.join('', result)


	# Encode array of objects as CSV string
	@staticmethod
	def encode_csv(lisOfDicts):
		result = []

		# output the headers
		for k, v in lisOfDicts[0].items():
			if '.' in k:
				kList = k.split('.')
				if kList[-1].isnumeric() == True:
					result.append('.'.join(kList[:-1]))
					result.append(',')
				else:
					result.append(k)
					result.append(',')
			else:
				result.append(k)
				result.append(',')

		result.append('\n')

		# per row
		for rows in lisOfDicts:

			# per cell
			for k, v in rows.items():

				vs = str(v)
				if vs == 'nan' or len(vs) == 0:
					result.append(',')
				else:

					# correctly escape values if they contain special characters
					if '"' in vs:

						# escape quotes and add quotes around cell
						result.append('"')
						result.append(vs.replace('"', '""'))
						result.append('",')

					elif ',' in vs:

						# add quotes around cell
						result.append('"')
						result.append(vs)
						result.append('",')

					else:
						result.append(vs)
						result.append(',')

			result.append('\n')

		return str.join('', result)
