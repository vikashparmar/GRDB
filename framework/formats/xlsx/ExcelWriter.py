import xlsxwriter
from framework.formats.xlsx.ExcelSheet import ExcelSheet

class ExcelWriter:

	@staticmethod
	def save(data:list[ExcelSheet], filepath):
		
		# creating workbook and worksheet
		workbook = xlsxwriter.Workbook(filepath)
		row_num = 0
		# For the outer most list, the data structure of the will look like the below
		# [ ExcelSheet[ExcelCell, ExcelCell, ExcelCell],  ExcelSheet[ExcelCell, ExcelCell, ExcelCell] ExcelSheet[ExcelCell, ExcelCell, ExcelCell] ]
		
		worksheet = workbook.add_worksheet()
		for sheet in data:			

			# For the inner list of ExcelCell
			for index in range(len(sheet.Rows)):
				format_dict:dict = {}

				# Enabling the available formats
				if 'Bold' in sheet.Rows[index].__dict__:
					format_dict.update({'bold': sheet.Rows[index].Bold})
				if 'Italic' in sheet.Rows[index].__dict__:
					format_dict.update({'italic': sheet.Rows[index].Italic})
				if 'Underline' in sheet.Rows[index].__dict__:
					format_dict.update({'underline': sheet.Rows[index].Underline})

				cell_format = workbook.add_format(format_dict) 

				# writing the table
				if index == 0:
					worksheet.write(row_num, 0, sheet.Name, cell_format)
					row_num += 1

				# skipping the first cell containing the table name
				if index > 0:
					for j in range(len(sheet.Rows[index].Value)):
						col_num = j
						worksheet.write(row_num, col_num, sheet.Rows[index].Value[j], cell_format)
					row_num += 1

			row_num += 2

		# Closing the workbook
		workbook.close()
