from framework.SSI.core.AppDatabase import AppDatabase
from pypika import Query, Table, Field
from framework.SSI.tables.FileMetaDataLogTable import FileMetaDataLogTable
from framework.SSI.job.SSICommonStatus import SSICommonStatus
from framework.system.LogService import LogService

class DocumentationTable:

	@staticmethod
	def insertOrUpdate(db:AppDatabase, commonStatus:SSICommonStatus):
		
		if commonStatus.bookingsMerged and int(commonStatus.cStatusCode) > 27:
			result  = db.master().select_all_safe("SELECT iDocumentationID FROM track_DocumentationDetails WHERE cPrimaryBookingNumber = %s", (commonStatus.primaryBkngNumber,))
		else:
			result  = db.master().select_all_safe("SELECT iDocumentationID FROM track_DocumentationDetails WHERE cWWAShipmentReference = %s AND cBookingNumber = %s", (commonStatus.cWWAShipmentReference, commonStatus.cBookingNumber))
		if result.__len__() > 0:

			# create empty lists to store the file meta data for logging
			references, values = [], []

			try:
				track_DocumentationDetails_table = Table('track_DocumentationDetails')
				columns = {
					'cImageData' : commonStatus.cImageData,
					'cImageLink' : commonStatus.cImageLink,
					'cDoctype' : commonStatus.cDoctype, 
					'iUpdatedby' : commonStatus.iUpdatedby, 
					'tUpdated' : commonStatus.tUpdated
				}
				if type(result[0][0]) == str:
					update_query = Query.update(track_DocumentationDetails_table).where(track_DocumentationDetails_table.iDocumentationID == result[0][0])
				else:
					iDocumentationIDin=[]
					for res in result:
						iDocumentationIDin.append(res)
					update_query = Query.update(track_DocumentationDetails_table).where(track_DocumentationDetails_table.iDocumentationID.isin(iDocumentationIDin))
				for column in columns:
					update_query = update_query.set(column, columns[column]) if columns[column] != None else update_query
					references.append(column)
					values.append(columns[column])


				db.master().batch_execute(update_query.get_sql().replace('"', ''), None)
				LogService.print('Record updated in track_DocumentationDetails')

				FileMetaDataLogTable.insert(db.master(), references, values)

				return True
			except Exception as e:
				LogService.print('Error while inserting record to track_DocumentationDetails table: ', e)
		else:
			iStatus = 1
			try:
				columns = ('cWWAShipmentReference', 'cBookingNumber', 'cPrimaryBookingNumber', 'cImageData', 'cImageLink', 'cDoctype', 'iStatus', 'iEnteredby', 'tEntered')
				values = (commonStatus.cWWAShipmentReference, commonStatus.cBookingNumber, commonStatus.primaryBkngNumber, commonStatus.cImageData, commonStatus.cImageLink, commonStatus.cDoctype, iStatus, commonStatus.iEnteredby, commonStatus.tEntered)

				db.master()._insert_id_safe(f"""INSERT INTO track_DocumentationDetails {str(columns).replace("'", "`")} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", values)
				LogService.print('Record Inserted in track_DocumentationDetails')

				FileMetaDataLogTable.insert(db.master(), columns[3:], values[3:])

				return True
			except Exception as e:
				LogService.print('Error while inserting record to track_DocumentationDetails table: ', e)
		return False