from framework.formats.xlsx.ExcelCell import ExcelCell
from framework.AppConfig import AppConfig
from framework.system.sql.SQLRecordType import SQLRecordType
from framework.formats.xlsx.ExcelSheet import ExcelSheet

class DatabaseRecordToExcelConverter:
	
	@staticmethod
	def convert(table_records:dict, filepath):
		if AppConfig.LOCAL_TESTING:
			from framework.formats.xlsx.ExcelWriter import ExcelWriter
			outer_list = []

			last_table_name = ''
			last_columns = []
			row_id = 1

			for table_name in table_records.keys():
				# 1. Table name
				table_cell = ExcelCell()
				table_cell.Value = table_name
				table_cell.Bold = True

				new_sheet = ExcelSheet(table_name)
				new_sheet.Rows.append(table_cell)
				new_sheet.Name = table_name

				values_list = []
				for row in table_records[table_name].rows:

					# 2. for column names
					# if last columns not equal to current columns or 
					# last table name not equals to current table name
					# then add new columns other wise skip it
					if last_table_name != table_name or last_columns != row.rowData.keys():
						column_cell = ExcelCell()
						col_names = []
						col_names.append('ID')
						for key, value in row.rowData.items():
							col_names.append(key)
						column_cell.Value = col_names
						column_cell.Bold = True
						new_sheet.Rows.append(column_cell)

						last_table_name = table_name
						last_columns = row.rowData.keys()

					# 3. for values
					value_cell = ExcelCell()
					values_list.append(row_id)
					row_id += 1
					# For insert / update cases
					if row.recordType in [SQLRecordType.INSERT_ROW, SQLRecordType.UPDATE_ROW]:
						iter_items = row.rowData
					# For delete cases we will store the data from where clauses
					else:
						iter_items = row.whereData

					for key, value in iter_items.items():
						values_list.append(value)
					value_cell.Value = values_list
					new_sheet.Rows.append(value_cell)
					values_list = []

				outer_list.append(new_sheet)

			ExcelWriter.save(outer_list, filepath)

				

				

				

