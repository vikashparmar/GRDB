from datetime import datetime
from framework.SSI.core.AppDatabase import AppDatabase
from framework.tracking.x12.X12Status import X12Status
from framework.system.LogService import LogService

class CarrierStatusTable:

	@staticmethod
	def insert(db:AppDatabase, x12_obj:X12Status):

		programID = db.select('SELECT iProgramID from gen_Program where cCode=%s', ('SSI',))
		programID = programID[0][0] if programID.__len__() > 0 else None

		cCarrierbookingnumber = x12_obj.booking_number
		# ------------- Unable to find Lading Number in the file ---------------
		cCarrierladingnumber = x12_obj.booking_number
		# ------------- Unable to find cOfficecode in the file ---------------
		cOfficecode = 0
		cCarrierstatuscode = CarrierStatusTable.map_status_code_x12(x12_obj.status_code)
		cContainernumber = x12_obj.container_code
		cCarrierSCAC = x12_obj.career_scac
		cVesselname = x12_obj.ocean_vessel
		cStatuslocationcode = x12_obj.status_location_code
		cStatuslocationname = x12_obj.status_location_code
		cPlaceofreceiptcode = x12_obj.place_of_receipt
		# ------------- Unable to find tPlaceofreceipt in the file ---------------
		tPlaceofreceipt = x12_obj.ets_port_of_loading
		cPortofloadingcode = x12_obj.port_of_loading
		tPortofloading = x12_obj.ets_port_of_loading
		cPortofdischargecode = x12_obj.port_of_discharge
		tPortofdischarge = x12_obj.eta_port_of_discharge
		cPlaceofdeliverycode = x12_obj.place_of_delivery
		# ------------- Unable to find tPlaceofdelivery in the file ---------------
		tPlaceofdelivery = x12_obj.ets_port_of_loading
		# ------------- Unable to find tStatusdate in the file ---------------
		tStatusdate = x12_obj.ets_port_of_loading
		# ------------- Unable to find cExportflag in the file ---------------
		cExportflag = 'N'
		# ------------- Unable to find iExportOwnerID in the file ---------------
		iExportOwnerID = None
		# ------------- Unable to find iImportOwnerID in the file ---------------
		iImportOwnerID = None
		iStatus = 0
		iEnteredBy = programID
		tEntered = datetime.now()
		iUpdatedBy = None
		tUpdated = None

		try:
			db.master().insert_record("tra_Carrier_status", {
				"cCarrierbookingnumber" : cCarrierbookingnumber, 
				"cCarrierladingnumber" : cCarrierladingnumber, 
				"cOfficecode" : cOfficecode, 
				"cCarrierstatuscode" : cCarrierstatuscode, 
				"cContainernumber" : cContainernumber, 
				"cCarrierSCAC" : cCarrierSCAC, 
				"cVesselname" : cVesselname, 
				"cStatuslocationcode" : cStatuslocationcode, 
				"cStatuslocationname" : cStatuslocationname, 
				"cPlaceofreceiptcode" : cPlaceofreceiptcode, 
				"tPlaceofreceipt" : tPlaceofreceipt, 
				"cPortofloadingcode" : cPortofloadingcode, 
				"tPortofloading" : tPortofloading, 
				"cPortofdischargecode" : cPortofdischargecode, 
				"tPortofdischarge" : tPortofdischarge, 
				"cPlaceofdeliverycode" : cPlaceofdeliverycode, 
				"tPlaceofdelivery" : tPlaceofdelivery, 
				"tStatusdate" : tStatusdate, 
				"cExportflag" : cExportflag, 
				"iExportOwnerID" : iExportOwnerID, 
				"iImportOwnerID" : iImportOwnerID, 
				"iStatus" : iStatus, 
				"iEnteredBy" : iEnteredBy, 
				"tEntered" : tEntered, 
				"iUpdatedBy" : iUpdatedBy, 
				"tUpdated" : tUpdated
			})
			# db.insert("INSERT INTO tra_Carrier_status (cCarrierbookingnumber, cCarrierladingnumber, cOfficecode, cCarrierstatuscode, cContainernumber, cCarrierSCAC, cVesselname, cStatuslocationcode, cStatuslocationname, cPlaceofreceiptcode, tPlaceofreceipt, cPortofloadingcode, tPortofloading, cPortofdischargecode, tPortofdischarge, cPlaceofdeliverycode, tPlaceofdelivery, tStatusdate, cExportflag, iExportOwnerID, iImportOwnerID, iStatus, iEnteredBy, tEntered, iUpdatedBy, tUpdated) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (cCarrierbookingnumber, cCarrierladingnumber, cOfficecode, cCarrierstatuscode, cContainernumber, cCarrierSCAC, cVesselname, cStatuslocationcode, cStatuslocationname, cPlaceofreceiptcode, tPlaceofreceipt, cPortofloadingcode, tPortofloading, cPortofdischargecode, tPortofdischarge, cPlaceofdeliverycode, tPlaceofdelivery, tStatusdate, cExportflag, iExportOwnerID, iImportOwnerID, iStatus, iEnteredBy, tEntered, iUpdatedBy, tUpdated))
		except:
			LogService.print("Error tra_Carrier_status.py file tra_Carrier_status()")
			return False

		return True

	@staticmethod
	def map_status_code_x12(status_code):
		code = None
		if status_code == 'AE':
			code = 810
		if status_code == 'C':
			code = 835 
		if status_code == 'E':
			code = 836 
		if status_code == 'I':
			code = 805
		if status_code == 'SD':
			code = 807
		if status_code == 'OA':
			code = 800
		if status_code == 'L':
			code = 813
		if status_code == 'UV':
			code = 811
		if status_code == 'VA':
			code = 829
		if status_code == 'VD':
			code = 823
		if status_code == 'X1':
			code = 827
		
		return code