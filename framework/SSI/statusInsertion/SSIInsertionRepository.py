from dateutil.parser import parse
from datetime import datetime
from framework.SSI.core.AppDatabase import AppDatabase
from framework.SSI.job.AppJob import AppJob
from framework.SSI.job.SSICommonStatus import SSICommonStatus
from framework.SSI.tables.ShipmentStatusTable import ShipmentStatusTable
from framework.SSI.tables.DocumentationTable import DocumentationTable
from framework.SSI.tables.ShipmentDetailsTable import ShipmentDetailsTable
from framework.SSI.tables.LineItemTable import LineItemTable
from framework.SSI.tables.TransshipmentDetailsTable import TransshipmentDetailsTable
from framework.system.LogService import LogService
from pypika import Query, Table, Field

class SSIInsertionRepository:

	@staticmethod
	def insert(db:AppDatabase, commonStatus:SSICommonStatus, job:AppJob):

		try:
			commonStatus.cStatusCode = int(commonStatus.cStatusCode)
		except:
			pass
		
		LogService.print(f"status code : {commonStatus.cStatusCode}")

		# If status code 600 is received then set lot number as null for the corresponding HBL number
		if commonStatus.cStatusCode == 600:
			# self.db.update("UPDATE track_ShipmentDetails SET cLotNumber=null where cHouseBillOfLadingNumber=%s", (commonStatus.cHouseBillOfLadingNumber,))
			db.master().update_record_where("track_ShipmentDetails", {
				"cHouseBillOfLadingNumber" : commonStatus.cHouseBillOfLadingNumber
			},
			{
				"cLotNumber" : None
			})
			LogService.print("Record updated in track_ShipmentDetails")
			return []

		# If status code 601 is received then update the previous HBL number with the new one
		if commonStatus.cStatusCode == 601:
			# commonStatus.PreviousBillOfladingNumber = self.getXmlTagValue('./ShipmentStatusDetails/commonStatus.PreviousBillOfladingNumber')
			# self.db.update("update track_ShipmentDetails set cPrevHBL=cHouseBillOfLadingNumber, cHouseBillOfLadingNumber=%s where cHouseBillOfLadingNumber = %s;", (commonStatus.cHouseBillOfLadingNumber, commonStatus.PreviousBillOfladingNumber))
			db.master().update_record_where("track_ShipmentDetails", {
				"cHouseBillOfLadingNumber" : commonStatus.PreviousBillOfladingNumber
			},
			{
				"cPrevHBL" : commonStatus.cHouseBillOfLadingNumber,
				"cHouseBillOfLadingNumber" : commonStatus.cHouseBillOfLadingNumber
			})
			LogService.print("Record updated in track_ShipmentDetails")
			# self.db.update("UPDATE track_ShipmentDetails SET cHouseBillOfLadingNumber=%s where cHouseBillOfLadingNumber=%s", (commonStatus.cHouseBillOfLadingNumber, commonStatus.PreviousBillOfladingNumber))
			return []
		
		# If status code 604 is received then void the HBL number
		if commonStatus.cStatusCode == 604:
			# self.db.update("update track_ShipmentDetails set cPrevHBL=cHouseBillOfLadingNumber, cHouseBillOfLadingNumber=null where cHouseBillOfLadingNumber = %s;", (commonStatus.cHouseBillOfLadingNumber))
			db.master().update_record_where("track_ShipmentDetails", {
				"cHouseBillOfLadingNumber" : commonStatus.cHouseBillOfLadingNumber
			},
			{
				"cPrevHBL" : commonStatus.cHouseBillOfLadingNumber,
				"cHouseBillOfLadingNumber" : None
			})
			LogService.print("Record updated in track_ShipmentDetails")
			# self.db.update("UPDATE track_ShipmentDetails SET cHouseBillOfLadingNumber=null where cHouseBillOfLadingNumber=%s", (commonStatus.cHouseBillOfLadingNumber,))
			return []

		# If Status code 11 then set iStatus as -1 for that WWARefNumber
		if commonStatus.cStatusCode == 11:
			LogService.print('Status 11 Received')
			db.master().update_record("track_StatusDetails", "cWWAShipmentReference", commonStatus.cWWAShipmentReference, {"iStatus" : -1})
			db.master().update_record("track_DocumentationDetails", "cWWAShipmentReference", commonStatus.cWWAShipmentReference, {"iStatus" : -1})
			db.master().update_record("track_ShipmentDetails", "cWWAShipmentReference", commonStatus.cWWAShipmentReference, {"iStatus" : -1})
			db.master().update_record("track_LineItems", "cWWAShipmentReference", commonStatus.cWWAShipmentReference, {"iStatus" : -1})
			# self.db.update('UPDATE track_StatusDetails SET iStatus=-1 WHERE cWWAShipmentReference=%s', (commonStatus.cWWAShipmentReference,))
			# self.db.update('UPDATE track_DocumentationDetails SET iStatus=-1 WHERE cWWAShipmentReference=%s', (commonStatus.cWWAShipmentReference,))
			# self.db.update('UPDATE track_ShipmentDetails SET iStatus=-1 WHERE cWWAShipmentReference=%s', (commonStatus.cWWAShipmentReference,))
			# self.db.update('UPDATE track_LineItems SET iStatus=-1 WHERE cWWAShipmentReference=%s', (commonStatus.cWWAShipmentReference,))
			return []

		# Check if merged shipment is received
		if commonStatus.cStatusCode == 27:
			LogService.print('Status 27 received')

			bookingNumbers = []
			for cs in job.statuses:
				bookingNumbers.append(cs.cBookingNumber)

			PrimaryBookingNumber = job.statuses[0].primaryBkngNumber
			bookingNumbers.append(PrimaryBookingNumber)
			
			# bookingNumbers.append(root.findall('./ShipmentStatusDetails/BookingNumber').text)
			# bookingNumbers = tuple(bookingNumbers)
			# LogService.print(bookingNumbers)

			track_ShipmentDetails_table = Table('track_ShipmentDetails')
			track_LineItems_table = Table('track_LineItems')
			track_DocumentationDetails_table = Table('track_DocumentationDetails')
			track_StatusDetails_table = Table('track_StatusDetails')

			# update_query = Query.update(track_DocumentationDetails_table).set(track_DocumentationDetails_table.PrimaryBookingNumber, PrimaryBookingNumber).where(track_DocumentationDetails_table.cBookingNumber.isin(bookingNumbers)).get_sql().replace('"', '')
			# LogService.print(Query.update(track_ShipmentDetails_table).set(track_ShipmentDetails_table.cPrimaryBookingNumber, PrimaryBookingNumber).where(track_ShipmentDetails_table.cBookingNumber.isin(bookingNumbers)).get_sql().replace('"', ''))
			# db.master().update_record("track_StatusDetails", "cWWAShipmentReference", commonStatus.cWWAShipmentReference, {"cPrimaryBookingNumber" : PrimaryBookingNumber})
			# db.master().update_record("track_DocumentationDetails", "cWWAShipmentReference", commonStatus.cWWAShipmentReference, {"cPrimaryBookingNumber" : PrimaryBookingNumber})
			# db.master().update_record("track_ShipmentDetails", "cWWAShipmentReference", commonStatus.cWWAShipmentReference, {"cPrimaryBookingNumber" : PrimaryBookingNumber})
			# db.master().update_record("track_LineItems", "cWWAShipmentReference", commonStatus.cWWAShipmentReference, {"cPrimaryBookingNumber" : PrimaryBookingNumber})

			# db.master().py file need to add support for IN Operators
			db.master().batch_execute(Query.update(track_ShipmentDetails_table).set(track_ShipmentDetails_table.cPrimaryBookingNumber, PrimaryBookingNumber).where(track_ShipmentDetails_table.cBookingNumber.isin(bookingNumbers)).get_sql().replace('"', ''), None)
			db.master().batch_execute(Query.update(track_LineItems_table).set(track_LineItems_table.cPrimaryBookingNumber, PrimaryBookingNumber).where(track_LineItems_table.cBookingNumber.isin(bookingNumbers)).get_sql().replace('"', ''), None)
			db.master().batch_execute(Query.update(track_DocumentationDetails_table).set(track_DocumentationDetails_table.cPrimaryBookingNumber, PrimaryBookingNumber).where(track_DocumentationDetails_table.cBookingNumber.isin(bookingNumbers)).get_sql().replace('"', ''), None)
			db.master().batch_execute(Query.update(track_StatusDetails_table).set(track_StatusDetails_table.cPrimaryBookingNumber, PrimaryBookingNumber).where(track_StatusDetails_table.cBookingNumber.isin(bookingNumbers)).get_sql().replace('"', ''), None)
			# self.db.update(Query.update(track_ShipmentDetails_table).set(track_ShipmentDetails_table.cPrimaryBookingNumber, PrimaryBookingNumber).where(track_ShipmentDetails_table.cBookingNumber.isin(bookingNumbers)).get_sql().replace('"', ''), None)
			# self.db.update(Query.update(track_LineItems_table).set(track_LineItems_table.cPrimaryBookingNumber, PrimaryBookingNumber).where(track_LineItems_table.cBookingNumber.isin(bookingNumbers)).get_sql().replace('"', ''), None)
			# self.db.update(Query.update(track_DocumentationDetails_table).set(track_DocumentationDetails_table.cPrimaryBookingNumber, PrimaryBookingNumber).where(track_DocumentationDetails_table.cBookingNumber.isin(bookingNumbers)).get_sql().replace('"', ''), None)
			# self.db.update(Query.update(track_StatusDetails_table).set(track_StatusDetails_table.cPrimaryBookingNumber, PrimaryBookingNumber).where(track_StatusDetails_table.cBookingNumber.isin(bookingNumbers)).get_sql().replace('"', ''), None)
			LogService.print(f'Tables track_ShipmentDetails, track_StatusDetails, track_LineItems and track_DocumentationDetails updated with PrimaryBookingNumber: {PrimaryBookingNumber}')
			return []

		 # If status code is 450 - Update ARN Request
		if commonStatus.cStatusCode == 450:
			LogService.print("Status 450 received")

			# Get HouseBillOfLadingNumber, ArrivalNoticeNumber and PrevArrivalNoticeNumber from the file
			# commonStatus.arn = self.getXmlTagValue('./ShipmentStatusDetails/ArrivalNoticeNumber')
			# prev_arn = self.getXmlTagValue('./ShipmentStatusDetails/PrevArrivalNoticeNumber')
			
			LogService.print(f"Previous ARN : {commonStatus.prev_arn}, New ARN : {commonStatus.arn}")
			db.master().batch_execute("UPDATE track_ShipmentDetails SD1 INNER JOIN track_ShipmentDetails SD2 ON SD2.iShipmentdetailID = SD1.iShipmentdetailID SET SD1.cPrevArrivalNoticeNumber=SD2.cArrivalNoticeNumber, SD1.cArrivalNoticeNumber=%s WHERE SD2.cArrivalNoticeNumber=%s or SD2.cPrevArrivalNoticeNumber=%s;", (commonStatus.arn, commonStatus.prev_arn, commonStatus.prev_arn))
			# self.db.update("UPDATE track_ShipmentDetails SD1 INNER JOIN track_ShipmentDetails SD2 ON SD2.iShipmentdetailID = SD1.iShipmentdetailID SET SD1.cPrevArrivalNoticeNumber=SD2.cArrivalNoticeNumber, SD1.cArrivalNoticeNumber=%s WHERE SD2.cArrivalNoticeNumber=%s or SD2.cPrevArrivalNoticeNumber=%s;", (commonStatus.arn, prev_arn, prev_arn))

			LogService.print("Record Updated in track_ShipmentDetails")
			return []
		
		if commonStatus.cStatusCode == 452:
			# commonStatus.parent_arn = self.getXmlTagValue('./ShipmentStatusDetails/ParentArrivalNoticeNumber')
			SSIInsertionRepository.parentARN(db, commonStatus.parent_arn, commonStatus.arn)

		# commonStatus.cCarrierSCAC = self.getXmlTagValue('./ShipmentStatusDetails/CarrierSCAC')
		result = db.master().select_all_safe("SELECT COUNT(*) FROM gen_Carrier WHERE cCode = %s", (commonStatus.cCarrierSCAC,))
		if result[0][0] == 0:
			LogService.log('WARNING: Invalid cCarrierscac value')

		errors = []
		if commonStatus.cStatusCode in (51, 52, 53, 1051, 1052, 1053):
			status = True if TransshipmentDetailsTable.insert(db, commonStatus, job) else errors.append('tra_Transshipment_detail')
		else:
			# CargoDetails = self.root.findall('./ShipmentStatusDetails/CargoDetails')
			if commonStatus.cStatustype.lower() == 'e' and commonStatus.CargoDetails.__len__() > 0:
				if commonStatus.bookingsMerged and commonStatus.cStatusCode > 27:
					db.master().update_record("track_LineItems", "cPrimaryBookingNumber", commonStatus.primaryBkngNumber, {"iStatus" : 0})
					# self.db.update('UPDATE track_LineItems SET iStatus = "0" WHERE cPrimaryBookingNumber = %s', (commonStatus.primaryBkngNumber,))
				else:
					db.master().update_record_where("track_LineItems", {"cWWAShipmentReference" : commonStatus.cWWAShipmentReference, "cBookingNumber" : commonStatus.cBookingNumber}, {"iStatus" : 0})
					# self.db.update('UPDATE track_LineItems SET iStatus = "0" WHERE cWWAShipmentReference = %s AND cBookingNumber = %s', (commonStatus.cWWAShipmentReference, commonStatus.cBookingNumber))
			elif commonStatus.cStatustype.lower() == 'i' and commonStatus.CargoDetails.__len__() > 0:
				pass
				# self.db.update('UPDATE track_LineItems SET iStatus = "0" WHERE cHouseBillOfLadingNumber = %s', (commonStatus.cHouseBillOfLadingNumber,))
			for cargo in commonStatus.CargoDetails:
				status = True if LineItemTable.insert(db, cargo, commonStatus) else errors.append('track_LineItems')
			status = True if ShipmentStatusTable.insertOrUpdate(db, commonStatus) else errors.append('track_StatusDetails')
			status = True if ShipmentDetailsTable.insertOrUpdate(db, commonStatus) else errors.append('track_ShipmentDetails')
			status = True if DocumentationTable.insertOrUpdate(db, commonStatus) else errors.append('track_DocumentationDetails')
		return errors

	@staticmethod
	def parentARN(db:AppDatabase, parent_arn, arn):
		# self.db.update('UPDATE track_ShipmentDetails SD1 INNER JOIN track_ShipmentDetails SD2 ON SD2.iShipmentdetailID = SD1.iShipmentdetailID set SD1.cParentArrivalNoticeNumber=SD2.cArrivalNoticeNumber, SD1.cArrivalNoticeNumber=%s where SD1.cArrivalNoticeNumber=%s;', (commonStatus.arn, parent_arn))
		db.master().batch_execute('UPDATE track_ShipmentDetails SD1 INNER JOIN track_ShipmentDetails SD2 ON SD2.iShipmentdetailID = SD1.iShipmentdetailID set SD1.cParentArrivalNoticeNumber=SD2.cArrivalNoticeNumber, SD1.cArrivalNoticeNumber=%s where SD1.cArrivalNoticeNumber=%s;', (arn, parent_arn))
	