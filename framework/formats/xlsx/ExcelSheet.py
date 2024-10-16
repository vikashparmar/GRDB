class ExcelSheet:
	Name:str
	Rows:list

	def __init__(self, table_name) -> None:
		self.Name = table_name
		self.Rows = []
