from framework.SSI.core.AppDatabase import AppDatabase
from pypika import Query, Table, Field
from dateutil.parser import parse
from framework.system.LogService import LogService
from framework.SSI.job.SSICommonStatus import SSICommonStatus
from framework.SSI.job.AppJob import AppJob
from framework.system.LogService import LogService
from datetime import datetime

class TransshipmentDetailsTable:

	@staticmethod
	def tra_Transshipment_detail(db:AppDatabase, commonStatus:SSICommonStatus, job:AppJob):
		#Check if the file received is in Trans Shipment Format or Shipment Status Format
		# result = self.db.select("SELECT cValue from sei_Member_setting INNER JOIN sei_Member ON sei_Member_setting.iMemberID = sei_Member.iMemberID WHERE sei_Member.cCompanycode=%s")
		# file_type = result[0][0] if result.__len__() > 0 else None
		if int(commonStatus.cStatusCode) in (1051, 1052, 1053):
			result = db.master().select_all_safe("SELECT COUNT(*) FROM tra_Transshipment_detail WHERE cBookingnumber=%s OR cLadingno=%s", (commonStatus.cBookingNumber, commonStatus.cHouseBillOfLadingNumber))
			if result[0][0] > 0:
				return True
			else:
				if TransshipmentDetailsTable.insert(db, commonStatus, job):
					return True
		else:
			if TransshipmentDetailsTable.insert(db, commonStatus, job):
				return True
		return False

	@staticmethod
	def insert(db:AppDatabase, commonStatus:SSICommonStatus, job:AppJob):
		if job.root == 'TransshipmentShipmentStatus':
			if TransshipmentDetailsTable.insert_ts_file_format(db, commonStatus):
				return True
		elif job.root == 'ShipmentStatus':
			if TransshipmentDetailsTable.insert_ss_file_format(db, commonStatus):
				return True
		else:
			LogService.print('Unsupported Tans Shipment File Format')
			return False

	@staticmethod
	def insert_ss_file_format(db:AppDatabase, commonStatus:SSICommonStatus):

		iStatus = 0
		
		result = db.master().select_all_safe("SELECT iTransshipmentdetailID FROM tra_Transshipment_detail WHERE cLadingno = %s or cBookingnumber = %s", (commonStatus.cLadingno, commonStatus.cBookingNumber))
		
		if result.__len__() > 0:
			#If record already exist then update the existing record
			try:
				db.master().update_record("tra_Transshipment_detail", "iTransshipmentdetailID", result[0][0], {
					"cContainerno" : commonStatus.cContainerno, 
					"cSeal" : commonStatus.cSeal, 
					"cCarrierSCAC" : commonStatus.cCarrierSCAC, 
					"cStatuscode" : commonStatus.cStatusCode, 
					"cVoyageno" : commonStatus.cVoyageno,
					"cVessel" : commonStatus.cVessel,
					"cStatuslocationcode" : commonStatus.cStatuslocationcode,
					"cStatuslocationname" : commonStatus.cStatuslocationname,
					"cPortofloadingcode" : commonStatus.cPortofloadingcode,
					"cPortofarrivalcode" : commonStatus.cPortofarrivalcode,
					"cPortofdischargecode" : commonStatus.cPortofdischargecode,
					"tStatusdate" : commonStatus.tStatusdate,
					"tPortofarrival" : commonStatus.tPortofarrival,
					"tPortofloading" : commonStatus.tPortofloading,
					"tPortofdischarge" : commonStatus.tPortofdischarge,
					"tUpdated" : datetime.now()
				})
				# self.db.update("UPDATE tra_Transshipment_detail SET cContainerno=%s, cSeal=%s, cCarrierSCAC=%s, cStatuscode=%s, cVoyageno=%s, cVessel=%s, cStatuslocationcode=%s, cStatuslocationname=%s, cPortofloadingcode=%s, cPortofarrivalcode=%s, cPortofdischargecode=%s, tStatusdate=%s, tPortofarrival=%s, tPortofloading=%s, tPortofdischarge=%s, tUpdated=%s WHERE iTransshipmentdetailID=%s", (cContainerno, cSeal, commonStatus.cCarrierSCAC, commonStatus.cStatusCode, cVoyageno, cVessel, cStatuslocationcode, cStatuslocationname, cPortofloadingcode, cPortofarrivalcode, cPortofdischargecode, tStatusdate, tPortofarrival, tPortofloading, tPortofdischarge, self.tUpdated, result[0][0]))
				LogService.print('Record updated in tra_Transshipment_detail')
				return True
			except:
				LogService.print("Error while updating the record in tra_Transshipment_detail table")
		else:
			#If record does not exist then insert the record
			try:
				db.master()._insert_id_safe("INSERT INTO tra_Transshipment_detail (cBookingnumber, cLadingno, cContainerno, cSeal, cCarrierSCAC, cStatuscode, cVoyageno, cVessel, cStatuslocationcode, cStatuslocationname, cPortofloadingcode, cPortofarrivalcode, cPortofdischargecode, tStatusdate, tPortofarrival, tPortofloading, tPortofdischarge, iStatus, tEntered) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (commonStatus.cBookingNumber, commonStatus.cLadingno, commonStatus.cContainerno, commonStatus.cSeal, commonStatus.cCarrierSCAC, commonStatus.cStatusCode, commonStatus.cVoyageno, commonStatus.cVessel, commonStatus.cStatuslocationcode, commonStatus.cStatuslocationname, commonStatus.cPortofloadingcode, commonStatus.cPortofarrivalcode, commonStatus.cPortofdischargecode, commonStatus.tStatusdate, commonStatus.tPortofarrival, commonStatus.tPortofloading, commonStatus.tPortofdischarge, iStatus, datetime.now()))
				LogService.print('Record Inserted in tra_Transshipment_detail')
				return True
			except:
				LogService.print("Error while inserting the record in tra_Transshipment_detail table")
		return False


	@staticmethod
	def insert_ts_file_format(db:AppDatabase, commonStatus:SSICommonStatus):
		
		iStatus = 0

		if commonStatus.TSReferenceTypeDetails == 1:
			# cLadingno = self.getXmlTagValue('./TSStatusDetails/TSReference/TSReferenceNumber')
			#Check if record already exists in the table
			result = db.master().select_all_safe("SELECT iTransshipmentdetailID FROM tra_Transshipment_detail WHERE cLadingno = %s", (commonStatus.cLadingno,))
			if result.__len__() > 0:
				#If record already exist then update the existing record
				try:
					db.master().update_record("tra_Transshipment_detail", "iTransshipmentdetailID", result[0][0], {
						"cContainerno" : commonStatus.cContainerno, 
						"cSeal" : commonStatus.cSeal, 
						"cCarrierSCAC" : commonStatus.cCarrierSCAC, 
						"cStatuscode" : commonStatus.cStatusCode, 
						"cVoyageno" : commonStatus.cVoyageno,
						"cVessel" : commonStatus.cVessel,
						"cStatuslocationcode" : commonStatus.cStatuslocationcode,
						"cStatuslocationname" : commonStatus.cStatuslocationname,
						"cPortofloadingcode" : commonStatus.cPortofloadingcode,
						"cPortofarrivalcode" : commonStatus.cPortofarrivalcode,
						"cPortofdischargecode" : commonStatus.cPortofdischargecode,
						"tStatusdate" : commonStatus.tStatusdate,
						"tPortofarrival" : commonStatus.tPortofarrival,
						"tPortofloading" : commonStatus.tPortofloading,
						"tPortofdischarge" : commonStatus.tPortofdischarge,
						"tUpdated" : datetime.now()
					})
					# self.db.update("UPDATE tra_Transshipment_detail SET cContainerno=%s, cSeal=%s, cCarrierSCAC=%s, cStatuscode=%s, cVoyageno=%s, cVessel=%s, cStatuslocationcode=%s, cStatuslocationname=%s, cPortofloadingcode=%s, cPortofarrivalcode=%s, cPortofdischargecode=%s, tStatusdate=%s, tPortofarrival=%s, tPortofloading=%s, tPortofdischarge=%s, tUpdated=%s WHERE iTransshipmentdetailID=%s", (cContainerno, cSeal, cCarrierSCAC, cStatuscode, cVoyageno, cVessel, cStatuslocationcode, cStatuslocationname, cPortofloadingcode, cPortofarrivalcode, cPortofdischargecode, tStatusdate, tPortofarrival, tPortofloading, tPortofdischarge, self.tUpdated, result[0][0]))
					LogService.print('Record updated in tra_Transshipment_detail')
					return True
				except:
					LogService.print("Error while updating the record in tra_Transshipment_detail table")
			else:
				#If record does not exist then insert the record
				try:
					db.master()._insert_id_safe("INSERT INTO tra_Transshipment_detail (cLadingno, cContainerno, cSeal, cCarrierSCAC, cStatuscode, cVoyageno, cVessel, cStatuslocationcode, cStatuslocationname, cPortofloadingcode, cPortofarrivalcode, cPortofdischargecode, tStatusdate, tPortofarrival, tPortofloading, tPortofdischarge, iStatus, tEntered) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (commonStatus.cLadingno, commonStatus.cContainerno, commonStatus.cSeal, commonStatus.cCarrierSCAC, commonStatus.cStatuscode, commonStatus.cVoyageno, commonStatus.cVessel, commonStatus.cStatuslocationcode, commonStatus.cStatuslocationname, commonStatus.cPortofloadingcode, commonStatus.cPortofarrivalcode, commonStatus.cPortofdischargecode, commonStatus.tStatusdate, commonStatus.tPortofarrival, commonStatus.tPortofloading, commonStatus.tPortofdischarge, iStatus, datetime.now()))
					LogService.print('Record Inserted in tra_Transshipment_detail')
					return True
				except:
					LogService.print("Error while inserting the record in tra_Transshipment_detail table")
		elif commonStatus.TSReferenceTypeDetails == 2:
			#Check if record already exists in the table
			result = db.master().select_all_safe("SELECT iTransshipmentdetailID FROM tra_Transshipment_detail WHERE cBookingnumber = %s", (commonStatus.cBookingnumber,))
			if result.__len__() > 0:
				#If record already exist then update the existing record
				try:
					db.master().update_record("tra_Transshipment_detail", "iTransshipmentdetailID", result[0][0], {
						"cContainerno" : commonStatus.cContainerno, 
						"cSeal" : commonStatus.cSeal, 
						"cCarrierSCAC" : commonStatus.cCarrierSCAC, 
						"cStatuscode" : commonStatus.cStatusCode, 
						"cVoyageno" : commonStatus.cVoyageno,
						"cVessel" : commonStatus.cVessel,
						"cStatuslocationcode" : commonStatus.cStatuslocationcode,
						"cStatuslocationname" : commonStatus.cStatuslocationname,
						"cPortofloadingcode" : commonStatus.cPortofloadingcode,
						"cPortofarrivalcode" : commonStatus.cPortofarrivalcode,
						"cPortofdischargecode" : commonStatus.cPortofdischargecode,
						"tStatusdate" : commonStatus.tStatusdate,
						"tPortofarrival" : commonStatus.tPortofarrival,
						"tPortofloading" : commonStatus.tPortofloading,
						"tPortofdischarge" : commonStatus.tPortofdischarge,
						"tUpdated" : datetime.now()
					})
					# self.db.update("UPDATE tra_Transshipment_detail SET cContainerno=%s, cSeal=%s, cCarrierSCAC=%s, cStatuscode=%s, cVoyageno=%s, cVessel=%s, cStatuslocationcode=%s, cStatuslocationname=%s, cPortofloadingcode=%s, cPortofarrivalcode=%s, cPortofdischargecode=%s, tStatusdate=%s, tPortofarrival=%s, tPortofloading=%s, tPortofdischarge=%s, tUpdated=%s WHERE iTransshipmentdetailID=%s", (cContainerno, cSeal, cCarrierSCAC, cStatuscode, cVoyageno, cVessel, cStatuslocationcode, cStatuslocationname, cPortofloadingcode, cPortofarrivalcode, cPortofdischargecode, tStatusdate, tPortofarrival, tPortofloading, tPortofdischarge, self.tUpdated, result[0][0]))
					LogService.print('Record updated in tra_Transshipment_detail')
					return True
				except:
					LogService.print("Error while updating the record in tra_Transshipment_detail table")  
			else:
				#If record does not exist then insert the record
				try:
					db.master()._insert_id_safe("INSERT INTO tra_Transshipment_detail (cBookingnumber, cContainerno, cSeal, cCarrierSCAC, cStatuscode, cVoyageno, cVessel, cStatuslocationcode, cStatuslocationname, cPortofloadingcode, cPortofarrivalcode, cPortofdischargecode, tStatusdate, tPortofarrival, tPortofloading, tPortofdischarge, iStatus, tEntered) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (commonStatus.cBookingnumber, commonStatus.cContainerno, commonStatus.cSeal, commonStatus.cCarrierSCAC, commonStatus.cStatuscode, commonStatus.cVoyageno, commonStatus.cVessel, commonStatus.cStatuslocationcode, commonStatus.cStatuslocationname, commonStatus.cPortofloadingcode, commonStatus.cPortofarrivalcode, commonStatus.cPortofdischargecode, commonStatus.tStatusdate, commonStatus.tPortofarrival, commonStatus.tPortofloading, commonStatus.tPortofdischarge, iStatus, datetime.now()))
					LogService.print('Record Inserted in tra_Transshipment_detail')
					return True
				except:
					LogService.print("Error while inserting the record in tra_Transshipment_detail table")
		return False