# from pypika import Query, Table, Field
from framework.SSI.core.AppDatabase import AppDatabase
from framework.SSI.job.AppJob import AppJob

from datetime import datetime

class SSIJobTable:
	
	@staticmethod
	def set_status_inserting(db:AppDatabase):
		db.master().update_record("wei_Jobs", "iJobID", AppJob.iJobID, {
			"cErrorMessage" : None,
			"tEndTime" : None,
			"cCurrentStatus" : "INSERTING"
		})
	
	@staticmethod
	def set_status_insertion_error(db:AppDatabase, message):
		db.master().update_record("wei_Jobs", "iJobID", AppJob.iJobID, {
			"cErrorMessage" : message,
			"tEndTime" : datetime.now(),
			"cCurrentStatus" : "INSERTION ERROR"
		})
	
	@staticmethod
	def set_status_validation_error(db:AppDatabase, message):
		db.master().update_record("wei_Jobs", "iJobID", AppJob.iJobID, {
			"cErrorMessage" : message,
			"tEndTime" : datetime.now(),
			"cCurrentStatus" : "VALIDATION ERROR"
		})
	
	@staticmethod
	def set_status_inserted(db:AppDatabase):
		db.master().update_record("wei_Jobs", "iJobID", AppJob.iJobID, {
			"cErrorMessage" : None,
			"tEndTime" : datetime.now(),
			"cCurrentStatus" : "INSERTED"
		})
	