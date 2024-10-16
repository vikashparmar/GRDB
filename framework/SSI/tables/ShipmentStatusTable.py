

from framework.SSI.core.AppDatabase import AppDatabase
from framework.SSI.job.SSICommonStatus import SSICommonStatus
from framework.system.LogService import LogService

class ShipmentStatusTable:

	@staticmethod
	def insertOrUpdate(db:AppDatabase, commonStatus:SSICommonStatus):

		result = db.master().select_all_safe('SELECT iProcessorder FROM gen_Status WHERE cStatuscode=%s', (commonStatus.cStatusCode,))
		processOrderInFile = result[0][0] if result.__len__() > 0 else None

		result = None
		if commonStatus.bookingsMerged and int(commonStatus.cStatusCode) > 27:
			result = db.master().select_all_safe('SELECT gen_Status.iProcessorder, track_StatusDetails.cStatusCode FROM gen_Status INNER JOIN track_StatusDetails ON gen_Status.cStatuscode = track_StatusDetails.cStatusCode WHERE track_StatusDetails.cPrimaryBookingNumber = %s ORDER BY gen_Status.iProcessorder DESC', (commonStatus.primaryBkngNumber,))
		else:
			result = db.master().select_all_safe('SELECT gen_Status.iProcessorder, track_StatusDetails.cStatusCode FROM gen_Status INNER JOIN track_StatusDetails ON gen_Status.cStatuscode = track_StatusDetails.cStatusCode WHERE track_StatusDetails.cBookingNumber = %s AND track_StatusDetails.cWWAShipmentReference = %s ORDER BY gen_Status.iProcessorder DESC', (commonStatus.cBookingNumber, commonStatus.cWWAShipmentReference))

		highestProcessOrderInDb = result[0][0] if result.__len__() > 0 else None
		
		if highestProcessOrderInDb == None:
			iStatus = 1
		elif processOrderInFile > highestProcessOrderInDb:
			# Add Support for ORDER BY and LIMIT in Update function
			# self.db.update('UPDATE track_StatusDetails SET iStatus = 0 WHERE cStatuscode = %s ORDER BY cStatusDateTime DESC LIMIT 1', (result[0][1],))
			db.master().batch_execute('UPDATE track_StatusDetails SET iStatus = 0 WHERE cStatuscode = %s ORDER BY cStatusDateTime DESC LIMIT 1', (result[0][1],))
			iStatus = 1
		elif processOrderInFile < highestProcessOrderInDb:
			iStatus = 0
			for record in result:
				if processOrderInFile == record[0]:
					iStatus = -1
		elif processOrderInFile == highestProcessOrderInDb:
			if commonStatus.bookingsMerged and int(commonStatus.cStatusCode) > 27:
				db.master().update_record("tra_Transshipment_detail", {"cPrimaryBookingNumber" : commonStatus.primaryBkngNumber, "cStatusCode" : commonStatus.cStatusCode}, {})
				# self.db.update('UPDATE track_StatusDetails SET iStatus = -1 WHERE cPrimaryBookingNumber = %s AND cStatusCode = %s', (commonStatus.primaryBkngNumber, commonStatus.cStatusCode))
				db.master().batch_execute('UPDATE track_StatusDetails SET iStatus = -1 WHERE cPrimaryBookingNumber = %s AND cStatusCode = %s', (commonStatus.primaryBkngNumber, commonStatus.cStatusCode))
			else:
				# self.db.update('UPDATE track_StatusDetails SET iStatus = -1 WHERE cBookingNumber = %s AND cWWAShipmentReference = %s AND cStatusCode = %s', (commonStatus.cBookingNumber, commonStatus.cWWAShipmentReference, commonStatus.cStatusCode))
				db.master().batch_execute('UPDATE track_StatusDetails SET iStatus = -1 WHERE cBookingNumber = %s AND cWWAShipmentReference = %s AND cStatusCode = %s', (commonStatus.cBookingNumber, commonStatus.cWWAShipmentReference, commonStatus.cStatusCode))
			iStatus = 1
		try:
			# self.db.insert("""INSERT INTO track_StatusDetails (cWWAShipmentReference, cBookingNumber, cPrimaryBookingNumber, cApplicationType, cCarrierscac, cImport, cStatustype, cStatusCode, cStatusDateTime, iStatus, iEnteredby, tEntered, iUpdatedby, tUpdated) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (commonStatus.cWWAShipmentReference, commonStatus.cBookingNumber, commonStatus.cBookingNumber, commonStatus.cApplicationType, commonStatus.cCarrierSCAC, None, commonStatus.cStatustype, commonStatus.cStatusCode, commonStatus.cStatusDateTime, iStatus, self.iEnteredby, self.tEntered, '', ''))
			db.master().batch_execute("""INSERT INTO track_StatusDetails (cWWAShipmentReference, cBookingNumber, cPrimaryBookingNumber, cApplicationType, cCarrierscac, cImport, cStatustype, cStatusCode, cStatusDateTime, iStatus, iEnteredby, tEntered, iUpdatedby, tUpdated) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (commonStatus.cWWAShipmentReference, commonStatus.cBookingNumber, commonStatus.cBookingNumber, commonStatus.cApplicationType, commonStatus.cCarrierSCAC, None, commonStatus.cStatustype, commonStatus.cStatusCode, commonStatus.cStatusDateTime, iStatus, commonStatus.iEnteredby, commonStatus.tEntered, '', ''))
			LogService.print('Record Inserted in track_StatusDetails')
			return True
		except Exception as e:
			LogService.print('Error while inserting record to track_StatusDetails table: ', e)
		return False