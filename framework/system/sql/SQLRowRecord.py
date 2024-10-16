class SQLRowRecord:
	recordType:str
	tableName:str
	rowID:int
	rowData:dict
	whereData:dict # only filled for UPDATE WHERE clauses and DELETE WHERE clauses

	def __init__(self) -> None:
		self.recordType = None
		self.tableName = None
		self.rowID = None
		self.rowData = None
		self.whereData = None