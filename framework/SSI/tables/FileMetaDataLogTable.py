from framework.SSI.core.AppDatabase import AppDatabase
from pypika import Query, Table, Field
from datetime import datetime
from framework.SSI.job.AppJob import AppJob

class FileMetaDataLogTable:

	@staticmethod
	def insert(db:AppDatabase, references, values):
		
		wei_File_Meta_Data_Log = Table('wei_File_Meta_Data_Log')
		query = Query.into(wei_File_Meta_Data_Log).columns('iFileLogID', 'cReferencetype', 'cReference', 'tEntered')

		for index, reference in enumerate(references):
			query = query.insert(AppJob.file_log_id, reference[1:], values[index], datetime.now())
		db.batch_execute(query.get_sql().replace('"', ''), None)