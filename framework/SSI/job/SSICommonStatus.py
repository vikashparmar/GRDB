
from dateutil.parser import parse

from framework.formats.xml.XmlDocumentReader import XmlDocumentReader
from framework.SSI.core.AppDatabase import AppDatabase
from datetime import datetime

class SSICommonStatus:

	isSS:bool
	isTS:bool

	cArrivalNoticeNumber:str
	cCarrierBookingNumber:str
	cBkngOfficeCode:str
	cBLReleasePoint:str
	cCommunicationReference:str
	cConsigneeReference:str
	cContainerCode:str
	cContainerNumber:int
	cContainerSize:str
	cContainerType:str
	cCustomerAlias:str
	tCutoffReceivingWarehouse:str
	tCutoffReceivingWarehouse:str
	tETAPlaceOfDelivery:str
	tETAPortOfDischarge:str
	tETSPlaceOfReceipt:str
	tETSPortOfLoading:str
	cFileNumber:int
	cForwarderReference:str
	cHouseBillOfLadingNumber:str
	cInTransitDate:str
	cInTransitNumber:str
	cLotNumber:int
	cOceanVessel:str
	cPickupReference:str
	cPlaceOfDelivery:str
	cPlaceOfReceipt:str
	cPortOfDischarge:str
	cPortOfLoading:str
	cReceivingWarehouse:str
	cReleaseType:str
	cSealNumber:int
	cShipperReference:str
	cVoyage:str
	TSReferenceTypeDetails:str
	cBookingnumber:str
	cLadingno:str
	cContainerno:str
	cSeal:str
	cCarrierSCAC:str
	cVoyageno:str
	cVessel:str
	cStatuslocationcode:str
	cStatuslocationname:str
	cPortofloadingcode:str
	cPortofarrivalcode:str
	cPortofdischargecode:str
	date:str
	time:str
	timezone:str
	tStatusdate:str
	tPortofarrival:str
	tPortofloading:str
	tPortofdischarge:str
	cWWAShipmentReference:str
	cBookingNumber:str
	cStatusCode:int
	cApplicationType:str
	cHouseBillOfLadingNumber:str
	arn:str
	PreviousBillOfladingNumber:str
	prev_arn:str
	parent_arn:str
	SenderID:str
	primaryBkngNumber:str
	cStatustype:str
	bookingsMerged:bool
	export_status_received_before:bool
	password:str
	temp_errors:list



	def __init__(self):
		self.isTS = None
		self.isSS = None
		self.cArrivalNoticeNumber = None
		self.cCarrierBookingNumber = None
		self.cBkngOfficeCode = None
		self.cBLReleasePoint = None
		self.cCommunicationReference = None
		self.cConsigneeReference = None
		self.cContainerCode = None
		self.cContainerNumber = None
		self.cContainerSize = None
		self.cContainerType = None
		self.cCustomerAlias = None
		self.tCutoffReceivingWarehouse = None
		#self.tCutoffReceivingWarehouse = None
		self.tETAPlaceOfDelivery = None
		self.tETAPortOfDischarge = None
		self.tETSPlaceOfReceipt = None
		self.tETSPortOfLoading = None
		self.cFileNumber = None
		self.cForwarderReference = None
		self.cHouseBillOfLadingNumber = None
		self.cInTransitDate = None
		self.cInTransitNumber = None
		self.cLotNumber = None
		self.cOceanVessel = None
		self.cPickupReference = None
		self.cPlaceOfDelivery = None
		self.cPlaceOfReceipt = None
		self.cPortOfDischarge = None
		self.cPortOfLoading = None
		self.cReceivingWarehouse = None
		self.cReleaseType = None
		self.cSealNumber = None
		self.cShipperReference = None
		self.cVoyage = None
		self.cLadingno = None
		self.cContainerno = None
		self.cSeal = None
		self.cVoyageno = None
		self.cVessel = None
		self.cBookingnumber = None
		# cCarrierSCAC = None
		# cStatuscode = None
		self.cStatuslocationcode = None
		self.cStatuslocationname = None
		self.cPortofloadingcode = None
		self.cPortofarrivalcode = None
		self.cPortofdischargecode = None
		self.date = None
		self.time = None
		self.timezone = None
		self.tStatusdate = None
		self.tPortofarrival = None
		self.tPortofloading = None
		self.tPortofdischarge = None
		self.TSReferenceTypeDetails = None
		self.cCarrierSCAC = None
		self.cStatuscode = None
		self.cWWAShipmentReference = None
		self.cBookingNumber = None
		self.cApplicationType = None
		self.cHouseBillOfLadingNumber = None
		self.arn = None
		self.PreviousBillOfladingNumber = None
		self.arn = None
		self.prev_arn = None
		self.parent_arn = None
		self.SenderID = None
		self.primaryBkngNumber = None
		self.cStatustype = None
		self.bookingsMerged = None
		self.export_status_received_before = None
		self.password = None
		self.temp_errors = []




	@staticmethod
	def isTransshipment(xmlDocument:XmlDocumentReader):
		return True if (xmlDocument.getXmlTagValue('./Envelope/Type') == 'transshipment_shipment_status') else False
	
	@staticmethod
	def value(tag, xmlDocument:XmlDocumentReader):
		return xmlDocument.searchXmlTagNested(tag)
	
	@staticmethod
	def values(path, xmlDocument:XmlDocumentReader):
		return xmlDocument.getXmlTags(path)

	@staticmethod
	def fromXml(xmlDocument:XmlDocumentReader, isTransshipment:bool, db:AppDatabase):

		obj = SSICommonStatus()


		# check type

		obj.isTS = isTransshipment
		obj.isSS = not isTransshipment

		# Common properties
		obj.password = xmlDocument.getXmlTagValue('./Envelope/Password')
		obj.cArrivalNoticeNumber = xmlDocument.getXmlTagValue('./ArrivalNoticeNumber')
		obj.cCarrierBookingNumber = xmlDocument.getXmlTagValue('./CarrierBookingNumber')
		obj.cBkngOfficeCode = None
		obj.cBLReleasePoint = None
		obj.cCommunicationReference = xmlDocument.getXmlTagValue('./CommunicationReference')
		obj.cConsigneeReference = xmlDocument.getXmlTagValue('./ConsigneeReference')
		obj.cContainerCode = xmlDocument.getXmlTagValue('./ContainerCode')
		obj.cContainerNumber = xmlDocument.getXmlTagValue('./ContainerNumber')
		obj.cContainerSize = xmlDocument.getXmlTagValue('./ContainerSize')
		obj.cContainerType = xmlDocument.getXmlTagValue('./ContainerType')
		obj.cCustomerAlias = xmlDocument.getXmlTagValue('./CustomerAlias')
		obj.tCutoffReceivingWarehouse = xmlDocument.getXmlTagValue('./RoutingDetails/CutoffReceivingWarehouse')
		#obj.tCutoffReceivingWarehouse = tCutoffReceivingWarehouse if tCutoffReceivingWarehouse else ''
		obj.tETAPlaceOfDelivery = xmlDocument.getXmlTagValue('./RoutingDetails/ETAPlaceOfDelivery')
		obj.tETAPortOfDischarge = xmlDocument.getXmlTagValue('./RoutingDetails/ETAPortOfDischarge')
		obj.tETSPlaceOfReceipt = xmlDocument.getXmlTagValue('./RoutingDetails/ETSPlaceOfReceipt')
		obj.tETSPortOfLoading = xmlDocument.getXmlTagValue('./RoutingDetails/ETSPortOfLoading')
		obj.cFileNumber = xmlDocument.getXmlTagValue('./FileNumber')
		obj.cForwarderReference = xmlDocument.getXmlTagValue('./ForwarderReference')
		obj.cHouseBillOfLadingNumber = xmlDocument.getXmlTagValue('./HouseBillOfLadingNumber')
		obj.cInTransitDate = xmlDocument.getXmlTagValue('./InTransitDate')
		obj.cInTransitNumber = xmlDocument.getXmlTagValue('./InTransitNumber')
		obj.cLotNumber = xmlDocument.getXmlTagValue('./LotNumber')
		obj.cOceanVessel = xmlDocument.getXmlTagValue('./OceanVessel')
		obj.cPickupReference = xmlDocument.getXmlTagValue('./PickupReference')
		obj.cPlaceOfDelivery = xmlDocument.getXmlTagValue('./RoutingDetails/PlaceOfDelivery')
		obj.cPlaceOfReceipt = xmlDocument.getXmlTagValue('./RoutingDetails/PlaceOfReceipt')
		obj.cPortOfDischarge = xmlDocument.getXmlTagValue('./RoutingDetails/PortOfDischarge')
		obj.cPortOfLoading = xmlDocument.getXmlTagValue('./RoutingDetails/PortOfLoading')
		obj.cReceivingWarehouse = xmlDocument.getXmlTagValue('./RoutingDetails/ReceivingWarehouse')
		obj.cReleaseType = xmlDocument.getXmlTagValue('./ReleaseType')
		obj.cSealNumber = xmlDocument.getXmlTagValue('./SealNumber')
		obj.cShipperReference = xmlDocument.getXmlTagValue('./ShipperReference')
		obj.cVoyage = xmlDocument.getXmlTagValue('./Voyage')
		obj.cLadingno = xmlDocument.getXmlTagValue('./HouseBillOfLadingNumber')
		obj.cContainerno = xmlDocument.getXmlTagValue('./ContainerNumber')
		obj.cSeal = xmlDocument.getXmlTagValue('./SealNumber')
		obj.cVoyageno = xmlDocument.getXmlTagValue('./Voyage')
		obj.cVessel = xmlDocument.getXmlTagValue('./OceanVessel')
		obj.cUom = xmlDocument.getXmlTagValue('./UOM')
		obj.cImageData = xmlDocument.getXmlTagValue('./DocumentationDetails/Image')
		obj.cImageLink = xmlDocument.getXmlTagValue('./DocumentationDetails/ImageLink')
		obj.cDoctype = xmlDocument.getXmlTagValue('./DocumentationDetails/ContentType')
		obj.cLotnumber = xmlDocument.getXmlTagValue('./LotNumber')
		
		# obj.cBookingnumber = xmlDocument.getXmlTagValue('./TSReference/TSReferenceNumber')

		obj.cWWAShipmentReference = xmlDocument.getXmlTagValue('./WWAShipmentReference')
		obj.cBookingNumber = xmlDocument.getXmlTagValue('./BookingNumber')
		obj.cStatusCode = xmlDocument.getXmlTagValue('./StatusCode') if xmlDocument.getXmlTagValue('./StatusCode') else xmlDocument.getXmlTagValue('./TSStatusCode')
		obj.cApplicationType = xmlDocument.getXmlTagValue('./ApplicationType')
		obj.arn = xmlDocument.getXmlTagValue('./ArrivalNoticeNumber')
		obj.PreviousBillOfladingNumber = xmlDocument.getXmlTagValue('./PreviousBillOfladingNumber')
		obj.arn = xmlDocument.getXmlTagValue('./ArrivalNoticeNumber')
		obj.prev_arn = xmlDocument.getXmlTagValue('./PrevArrivalNoticeNumber')
		obj.parent_arn = xmlDocument.getXmlTagValue('./ParentArrivalNoticeNumber')
		obj.SenderID = xmlDocument.getXmlTagValue('./Envelope/SenderID')
		obj.CargoDetails = xmlDocument.getXmlTags('./CargoDetails')
		obj.iEnteredby = ''
		obj.tEntered = datetime.now()
		obj.iUpdatedby = ''
		obj.tUpdated = datetime.now()


		obj.bookingsMerged = True if db.master().select_all_safe('SELECT COUNT(*) from sei_Member_setting INNER JOIN sei_Member ON sei_Member_setting.iMemberID = sei_Member.iMemberID where sei_Member_setting.cValue="merged_bookings" and sei_Member.cCompanycode=%s;', (obj.SenderID,))[0][0] > 0 else False
		obj.primaryBkngNumber = xmlDocument.getXmlTagValue('./BookingNumber') if obj.bookingsMerged and obj.cStatusCode > 27 else None
		
		result = db.master().select_all_safe('SELECT cStatustype FROM gen_Status WHERE cStatuscode=%s', (obj.cStatusCode,))
		obj.cStatustype = result[0][0] if result.__len__() > 0 else None

		obj.export_status_received_before = True if db.master().select_all_safe('SELECT COUNT(*) FROM track_StatusDetails INNER JOIN track_ShipmentDetails ON track_StatusDetails.cBookingNumber = track_ShipmentDetails.cBookingNumber WHERE track_ShipmentDetails.cHouseBillOfLadingNumber = %s and track_StatusDetails.cStatustype = %s;', (obj.cHouseBillOfLadingNumber, 'e'))[0][0] > 0 else False

		

		obj.date = xmlDocument.getXmlTagValue('./StatusDateTimeDetails/Date')
		obj.time = xmlDocument.getXmlTagValue('./StatusDateTimeDetails/Time')
		obj.timezone = xmlDocument.getXmlTagValue('./StatusDateTimeDetails/TimeZone')
		obj.cStatusDateTime = parse(f"{obj.date} {obj.time} {obj.timezone}") if obj.date and obj.time and obj.timezone else ''

		# SS only
		if not isTransshipment:

			obj.cLadingno = xmlDocument.getXmlTagValue('./HouseBillOfLadingNumber')

			obj.cContainerno = xmlDocument.getXmlTagValue('./ContainerNumber')
			obj.cSeal = xmlDocument.getXmlTagValue('./SealNumber')
			# cCarrierSCAC = xmlDocument.getXmlTagValue('./TSCarrierSCAC')
			# cStatuscode = xmlDocument.getXmlTagValue('./TSStatusCode')
			obj.cVoyageno = xmlDocument.getXmlTagValue('./Voyage')
			obj.cVessel = xmlDocument.getXmlTagValue('./OceanVessel')
			obj.cStatuslocationcode = xmlDocument.getXmlTagValue('./StatusLocationCode')
			obj.cStatuslocationname = xmlDocument.getXmlTagValue('./StatusLocationName')
			obj.cPortofloadingcode = xmlDocument.getXmlTagValue('./RoutingDetails/PortOfLoading')
			obj.cPortofarrivalcode = xmlDocument.getXmlTagValue('./RoutingDetails/ReceivingWarehouse')   
			obj.cPortofdischargecode = xmlDocument.getXmlTagValue('./RoutingDetails/PortOfDischarge')

			obj.tPortofarrival = xmlDocument.getXmlTagValue('./RoutingDetails/ETSPortOfLoading')
			obj.tPortofloading = xmlDocument.getXmlTagValue('./RoutingDetails/ETSPortOfLoading')
			obj.tPortofdischarge = xmlDocument.getXmlTagValue('./RoutingDetails/ETAPortOfDischarge')
			
			obj.cCarrierSCAC = xmlDocument.getXmlTagValue('./CarrierSCAC')



		# TS only

		if isTransshipment:

			obj.TSReferenceTypeDetails = int(xmlDocument.getXmlTagValue('./TSReference/TSReferenceTypeDetails'))
			obj.cWWAShipmentReference = xmlDocument.getXmlTagValue('./TSReference/TSReferenceNumber')
			obj.cContainerno = xmlDocument.getXmlTagValue('./TSContainerNumber')
			obj.cSeal = xmlDocument.getXmlTagValue('./TSSealNumber')
			obj.cCarrierSCAC = xmlDocument.getXmlTagValue('./TSCarrierSCAC')
			obj.cVoyageno = xmlDocument.getXmlTagValue('./TSVoyage')
			obj.cVessel = xmlDocument.getXmlTagValue('./TSOceanVessel')
			obj.cStatuslocationcode = xmlDocument.getXmlTagValue('./TSStatusLocationCode')
			obj.cStatuslocationname = xmlDocument.getXmlTagValue('./TSStatusLocationName')
			obj.cPortofloadingcode = xmlDocument.getXmlTagValue('./TSRoutingDetails/TSPortOfLoading')
			obj.cPortofarrivalcode = xmlDocument.getXmlTagValue('./TSRoutingDetails/ETATSPortOfArrival')
			obj.cPortofdischargecode = xmlDocument.getXmlTagValue('./TSRoutingDetails/TSPortOfDischarge')

			obj.date = xmlDocument.getXmlTagValue('./StatusDateTimeDetails/Date')
			obj.time = xmlDocument.getXmlTagValue('./StatusDateTimeDetails/Time')
			obj.timezone = xmlDocument.getXmlTagValue('./StatusDateTimeDetails/TimeZone')
			obj.tStatusdate = parse(f"{obj.date} {obj.time} {obj.timezone}") if obj.date and obj.time and obj.timezone else ''

			obj.tPortofarrival = xmlDocument.getXmlTagValue('./TSRoutingDetails/TSCFS')
			obj.tPortofloading = xmlDocument.getXmlTagValue('./TSRoutingDetails/TSPortOfLoading')
			obj.tPortofdischarge = xmlDocument.getXmlTagValue('./TSRoutingDetails/TSPortOfDischarge')


		return obj