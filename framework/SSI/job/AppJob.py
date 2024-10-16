

from datetime import datetime
from framework.SSI.core.AppDatabase import AppDatabase
from framework.SSI.job.SSICommonStatus import SSICommonStatus
from framework.SSI.tables.SSIJobTable_AppJob import SSIJobTable_AppJob
from framework.formats.xml.XmlDocumentReader import XmlDocumentReader
from framework.tracking.x12.X12Status import X12Status
from framework.tracking.x12.X12Reader import X12Reader
from framework.AppConfig import AppConfig


class AppJob:
	
	
	# DB connections and objects
	db:AppDatabase
	xmlDocument:XmlDocumentReader
	statuses:list
	file_log_id:int
	failed_validations:list
	x12_obj:X12Status
	file_type:str
	file_path:str
	file_bucket:str
	isTransShipment:bool
	sqs_message:dict

	# FTP upload details
	member_id:int				# iMemberID of the user who uploaded it
	member_allowed_ftp:bool		# is the user granted FTP upload permission?
	member_FTP_host:str			# for this member, what is the FTP host?
	member_FTP_port:int			# for this member, what is the FTP port?
	member_FTP_user:str			# for this member, what is the FTP username?
	member_FTP_pass:str			# for this member, what is the FTP password?
	member_FTP_ack_folder:str 	# where to upload the acknowledgements?



	# object model
	statuses:list[SSICommonStatus]



	# job metadata
	iJobID:int
	iFileLogID:int
	root:str
	cFileName:str
	cFilePath:str
	cDestFileName:str
	cIncomingS3Link:str
	iProgramID:int
	cFileFormat:str
	cFileType:str
	cCurrentStatus:str
	iErrorcode:int
	cErrorMessage:str
	cSender:str
	cReceiver:str
	cInAck:str
	cOutAck:str
	tFileDate:datetime
	tStartTime:datetime
	tEndTime:datetime
	iStatus:int
	iEnteredby:int
	tEntered:int
	iUpdatedby:int
	tUpdated:int


	
	
	def __init__(self):

		self.db = None
		self.xmlDocument = None
		self.statuses = None
		self.file_log_id = None
		self.failed_validations = None
		self.x12_obj = None
		self.file_type = None
		self.file_path = None
		self.file_bucket = None
		self.isTransShipment = None
		self.sqs_message = None

		self.member_id = 0
		self.member_allowed_ftp = False
		self.member_FTP_host = None
		self.member_FTP_port = None
		self.member_FTP_user = None
		self.member_FTP_pass = None
		self.member_FTP_ack_folder = None

		self.statuses = []

		self.root = None
		self.iJobID = None
		self.iFileLogID = None
		self.cFileName = None
		self.cFilePath = None
		self.cDestFileName = None
		self.cIncomingS3Link = None
		self.iProgramID = None
		self.cFileFormat = None
		self.cFileType = None
		self.cCurrentStatus = None
		self.iErrorcode = None
		self.cErrorMessage = None
		self.cSender = None
		self.cReceiver = None
		self.cInAck = None
		self.cOutAck = None
		self.tFileDate = None
		self.tStartTime = None
		self.tEndTime = None
		self.iStatus = None
		self.iEnteredby = None
		self.tEntered = None
		self.iUpdatedby = None
		self.tUpdated = None


		self.initJobTable()


	def initJobTable(self):
		if not AppConfig.LOCAL_TESTING:
			SSIJobTable_AppJob.loadJobMetadata(self)


	def loadFromXml(self):
		self.cReceiver = self.xmlDocument.getXmlTagValue('./Envelope/ReceiverID')
		self.cSender = self.xmlDocument.getXmlTagValue('./Envelope/SenderID')
		self.root = self.xmlDocument.getXmlTags('.')[0].tag


	def loadFromX12(self, x12_file):
		self.x12_obj = X12Reader.read(x12_file)
		self.isTransShipment = False
		self.cSender = self.x12_obj.sender_id
		self.cReceiver = self.x12_obj.receiver_id