from datetime import datetime


class X12Status:
	datetime:datetime
	sender_id:str
	receiver_id:str
	status_code:str
	status_location_code:str
	booking_number:str
	shipper_ref:str
	forwarder_Ref:str
	status_loc_code:str
	equipment_initials:str
	equipment_no:str
	container_code:str
	status_loc_code:str
	status_loc_code_alias:str
	country_code:str
	country_code:str
	ets_port_of_loading:str
	eta_port_of_discharge:str
	career_scac:str
	ocean_vessel:str
	place_of_receipt:str
	port_of_loading:str
	port_of_discharge:str
	place_of_delivery:str

	
	def __init__(self):
		self.datetime = None
		self.sender_id = None
		self.receiver_id = None
		self.status_code = None
		self.status_location_code = None
		self.booking_number = None
		self.shipper_ref = None
		self.forwarder_Ref = None
		self.status_loc_code = None
		self.equipment_initials = None
		self.equipment_no = None
		self.container_code = None
		self.status_loc_code = None
		self.status_loc_code_alias = None
		self.country_code = None
		self.country_code = None
		self.ets_port_of_loading = None
		self.eta_port_of_discharge = None
		self.career_scac = None
		self.ocean_vessel = None
		self.place_of_receipt = None
		self.port_of_loading = None
		self.port_of_discharge = None
		self.place_of_delivery = None