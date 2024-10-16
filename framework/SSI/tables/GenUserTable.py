from framework.SSI.core.AppDatabase import AppDatabase
from framework.formats.objects.DictIndexer import DictIndexer
from framework.formats.objects.DictLookup import DictLookup
from framework.formats.objects.Primitives import Primitives
from framework.AppConfig import AppConfig

class GenUserTable:

	# return a boolean indicating if user is permitted to upload on FTP server
	@staticmethod
	def isUserAllowedFtpUpload(db:AppDatabase, programID:int, userID:int):
		member_id = None

		response = db.master().select_all_safe("SELECT cValue, iMemberID FROM gen_Configuration WHERE iUserID=%s AND iProgramID=%s AND cCode='FTPUSER' AND iStatus=0;", [userID, programID], False)

		if len(response) > 0:
			if response[0][0] == 'Y':
				member_id = response[0][1]
				return True, member_id

		return False, member_id

	# return all the FTP details for this member
	@staticmethod
	def getMemberFtpDetails(db:AppDatabase, programID:int, memberID:int):
		
		# get FTP Details for import and export files
		mainSettingsList = db.master().select_all_safe("SELECT cCode,cValue FROM gen_Configuration WHERE iStatus=0 AND iMemberID=%s AND iProgramID=%s", (memberID, 0), False)
		
		# get FTP host server details and paths
		rateSettingsList = db.master().select_all_safe("SELECT cCode,cValue FROM gen_Configuration WHERE iStatus=0 AND iMemberID=%s AND iProgramID=%s", (memberID, programID), False)
		
		if len(mainSettingsList) > 0 and len(rateSettingsList) > 0:

			# index keys into dictionary of key:value
			mainSettings = DictIndexer.bySlot(mainSettingsList, 0, False, 'cell', 1)
			rateSettings = DictIndexer.bySlot(rateSettingsList, 0, False, 'cell', 1)

			# if all the required settings exist
			if DictLookup.hasAllKeys(mainSettings, ['FTPHOST', 'FTPUSERNAME', 'FTPPASS', 'FTPPORT']) and DictLookup.hasAllKeys(rateSettings, ['FTPACKPATH']):
				
				# load individual settings
				HOST = mainSettings['FTPHOST']
				PORT = Primitives.parseInt(mainSettings['FTPPORT'])
				USERNAME = mainSettings['FTPUSERNAME']
				PASS = mainSettings['FTPPASS']
				ACKPATH = rateSettings['FTPACKPATH']

				return (HOST, PORT, USERNAME, PASS, ACKPATH)
			
		return (None, None, None, None, None, None)