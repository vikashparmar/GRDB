#Run all the validations defined in the tra_status_files_validation_rules table
#Define the functions for validations
#Send the final status to the main file for further process
# from db_utils import DB
import datetime, pytz, requests, os, ast, hashlib
from framework.system.LogService import LogService

class SSIValidationRuleEngine:
	def __init__(self, commonStatus, db, xmlDocument):
		self.xmlDocument = xmlDocument
		self.commonStatus = commonStatus
		self.db = db

	def isPresent(self, tag, errors=None):
		error = f'{tag} is Missing'
		# for elem in self.commonStatus.value(tag, self.xmlDocument):
		elem = self.commonStatus.value(tag, self.xmlDocument)
		if elem:
			return True
		self.commonStatus.temp_errors.append(error)
		return False

	def validateUNCode(self, tag, errors=None):
		error = f'{tag} is Invalid'
		# for elem in self.commonStatus.value(tag, self.xmlDocument):
		elem = self.commonStatus.value(tag, self.xmlDocument)
		if elem and elem.__len__() == 5:
			try:
				result = self.db.master().select_all_safe('SELECT count(*) FROM gen_Location WHERE cCode=%s', (elem,))
			except:
				self.commonStatus.temp_errors.append(error)
				return False
			if result.__len__() > 0 and  result[0][0] > 0:
				return True
		elif elem == None:
			error = f'{tag} is Missing'
		self.commonStatus.temp_errors.append(error) if error not in self.commonStatus.temp_errors else None
		return False
	
	def validateContentType(self, tag, types, errors=None):
		error = f'{tag} is Invalid'
		types = [x.lower() for x in types]
		elem = self.commonStatus.value(tag, self.xmlDocument)
		# for elem in self.commonStatus.value(tag, self.xmlDocument):
		if elem.split('/')[1] in types:
			return True
		self.commonStatus.temp_errors.append(error)
		return False
	
	def validateDate(self, tag, errors=None):
		error = f'{tag} is Invalid'
		# for elem in self.commonStatus.value(tag, self.xmlDocument):
		elem = self.commonStatus.value(tag, self.xmlDocument)
		if elem:
			try:
				datetime.datetime.strptime(elem, "%Y-%m-%d")
				return True
			except:
				self.commonStatus.temp_errors.append(error)
				return False
		else:
			error = f'{tag} is Missing'
		
		self.commonStatus.temp_errors.append(error) if error not in self.commonStatus.temp_errors else None
		
		return False
	
	def maxLength(self, tag, length, errors=None):
		error = f"{tag} exceeding it's maximum limit {length}"
		# for elem in self.commonStatus.value(tag, self.xmlDocument):
		elem = self.commonStatus.value(tag, self.xmlDocument)

		if elem and elem.__len__() > length:
			errorLogDB = f'Data {elem} Exceeding its Maximum Limit {length}'
			errorLogEmail = 'is Exceeding its Maximum Limit'
			self.commonStatus.temp_errors.append(error)
			return False
		else:
			return True
		
		self.commonStatus.temp_errors.append(error)
		
		return False
	
	def validateBookingNumber(self, errors=None):
		return True
		tag = 'BookingNumber'
		error = f'{tag} is Invalid'
		# wwaRefNumber = self.commonStatus.values('./ShipmentStatusDetails/WWAShipmentReference', self.xmlDocument) if self.commonStatus.values('./ShipmentStatusDetails/WWAShipmentReference', self.xmlDocument)!=None else None
		# bookingNumber = self.commonStatus.values('./ShipmentStatusDetails/BookingNumber', self.xmlDocument) if self.commonStatus.values('./ShipmentStatusDetails/BookingNumber', self.xmlDocument)!=None else None
		if self.commonStatus.cWWAShipmentReference == None or self.commonStatus.cBookingNumber == None:
			self.commonStatus.temp_errors.append(error)
			return False
		if self.commonStatus.cWWAShipmentReference.__len__() > 30 or self.commonStatus.cBookingNumber.__len__() > 20:
			self.commonStatus.temp_errors.append(error)
			return False
		result = self.db.master().select_all_safe('SELECT COUNT(*) FROM track_ShipmentDetails WHERE cBookingNumber=%s and cWWAShipmentReference=%s', (self.commonStatus.cBookingNumber, self.commonStatus.cWWAShipmentReference,))
		if result[0][0] > 0:
			return True
		self.commonStatus.temp_errors.append(error)
		return False
	
	def evalDates(self, tag1, operator1, tag2, operator2, value, errors=None):
		operators = {
			"==" : "Equal to",
			">" : "Greater than",
			"<" : "Less than",
			">=" : "Greater than or equal to",
			"<=" : "Less than or equal to"
		}
		# error1 = f"{tag1} should not be {operators[operator2]} {int(value)/30} months from Today's Date"
		# error2 = f'{tag1} should be {operators[operator1]} {tag2}'
		if tag1 == 'TODAY':
			date1 = datetime.datetime.today()
		else:
			elem = self.commonStatus.value(tag1, self.xmlDocument)
			# for elem in self.commonStatus.value(tag1, self.xmlDocument):
			if elem:
				try:
					date1 = datetime.datetime.strptime(elem, "%Y-%m-%d")
				except:
					return False
			else:
				return False
		if tag2 == 'TODAY':
			date2 = datetime.datetime.today()
		else:
			elem = self.commonStatus.value(tag2, self.xmlDocument)
			# for elem in self.commonStatus.value(tag2, self.xmlDocument):
			if elem:
				try:
					date2 = datetime.datetime.strptime(elem, "%Y-%m-%d")
				except:
					return False
			else:
				return False
		if operator2 and value:
			if eval('(date1'+operator1+'date2).days'+operator2+value):
				return True
			else:
				error = f"{tag1} should not be {operators[operator2]} {int(abs(int(value)/30))} months from Today's Date"
		else:
			if eval('date1'+operator1+'date2'):
				return True
			else:
				error = f'{tag1} should be {operators[operator1]} {tag2}'
		self.commonStatus.temp_errors.append(error)
		return False
	
	def validateTime(self, tag, errors=None):
		error = f'{tag} is Invalid'
		elem = self.commonStatus.value(tag, self.xmlDocument)
		# for elem in self.commonStatus.value(tag, self.xmlDocument):
		if elem:
			try:
				datetime.datetime.strptime(elem, '%H:%M:%S')
				return True
			except:
				self.commonStatus.temp_errors.append(error)
				return False
		self.commonStatus.temp_errors.append(error)
		
		return False
	
	def validateTimezone(self, tag, errors=None):
		error = f'{tag} is Invalid'
		elem = self.commonStatus.value(tag, self.xmlDocument)
		# for elem in self.commonStatus.value(tag, self.xmlDocument):
		if elem:
			try:
				pytz.timezone(elem)
				return True
			except:
				self.commonStatus.temp_errors.append(error)
				return False
		self.commonStatus.temp_errors.append(error)
		return False
	
	def validateURL(self, tag, errors=None):
		error = f'{tag} is Invalid'
		elem = self.commonStatus.value(tag, self.xmlDocument)
		# for elem in self.commonStatus.value(tag, self.xmlDocument):
		if elem:
			try:
				if requests.get(elem).status_code == 200:
					return True
			except:
				self.commonStatus.temp_errors.append(error)
				return False
		self.commonStatus.temp_errors.append(error)
		return False
	
	def tagValue(self, tag, errors=None):
		error = f'{tag} is Missing'
		elem = self.commonStatus.value(tag, self.xmlDocument)
		# for elem in self.commonStatus.value(tag, self.xmlDocument):
		if elem:
			return elem
		self.commonStatus.temp_errors.append(error)
		return ''
	#def customerAlias: all the validations are applicable for global customers only, not for local customers

	def customerAlias(self, tag, errors=None):
		error = f'{tag} is Invalid'
		elem = self.commonStatus.value(tag, self.xmlDocument)
		# for elem in self.commonStatus.value(tag, self.xmlDocument):
		if elem:
			try:
				result = self.db.master().select_all_safe('SELECT count(*) FROM gen_Customer_alias WHERE cAliascode=%s', (elem,))
			except:
				self.commonStatus.temp_errors.append(error)
				return False
			if result.__len__() > 0 and  int(result[0][0]) > 0:
				return True
		self.commonStatus.temp_errors.append(error)
		return False
	
	def isIn(self, tag, values):
		error = f'{tag} is Invalid'
		elem = self.commonStatus.value(tag, self.xmlDocument)
		# for elem in self.commonStatus.value(tag, self.xmlDocument):
		if elem and elem in values:
			return True
		else:
			self.commonStatus.temp_errors.append(error)
			return False
	
	def parent_arn(self):
		# ParentArrivalNoticeNumber = self.commonStatus.values('./ShipmentStatusDetails/ParentArrivalNoticeNumber', self.xmlDocument) if self.commonStatus.values('./ShipmentStatusDetails/ParentArrivalNoticeNumber', self.xmlDocument) is not None else None
		if self.commonStatus.parent_arn:
			resp = self.db.master().select_all_safe("SELECT COUNT(*) FROM track_ShipmentDetails WHERE cArrivalNoticeNumber=%s", (self.commonStatus.parent_arn))
			if resp[0][0] > 0:
				return True
		self.commonStatus.temp_errors.append('Parent ARN not present in DB')
		return False
		return False
	
	def check_validate_communication_reference(self):
		return True
	
	def validate_communication_reference(self, tag):
		return True

	@staticmethod
	def envelopeVal(root, db):
		LogService.print("Relaxed Envelope validations for testing")
		return True
		# sender = root.find('./Envelope/SenderID') if root.find('./Envelope/SenderID') is not None else None
		# password_hash = root.find('./Envelope/Password') if root.find('./Envelope/Password') is not None else None
		res = db.select("SELECT cPassword FROM gen_User where cUsername=%s;", (self.commonStatus.cSender,))
		if res.__len__() > 0:
			hash_object = hashlib.sha1(res[0][0].encode('utf-8'))
			if hash_object == self.commonStatus.password:
				return True
		return False

	@staticmethod
	def validate_carrier_booking(x12_obj):
		errors = []
		errors.append('CarrierBookingNumber is blank') if x12_obj['booking_number'] == '' else None
		errors.append('Status code is blank') if x12_obj['status_code'] == '' else None
		errors.append('StatusLocationCode is blank') if x12_obj['status_location_code'] == '' else None
		errors.append('Status Date has not been provided') if x12_obj['datetime'] == '' else None
		return errors if errors.__len__() > 0 else []
