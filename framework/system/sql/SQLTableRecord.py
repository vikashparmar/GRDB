from framework.system.sql.SQLRowRecord import SQLRowRecord

class SQLTableRecord:
	tableName:str
	rows:list

	def __init__(self) -> None:
		self.tableName = None
		self.rows = []

