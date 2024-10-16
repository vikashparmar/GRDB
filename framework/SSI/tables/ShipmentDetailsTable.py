from framework.SSI.core.AppDatabase import AppDatabase
from pypika import Query, Table, Field
from framework.SSI.tables.FileMetaDataLogTable import FileMetaDataLogTable
from framework.SSI.job.SSICommonStatus import SSICommonStatus
from framework.system.LogService import LogService

class ShipmentDetailsTable:

	def insertOrUpdate(db:AppDatabase, commonStatus:SSICommonStatus):
		
		# Update Origin and Destination Member details
		if commonStatus.cPlaceOfReceipt:
			origin = commonStatus.cPlaceOfReceipt
		elif commonStatus.cPortOfLoading:
			origin = commonStatus.cPortOfLoading
		else:
			origin = None
		
		if commonStatus.cPlaceOfDelivery:
			destination = commonStatus.cPlaceOfDelivery
		elif commonStatus.cPortOfDischarge:
			destination = commonStatus.cPortOfDischarge
		else:
			destination = None

		if origin and destination:
			# LogService.print("store procedure called.....")
			query = "call getMemberID(%s,%s,@a,@b);"
			values = (origin, destination)
			db.master()._insert_id_safe(query, values)
			# LogService.print("values....", self.db.select("Select @a, @b;", ()))

		#if import status is received then getting iShipmentdetailID using cHouseBillOfLadingNumber
		if commonStatus.cStatustype.lower() == 'i':
			result  = db.master().select_all_safe("SELECT iShipmentdetailID FROM track_ShipmentDetails WHERE cHouseBillOfLadingNumber = %s", (commonStatus.cHouseBillOfLadingNumber,))
		#if export status is received then getting iShipmentdetailID using a combination of cWWAShipmentReference and cBookingNumber
		elif commonStatus.cStatustype.lower() == 'e':
			if commonStatus.bookingsMerged and int(commonStatus.cStatusCode) > 27:
				result  = db.master().select_all_safe("SELECT iShipmentdetailID FROM track_ShipmentDetails WHERE cPrimaryBookingNumber = %s", (commonStatus.primaryBkngNumber,))
			else:
				result  = db.master().select_all_safe("SELECT iShipmentdetailID FROM track_ShipmentDetails WHERE cWWAShipmentReference = %s AND cBookingNumber = %s", (commonStatus.cWWAShipmentReference, commonStatus.cBookingNumber))

		#if record already exists in track_ShipmentDetails table then run update scripts
		if result.__len__() > 0:

			# create empty lists to store the file meta data for logging
			references, values = [], []
			try:
				track_ShipmentDetails_table = Table('track_ShipmentDetails')
				columns = {
					'cArrivalNoticeNumber' : commonStatus.cArrivalNoticeNumber,
					'cWWAShipmentReference' : commonStatus.cWWAShipmentReference,
					'cBookingNumber' : commonStatus.cBookingNumber,
					'cApplicationType' : commonStatus.cApplicationType,
					'cCarrierBookingNumber' : commonStatus.cCarrierBookingNumber, 
					'cCarrierSCAC' : commonStatus.cCarrierSCAC, 
					'cBkngOfficeCode' : commonStatus.cBkngOfficeCode,
					'cBLReleasePoint' : commonStatus.cBLReleasePoint,
					'cCommunicationReference' : commonStatus.cCommunicationReference,
					'cConsigneeReference' : commonStatus.cConsigneeReference,
					'cContainerCode' : commonStatus.cContainerCode,
					'cContainerNumber' : commonStatus.cContainerNumber,
					'cContainerSize' : commonStatus.cContainerSize,
					'cContainerType' : commonStatus.cContainerType,
					'cCustomerAlias' : commonStatus.cCustomerAlias,
					'tCutoffReceivingWarehouse' : commonStatus.tCutoffReceivingWarehouse,
					'tETAPlaceOfDelivery' : commonStatus.tETAPlaceOfDelivery,
					'tETAPortOfDischarge' : commonStatus.tETAPortOfDischarge,
					'tETSPlaceOfReceipt' : commonStatus.tETSPlaceOfReceipt,
					'tETSPortOfLoading' : commonStatus.tETSPortOfLoading,
					'cFileNumber' : commonStatus.cFileNumber,
					'cForwarderReference' : commonStatus.cForwarderReference,
					'cHouseBillOfLadingNumber' : commonStatus.cHouseBillOfLadingNumber,
					'cInTransitDate' : commonStatus.cInTransitDate,
					'cInTransitNumber' : commonStatus.cInTransitNumber,
					'cLotNumber' : commonStatus.cLotNumber,
					'cOceanVessel' : commonStatus.cOceanVessel,
					'cPickupReference' : commonStatus.cPickupReference,
					'cPlaceOfDelivery' : commonStatus.cPlaceOfDelivery,
					'cPlaceOfReceipt' : commonStatus.cPlaceOfReceipt,
					'cPortOfDischarge' : commonStatus.cPortOfDischarge,
					'cPortOfLoading' : commonStatus.cPortOfLoading,
					'cReceivingWarehouse' : commonStatus.cReceivingWarehouse,
					'cReleaseType' : commonStatus.cReleaseType,
					'cSealNumber' : commonStatus.cSealNumber,
					'cShipperReference' : commonStatus.cShipperReference,
					'cVoyage' : commonStatus.cVoyage,
					'iUpdatedby' : commonStatus.iUpdatedby,
					'tUpdated' : commonStatus.tUpdated,
				}

				#if import status is reecived
				if commonStatus.cStatustype.lower() == 'i':
					#Setting the basic update query with table name and where condition
					update_query = Query.update(track_ShipmentDetails_table).where(track_ShipmentDetails_table.cHouseBillOfLadingNumber == commonStatus.cHouseBillOfLadingNumber)
					#if export status was received before then update certain columns
					update_query = update_query.set('iDestMemberID', '@b')
					if commonStatus.export_status_received_before:
						for column in ['cContainerNumber', 'cVoyage', 'cArrivalNoticeNumber', 'tUpdated', 'cWWAShipmentReference', 'cPortOfDischarge', 'cPlaceOfDelivery', 'cCustomerAlias']:
							update_query = update_query.set(column, columns[column]) if columns[column] != None else update_query	 
							references.append(column)
							values.append(columns[column])				   
					#if export status was not received before then update certain columns
					else:
						for column in ['cContainerNumber', 'cVoyage', 'cArrivalNoticeNumber', 'cHouseBillOfLadingNumber', 'cBookingNumber', 'cLotNumber', 'tUpdated', 'cWWAShipmentReference', 'cPlaceOfReceipt', 'cPortOfLoading', 'cPortOfDischarge', 'cPlaceOfDelivery', 'cCustomerAlias']:
							update_query = update_query.set(column, columns[column]) if columns[column] != None else update_query
							references.append(column)
							values.append(columns[column]) 
				#if export status is received update all the columns
				elif commonStatus.cStatustype.lower() == 'e':
					#Setting the basic update query with table name and where condition
					if type(result[0][0]) == str:
						update_query = Query.update(track_ShipmentDetails_table).where(track_ShipmentDetails_table.iShipmentdetailID == result[0][0])
					else:
						iShipmentdetailID=[]
						for res in result:
							iShipmentdetailID.append(res)
						update_query = Query.update(track_ShipmentDetails_table).where(track_ShipmentDetails_table.iShipmentdetailID.isin(iShipmentdetailID))
					update_query = update_query.set('iOrgMemberID', '@a')
					update_query = update_query.set('iDestMemberID', '@b')
					for column in columns:
						update_query = update_query.set(column, columns[column]) if columns[column] != None else update_query
						references.append(column)
						values.append(columns[column]) 
				# LogService.print(update_query.get_sql().replace('"', '').replace("'@a'", "@a").replace("'@b'", "@b"))
				# LogService.print("values....", self.db.select("Select @a, @b;", ()))
				# self.db.update(update_query.get_sql().replace('"', '').replace("'@a'", "@a").replace("'@b'", "@b"), None)
				db.master().batch_execute(update_query.get_sql().replace('"', '').replace("'@a'", "@a").replace("'@b'", "@b"), None)
				LogService.log('Record updated in track_ShipmentDetails')
				FileMetaDataLogTable.insert(db.master(), references, values)
				return True
			except Exception as e:
				LogService.error('Exception while inserting at track_ShipmentDetails_table', e)
		#if record does not exist in track_ShipmentDetails table then run insert script
		else:
			iStatus = 1
			columns = ('cWWAShipmentReference', 'cBookingNumber', 'cPrimaryBookingNumber', 'cArrivalNoticeNumber', 'cApplicationType', 'cCarrierBookingNumber', 'cCarrierSCAC', 'cBkngOfficeCode', 'cBLReleasePoint', 'cCommunicationReference', 'cConsigneeReference', 'cContainerCode', 'cContainerNumber', 'cContainerSize', 'cContainerType', 'cCustomerAlias', 'tCutoffReceivingWarehouse', 'tETAPlaceOfDelivery', 'tETAPortOfDischarge', 'tETSPlaceOfReceipt', 'tETSPortOfLoading', 'cFileNumber', 'cForwarderReference', 'cHouseBillOfLadingNumber', 'cInTransitDate', 'cInTransitNumber', 'cLotNumber', 'cOceanVessel', 'cPickupReference', 'cPlaceOfDelivery', 'cPlaceOfReceipt', 'cPortOfDischarge', 'cPortOfLoading', 'cReceivingWarehouse', 'cReleaseType', 'cSealNumber', 'cShipperReference', 'cVoyage', 'iOrgMemberID', 'iDestMemberID', 'iStatus', 'iEnteredby', 'tEntered')

			values = (commonStatus.cWWAShipmentReference, commonStatus.cBookingNumber, commonStatus.primaryBkngNumber, commonStatus.cArrivalNoticeNumber, commonStatus.cApplicationType, commonStatus.cCarrierBookingNumber, commonStatus.cCarrierSCAC, commonStatus.cBkngOfficeCode, commonStatus.cBLReleasePoint, commonStatus.cCommunicationReference, commonStatus.cConsigneeReference, commonStatus.cContainerCode, commonStatus.cContainerNumber, commonStatus.cContainerSize, commonStatus.cContainerType, commonStatus.cCustomerAlias, commonStatus.tCutoffReceivingWarehouse, commonStatus.tETAPlaceOfDelivery, commonStatus.tETAPortOfDischarge, commonStatus.tETSPlaceOfReceipt, commonStatus.tETSPortOfLoading, commonStatus.cFileNumber, commonStatus.cForwarderReference, commonStatus.cHouseBillOfLadingNumber, commonStatus.cInTransitDate, commonStatus.cInTransitNumber, commonStatus.cLotNumber, commonStatus.cOceanVessel, commonStatus.cPickupReference, commonStatus.cPlaceOfDelivery, commonStatus.cPlaceOfReceipt, commonStatus.cPortOfDischarge, commonStatus.cPortOfLoading, commonStatus.cReceivingWarehouse, commonStatus.cReleaseType, commonStatus.cSealNumber, commonStatus.cShipperReference, commonStatus.cVoyage, iStatus, commonStatus.iEnteredby, commonStatus.tEntered)
			try:
				db.master()._insert_id_safe(f"""INSERT INTO track_ShipmentDetails {str(columns).replace("'", "`")} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, @a, @b, %s, %s, %s)""", values)
				LogService.log('Record Inserted in track_ShipmentDetails')
				return True
			except Exception as e:
				LogService.error('Error while inserting record to track_ShipmentDetails table: ', e)
			
			FileMetaDataLogTable.insert(db.master(), columns, values)
		return False