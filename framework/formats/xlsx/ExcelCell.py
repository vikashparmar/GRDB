class ExcelCell:
	Value:any
	BackColor:int   # this should be str
	TextColor:int  # this should be str
	Bold:bool 
	Italic:bool
	Underline:bool 
	MergedRows:int 
	MergedCols:int

	def __init__(self) -> None:
		Value = None
		BackColor = None 
		TextColor = None
		Bold = False
		Italic = False
		Underline = False
		MergedRows = None
		MergedCols = None