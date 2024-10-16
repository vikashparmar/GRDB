from framework.SSI.core.AppDatabase import AppDatabase
from pypika import Query, Tables, Field
from framework.SSI.tables.FileMetaDataLogTable import FileMetaDataLogTable
from framework.SSI.job.SSICommonStatus import SSICommonStatus
from framework.formats.xml.XmlDocumentReader import XmlDocumentReader
from framework.system.LogService import LogService

class LineItemTable:

	@staticmethod
	def insert(db:AppDatabase, CargoDetails, commonStatus:SSICommonStatus):
		# LogService.print("CargoDetails", CargoDetails)
		CargoDetails = XmlDocumentReader(CargoDetails)

		cCommodity = None
		cDescription = None
		cMarks = None
		cPackaging = None
		cHazardousFlag = CargoDetails.getXmlTagValue('./HazardousFlag')
		iHeight = 0
		iLength = 0
		iWidth = 0
		cObjectType = 0
		cObject = 0
		cPieces = CargoDetails.getXmlTagValue('./Pieces')
		iVolumeCBF = CargoDetails.getXmlTagValue('./VolumeCBF')
		iVolumeCBM = CargoDetails.getXmlTagValue('./VolumeCBM')
		iWeightKG = CargoDetails.getXmlTagValue('./WeightKG')
		iWeightLBS = CargoDetails.getXmlTagValue('./WeightLBS')

		if cHazardousFlag.lower() == 'y':
			iHazWeightLBS = CargoDetails.getXmlTagValue('./HazardousDetails/HazWeightLBS')
			iHazVolumeCBF = CargoDetails.getXmlTagValue('./HazardousDetails/HazVolumeCBF')
			iHazVolumeCBM = CargoDetails.getXmlTagValue('./HazardousDetails/HazVolumeCBM')
			iHazWeightKG = CargoDetails.getXmlTagValue('./HazardousDetails/HazWeightKG')
		else:
			iHazWeightLBS = 0
			iHazVolumeCBF = 0
			iHazVolumeCBM = 0
			iHazWeightKG = 0

		iStatus = 1
		try:
			columns = ('cWWAShipmentReference', 'cBookingNumber', 'cPrimaryBookingNumber', 'cCommodity', 'cDescription', 'cMarks', 'cPackaging', 'cUom', 'cHazardousFlag', 'iHazVolumeCBF', 'iHazVolumeCBM', 'iHazWeightKG', 'iHazWeightLBS', 'cLotnumber', 'iHeight', 'iLength', 'iWidth', 'cObjectType', 'cObject', 'cPieces', 'iVolumeCBF', 'iVolumeCBM', 'iWeightKG', 'iWeightLBS', 'iStatus', 'iEnteredby', 'tEntered')

			values = (commonStatus.cWWAShipmentReference, commonStatus.cBookingNumber, commonStatus.primaryBkngNumber, cCommodity, cDescription, cMarks, cPackaging, commonStatus.cUom, cHazardousFlag, iHazVolumeCBF, iHazVolumeCBM, iHazWeightKG, iHazWeightLBS, commonStatus.cLotnumber, iHeight, iLength, iWidth, cObjectType, cObject, cPieces, iVolumeCBF, iVolumeCBM, iWeightKG, iWeightLBS, iStatus, commonStatus.iEnteredby, commonStatus.tEntered)

			db.master()._insert_id_safe(f"""INSERT INTO track_LineItems {str(columns).replace("'", "`")} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", values)
			LogService.print('Record Inserted in track_LineItems')

			FileMetaDataLogTable.insert(db.master(), columns[3:], values[3:])
			return True
		except Exception as e:
			LogService.print('Error while inserting record to track_LineItems table: ', e)
		return False