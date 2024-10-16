from framework.SSI.acknowledgment.AckFTPUploader import AckFTPUploader
from framework.SSI.statusInsertion.SSIInsertionRepository import SSIInsertionRepository
from datetime import datetime
from framework.SSI.tables.CarrierStatusTable import CarrierStatusTable
from framework.SSI.tables.FileLogTable import FileLogTable
from timeit import default_timer as timer
from framework.AppConfig import AppConfig
from framework.SSI.job.AppJob import AppJob
from framework.SSI.tables.SSIJobTable import SSIJobTable
from framework.SSI.core.AppDatabase import AppDatabase
from framework.system.LogService import LogService

class SSIInsertionManager:

	@staticmethod
	def insert(job:AppJob):
		db = job.db

		#--------------------------------------------------
		#					Change job status
		#--------------------------------------------------
		errors = []

		# Update the jobs table, set status as "INSERTING"
		SSIJobTable.set_status_inserting(job.db)


		#--------------------------------------------------
		#				Insert X12 or XML
		#--------------------------------------------------
		# Check if file type is X12
		if job.file_type == 'x12':
			# Read the X12 file and sent for insertion
			if CarrierStatusTable.insert(job.x12_obj, db):
				LogService.print("Record inserted in tra_Carrier_status table")
			else:
				LogService.print("Error while inserting record to tra_Carrier_status table")
				errors.append("Error while inserting record to tra_Carrier_status table")

		elif job.file_type == 'xml':
			# Run the insertion scripts
			errors = SSIInsertionManager.runXmlJsonInsertion(job)


		#--------------------------------------------------
		#				Change job status
		#--------------------------------------------------
		# If errors while inserting the log the message accordingly and delete the message
		if len(errors) > 0:
			
			SSIJobTable.set_status_insertion_error(db, str(errors))
			FileLogTable.update(db, iFileLogID=AppJob.file_log_id, cErrorMessage=str(errors), tEndDateTime=datetime.now(), cCurrentStatus=-1)
			# LogService.LogService.print('Error while inserting file to DB')
			LogService.print('Error while inserting file to DB ', errors)
		else:
			SSIJobTable.set_status_inserted(db)
			FileLogTable.update(db, iFileLogID=AppJob.file_log_id, tEndDateTime=datetime.now(), cCurrentStatus=1)
			# LogService.LogService.print('file processed Sucessfully')
			LogService.print('file processed Sucessfully')




	# The function to run the insertion scripts
	@staticmethod
	def runXmlJsonInsertion(job:AppJob):
		db = job.db
		
		# Run a loop on all the shipmentStatus/TransShipment details in the file
		for commonStatus in job.statuses:
			errors = SSIInsertionRepository.insert(db, commonStatus, job)
			LogService.print('\n')

			LogService.print(errors)

			# Move the file to a different directory if the status code is 10 
			# and customers wants to hold the booking confirmation until they receive shipment statuses
			# LogService.print(cStatusCode, type(cStatusCode), cStatusCode == 10)
			status_code = commonStatus.cStatusCode
			if status_code == '10':
				# Check in the DB if member setting is available
				receiver = job.cReceiver
				res = db.master().select_all_safe('SELECT count(*) FROM wwa.sei_Member_setting where ccode = "copy_bkg_confirmation_file" and cValue=%s;', (receiver,))
				if int(res[0][0]) > 0:
					SSIInsertionManager.upload_file_to_path(job, filepath, '/home/wwaonline/temp/booking_confirmation')



		# send acknowledgement based on sender ID
		sender = job.cSender

		query = """SELECT COUNT(*) FROM sei_Member_setting INNER JOIN sei_Member ON sei_Member_setting.iMemberID = sei_Member.iMemberID
			WHERE sei_Member_setting.cCode = "acknowledge_xml" AND sei_Member.cCompanycode = %s"""
		
		res = db.master().select_all_safe(query, (sender,))
		if res[0][0] > 0:
			
			AckFTPUploader.upload(job)

		return errors



	# ideally upload_file_to_path function should upload file to a path on SFTP Server. 
	# Since we don't have a server now, just saving the file to a local dir
	@staticmethod
	def upload_file_to_path(job, filepath, desPath):
		LogService.print(f"File : '{filepath.split('/')[filepath.split('/').__len__()-1]}' Uploaded to path : '{desPath}'")
