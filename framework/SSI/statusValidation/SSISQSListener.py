# Use case of the file
# Scan Validation Queue for messages
# Pull the file from S3 bucket
# Read file and get the root node, status code
# Get validation cases from tra_status_files_validation_map table
# Send the file to Insertion queue if valid

# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# import libraries
import logging, boto3, json, configparser, os, ast, sys, random
from hashlib import blake2b, md5
from datetime import datetime
from dict2xml import dict2xml
from timeit import default_timer as timer
from datetime import timedelta
from framework.SSI.statusInsertion.SSIInsertionManager import SSIInsertionManager
from framework.SSI.statusValidation.SSIValidationRuleEngine import SSIValidationRuleEngine
from framework.SSI.statusValidation.SSIValidations import SSIValidations
from framework.system.LogService import LogService
from framework.cloud.storage.AwsS3Service import AwsS3Service
from framework.SSI.core.AppDatabase import AppDatabase
from framework.AppConfig import AppConfig
from framework.SSI.job.AppJob import AppJob
from framework.SSI.job.SSICommonStatus import SSICommonStatus
from framework.SSI.tables.SSIJobTable import SSIJobTable
from framework.formats.xml.XmlDocumentReader import XmlDocumentReader
from framework.tracking.notifyEmail.EmailNotificationManager import EmailNotificationManager

class SSISQSListener:
	def __init__(self):
		pass		
		
	# def create_aws_resources(self):
	#	 #Create all AWS Resources that will be used
	#	 sess = boto3.session.Session(aws_access_key_id=self.config['AWS']['ACCESS_KEY'], aws_secret_access_key=self.config['AWS']['SECRET_ACCESS_KEY'], region_name=self.config['AWS']['REGION'])
	#	 sqs = sess.resource("sqs")
	#	 self.s3 = sess.resource('s3')
	#	 self.validation_queue = sqs.get_queue_by_name(QueueName=self.config['AWS']['VALIDATION_QUEUE'])
	#	 self.insertion_queue = sqs.get_queue_by_name(QueueName=self.config['AWS']['INSERTION_QUEUE'])
	
	def get_message(self, job:AppJob):

		# Receive message from the Validation Queue
		messages = self.validation_queue.receive_messages(MaxNumberOfMessages=1)
		bucket, filepath = (None, None)

		# If any messages present then it will be returned else None
		job.sqs_message = messages[0]
		LogService.print("Reading the message...")
		body = json.loads(job.sqs_message.body)
		job.file_path = body['filepath']
		job.file_bucket = body['bucket']
		job.sqs_message = job.sqs_message
		job.job_id = str(body['job_id'])
		LogService.print(f"Job Id is : {job.job_id}")
		LogService.print(f"Filepath in S3 : {job.file_path}")
		return True
	
	def loadFile(self, db:AppDatabase, job:AppJob):
		
		# remove this random job id code once we've data coming from job_table/SQS Queue
		job.job_id = random.randint(0, 10000)
		AppJob.iJobID = job.job_id
		AppJob.file_log_id = AppConfig.LOCAL_FILE_LOG_ID


		#--------------------------------------------------
		#					Load the file
		#--------------------------------------------------
		file_object = None
		if AppConfig.LOCAL_TESTING:
			# Get the file from the disk
			f = open(job.file_path, "rb")
			file_object = f.read()
			f.close()
		else:
			# Get the file from S3
			s3client = AwsS3Service.get_client(True)
			file_object = s3client.Object(job.file_bucket, job.file_path)
			file_object = file_object.get()['Body'].read()


		#--------------------------------------------------
		#				Convert JSON to XML
		#--------------------------------------------------
		# If the file type is JSON then convert it to XML
		if job.file_path.endswith('.json'):
			LogService.print('file received is a JSON file')
			LogService.LogService.print('file received is a JSON file')
			file_object = dict2xml(json.loads(file_object), wrap='ShipmentStatus')



		#--------------------------------------------------
		#				Decode X12 format
		#--------------------------------------------------
		if 'ShipmentStatus' not in file_object.decode("utf-8"):
			job.file_type = 'x12'
			job.loadFromX12(file_object)
			
		else:
			job.file_type = 'xml'
			job.xmlDocument = XmlDocumentReader(file_object)
			job.loadFromXml()
			job.isTransShipment = SSICommonStatus.isTransshipment(job.xmlDocument)
			
			# Validate the Envelope tag
			if not SSIValidations.validateEnvelope(job, db):
				LogService.print('Envelope Validations failed')
				SSIJobTable.set_status_validation_error(job.db, 'Envelope Validations Failed')
				return False
				
		return True
	
	
	def validate(self, db:AppDatabase, job:AppJob):

		# if the file received is from "edi_saco_prod" then check if similar booking from Shipco is reveiced. 
		# If so then skip all the insertion and validations and just send the file to phionex



		# Store all the failed validations in "failed_validations" list for logging purposes
		job.failed_validations = []



		# Convert XML into object model
		job.statuses = []
		for StatusDetails in (job.xmlDocument.getXmlTags('./TSStatusDetails' if job.isTransShipment else './ShipmentStatusDetails')):
			# Create validations object and get the status code to run validations
			xmlDocument = XmlDocumentReader(StatusDetails)
			commonStatus = SSICommonStatus.fromXml(xmlDocument, job.isTransShipment, db)
			job.statuses.append(commonStatus)
		
		if job.cSender == 'edi_saco_prod':			
			if job.statuses[0].cStatustype == 'e':
				res = db.master().select_all_safe('SELECT count(1) AS ncount FROM track_ShipmentDetails WHERE cBookingnumber=%s AND istatus >= 0', (commonStatus.cCommunicationReference,))
				if res[0][0] > 0:
					res = db.master().select_all_safe('SELECT cExtendedcode FROM sei_Member_setting where ccode="wwa_status_to_phoenix";')
					if len(res) > 0:
						self.upload_file_to_path(res[0][0])
					return "skip_validation_insertion"


		# Run validations on all the Shipment Details in the file
		for commonStatus in job.statuses:
			validations = SSIValidationRuleEngine(commonStatus, db, xmlDocument)

			if not commonStatus.cStatusCode:
				error = {
							"arrival_notice_number" : commonStatus.arn, 
							"booking_number" : commonStatus.cBookingnumber, 
							"status_code" : None, 
							"status_type" : None, 
							"customer_alias" : "", 
							"errors" : ["Status code not present"]
						}
				job.failed_validations.append(error)
				return False
			LogService.print(f"Status code is {commonStatus.cStatusCode}")

			# Fetch all the validation rules for the specific status code
			rules = []

			# If status code is 450 - Update ARN Request then validate few things
			if int(commonStatus.cStatusCode) == 450:

				# Check if all the values are present, If present then chek if PrevArrivalNoticeNumber is present in the DB
				if commonStatus.cHouseBillOfLadingNumber and commonStatus.arn and commonStatus.prev_arn:
					res = db.master().select_all_safe("SELECT COUNT(*) FROM track_ShipmentDetails WHERE cArrivalNoticeNumber=%s or cPrevArrivalNoticeNumber=%s", (commonStatus.prev_arn, commonStatus.prev_arn))

					# Validate the file if PrevArrivalNoticeNumber is present in the DB
					if res[0][0] > 0:
						return True
				
				return False

			# If the file type is Trans Shipment and the status code is in (51, 52, 53, 1051, 1052, 1053) then get the Trans Shipment Validation rules 
			# else get the Shipment Status Validation Rules
			if job.isTransShipment and int(commonStatus.cStatusCode) in (51, 52, 53, 1051, 1052, 1053):
				rules = db.master().select_all_safe('SELECT cRuleName, cConditions, tra_status_files_validation_map.bFileFails, cErrorLogInEmail, cErrorLogInDB FROM tra_status_files_validation_rules INNER JOIN tra_status_files_validation_map ON tra_status_files_validation_map.cValidations = tra_status_files_validation_rules.cRuleName WHERE tra_status_files_validation_map.iStatusCode = %s and tra_status_files_validation_rules.cRuleName like "TS_%";', (commonStatus.cStatusCode,))
				LogService.print("rules : ", rules)
			elif not job.isTransShipment:
				rules = db.master().select_all_safe('SELECT cRuleName, cConditions, tra_status_files_validation_map.bFileFails, cErrorLogInEmail, cErrorLogInDB FROM tra_status_files_validation_rules INNER JOIN tra_status_files_validation_map ON tra_status_files_validation_map.cValidations = tra_status_files_validation_rules.cRuleName WHERE tra_status_files_validation_map.iStatusCode = %s and cValidations not like "TS_%";', (commonStatus.cStatusCode,))
			
			# If status 27 is receivved then no validations should run
			if int(commonStatus.cStatusCode) == 27:
				LogService.print("No validations for status 27")
				return True

			# Check if the status type is Import or Export
			commonStatus.cStatustype = db.master().select_all_safe('SELECT cStatustype FROM gen_Status WHERE cStatuscode=%s', (commonStatus.cStatusCode,))
			commonStatus.cStatustype = commonStatus.cStatustype[0][0].lower() if commonStatus.cStatustype.__len__() > 0 else None

			# If no validations are present in the DB then show appropreate message
			if rules.__len__() == 0:
				LogService.print(f"No validations found for the status code : {commonStatus.cStatusCode}")

			temp_store = []
			# Run all the validations in a loop and if any validation fails store the details in "temp_store"
			for rule in rules:
				res = eval(rule[1])
				
				if res == True:
					LogService.print(f'{rule[0]} validation success')
				else:
					LogService.print(f'WARNING : {rule[0]} validation failed')
					if rule[2] == 1:
						err = commonStatus.temp_errors
						if err.__len__() > 0 : temp_store = temp_store + err

			# If any errors in "temp_store" then append it to "failed_validations" list
			if temp_store.__len__() > 0:
				if commonStatus.cStatustype == 'e':
					error = {
								"booking_number" : commonStatus.cBookingnumber, 
								"arrival_notice_number" : commonStatus.arn, 
								"status_code" : commonStatus.cStatusCode, 
								"status_type" : commonStatus.cStatustype, 
								"customer_alias" : "", 
								"errors" : []
							}
				elif commonStatus.cStatustype == 'i':
					error = {
								"arrival_notice_number" : commonStatus.arn, 
								"booking_number" : commonStatus.cBookingnumber, 
								"status_code" : commonStatus.cStatusCode, 
								"status_type" : commonStatus.cStatustype, 
								"customer_alias" : "", 
								"errors" : []
							}
				for val in temp_store:
					error['errors'].append(val)
				job.failed_validations.append(error)
		
		# Return True if "failed_validations" is empty else return False
		return False if job.failed_validations.__len__() > 0 else True
	
	def send_for_insertion(self, job:AppJob):

		# insert job
		SSIInsertionManager.insert(job)
		
		# delete message after insertion
		if not AppConfig.LOCAL_TESTING:
			LogService.print('deleting message')
			job.sqs_message.delete()
			LogService.print('message deleted\n\n')

	
	# ideally upload_file_to_path function should upload file to a path on SFTP Server. 
	# Since we don't have a server now, just saving the file to a local dir
	def upload_file_to_path(self, path):
		LogService.print(f"File : '{self.filename}' Uploaded to path : '{path}'")
	
	def similar_record_exist(self, db, commonStatus):
		# date = getXmlTagValue(self.root, './ShipmentStatusDetails/StatusDateTimeDetails/Date')
		# time = getXmlTagValue(self.root, './ShipmentStatusDetails/StatusDateTimeDetails/Time')
		# timezone = getXmlTagValue(self.root, './ShipmentStatusDetails/StatusDateTimeDetails/TimeZone')

		# status_date_time = parse(f"{date} {time} {timezone}") if date and time and timezone else ''
		# status_code = getXmlTagValue(self.root, './ShipmentStatusDetails/StatusCode')
		# port_of_discharge = getXmlTagValue(self.root, './ShipmentStatusDetails/RoutingDetails/PortOfDischarge')
		# place_of_delivery = getXmlTagValue(self.root, './ShipmentStatusDetails/RoutingDetails/PlaceOfDelivery')

		res = db.master().select_all_safe("""SELECT COUNT(*) FROM track_StatusDetails 
			INNER JOIN track_ShipmentDetails ON track_StatusDetails.cBookingNumber = track_ShipmentDetails.cBookingNumber
			WHERE track_StatusDetails.cStatusDateTime = %s and track_StatusDetails.cStatusCode = %s 
			AND track_ShipmentDetails.cPortOfDischarge = %s and track_ShipmentDetails.cPlaceOfDelivery = %s""", 
			(commonStatus.cStatusDateTime, commonStatus.cStatusCode, commonStatus.cPortOfDischarge, commonStatus.cPlaceOfDelivery,))
		if res[0][0] > 0:
			return True
		return False

	def local_test(self):

		db = AppDatabase()
		job = AppJob()
		job.db = db


		job.file_path = AppConfig.LOCAL_INPUT_FILES[0]
		self.filename = job.file_path.split('/')[job.file_path.split('/').__len__()-1]
		job.job_id = random.randint(0, 10000)
		LogService.print(f"job_id is {job.job_id}")

		read_successful = self.loadFile(db, job)

		# If message reading was successful then validate the file
		if read_successful:

			if job.file_type == 'xml':
				valid = self.validate(db, job)

				# If file is valid then send it for insertion else send a notification email
				if valid == "skip_validation_insertion":
					LogService.print("Validations and Insertions Skipped")
				elif valid:
					LogService.print("File Valid")
					self.send_for_insertion(job)
				else:
					LogService.print("File Invalid")
					EmailNotificationManager.send(db, job)

			elif job.file_type == 'x12':
				valid = SSIValidations.validate_carrier_booking(job)

				# If file is valid then send it for insertion else send a notification email
				if valid:
					LogService.print('File valid')
					self.send_for_insertion(job)
				else:
					LogService.print('File invalid')
					EmailNotificationManager.send(db)

# class job():
#	 # Initial values are set to None, values has to be updated before running the update()
#	 Sender = None
#	 Receiver = None
#	 CurrentStatus = None
#	 ErrorMessage = None
#	 JobID = None
#	 def __init__(self, db):
#		 db = db
	
	# Function to update the job status in the Database
	# def update(self):
	#	 db.update_job({'cErrorMessage' : self.ErrorMessage, 'cCurrentStatus' : self.CurrentStatus, 'cSender' : self.Sender, 'cReceiver' : self.Receiver, 'iJobID' : self.JobID})





# -------Entry Point To The Code--------
if __name__=="__main__":
	# global logger
	# logging.basicConfig(filename='files/validations.log', filemode='w', level=logging.DEBUG)
	# logger = logging.getLogger('sqs_listener')


	
	# Create sqs listener object
	listener = SSISQSListener()

	# Run local test if filepath argument is passed
	if AppConfig.LOCAL_TESTING:
		LogService.print('Running Local Test')
		start = timer()
		listener.local_test()
		end = timer()
		LogService.print(f"Time taken in seconds - {timedelta(seconds=end-start)}")
		exit()
	else:
		pass
		# listener.create_aws_resources()

		## Look of messages in an endless loop
		#LogService.print("Looking for messages...")
		#message_received = listener.get_message()
#
		## If message found then read the message and get the file type i.e. 'xml' or 'x12
		#if message_received:
		#	read_successful = listener.read_message()
#
		#	# If message reading was successful then validate the file
		#	if read_successful == 'xml':
		#		valid = listener.validate()
#
		#		# If file is valid then send it for insertion else send a notification email
		#		if valid:
		#			listener.send_for_insertion()
		#		elif valid == "skip_validation_insertion":
		#			LogService.print("Validations and Insertions Skipped")
		#		else:
		#			LogService.print("File Invalid")
		#			listener.send_notification_email()
		#	elif read_successful == 'x12':
		#		valid = SSIValidations.validate_carrier_booking()
#
		#		# If file is valid then send it for insertion else send a notification email
		#		if valid:
		#			LogService.print('File valid')
		#			listener.send_for_insertion()
		#		else:
		#			LogService.print('File invalid')
		#			listener.send_notification_email()