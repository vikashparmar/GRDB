
from framework.SSI.job.AppJob import AppJob
from framework.tracking.x12.X12Status import X12Status
from framework.system.LogService import LogService


class SSIValidations:

	@staticmethod
	def validateEnvelope(commonStatus, db):
		LogService.print("Relaxed Envelope validations for testing")
		return True
		res = db.select("SELECT cPassword FROM gen_User where cUsername=%s;", (commonStatus.cSender,))
		if res.__len__() > 0:
			hash_object = hashlib.sha1(res[0][0].encode('utf-8'))
			if hash_object == commonStatus.password:
				return True
		return False

	@staticmethod
	def validate_carrier_booking(job:AppJob):
		
		# Store all the failed validations in "failed_validations" list for logging purposes
		job.failed_validations = []
		
		res = SSIValidations.validate_carrier_booking_inner(job.x12_obj)
		if res.__len__() > 0:
			LogService.print("Errors while validating carrier booking : ", res)
			error = {
					"arrival_notice_number" : None, 
					"booking_number" : job.x12_obj.booking_number, 
					"status_code" : job.x12_obj.status_code, 
					"status_type" : 'e', 
					"customer_alias" : "", 
					"errors" : []
				}
			for err in res:
				error['errors'].append(err)
				
			job.failed_validations.append(error)

			return False
		return True

	@staticmethod
	def validate_carrier_booking_inner(x12_obj:X12Status):
		errors = []
		errors.append('CarrierBookingNumber is blank') if x12_obj.booking_number == '' else None
		errors.append('Status code is blank') if x12_obj.status_code == '' else None
		errors.append('StatusLocationCode is blank') if x12_obj.status_location_code == '' else None
		errors.append('Status Date has not been provided') if x12_obj.datetime == '' else None

		return errors if errors.__len__() > 0 else []
