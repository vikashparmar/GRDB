from framework.SSI.core.databaseConnection import connection
from pypika import Query, Table, Field

class FileLogger():

	def __init__(self, db):
		self.db = db
		self.cFileName = None
		self.cFilePath = None
		self.cDestFileName = None
		self.cDestFilePath = None
		self.cS3Incoming = None
		self.cS3OutGoing = None
		self.iProgramID = 23
		self.cFileFormat = None
		self.cFileType = None
		self.iErrorcode = None
		self.cErrorMessage = None
		self.cSender = None
		self.cReceiver = None
		self.cOutAck = None
		self.tFileDateTime = '0000-00-00 00:00:00'
		self.tStartDateTime = '0000-00-00 00:00:00'
		self.tEndDateTime = '0000-00-00 00:00:00'
		self.cCustomeralias = None
		self.iStatus = 1
		self.iEnteredby = 0
		self.tEntered = '0000-00-00 00:00:00'
		self.iUpdatedby = 0
		self.tUpdated = '0000-00-00 00:00:00'


	# def log(self):
	#	 self.db.insert_file_log(self)
	
def update_file_log(*args, **kwargs):
	# args[0].update_file_log(kwargs)

	wei_File_Log_new = Table('wei_File_Log_new')
	query = Query.update(wei_File_Log_new).where(wei_File_Log_new.iFileLogID == kwargs['iFileLogID'])

	for column in kwargs:
	  query = query.set(column, kwargs[column])
		
	connection.DatabaseService.batch_execute(query.get_sql().replace('"', ''), None)
	