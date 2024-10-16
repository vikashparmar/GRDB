from dateutil.parser import parse

from framework.tracking.x12.X12Status import X12Status

class X12Reader:

	# reading a X12 file and returning a new X12Status object
	@staticmethod
	def read(file_obj) -> X12Status:

		# Create empty object to store the values
		data={}

		# Go to the begining fof the file and read the lines
		# file_obj.seek(0)
		lines=file_obj.decode("utf-8").split('\n')
		
		# Split the lines with '*' to get individual values from lines
		lines = [line.split('*') for line in lines]

		# Read the values and store it in the 'data' object
		data = X12Status()
		data.sender_id = lines[1][2]
		data.receiver_id = lines[1][3]

		# Get date and time values from x12 file and convert it into Python Datetime Object
		date = lines[1][4]
		time = lines[1][5]
		try:
			data.datetime = parse(f'{date[:4]}-{date[4:6]}-{date[6:8]} {time[:2]}:{time[2:4]}')
		except:
			data.datetime = ''

		# Get rest of the values
		data.status_code = lines[3][3]
		data.status_location_code = lines[3][6]
		data.booking_number = lines[4][2]
		data.shipper_ref = lines[5][2]
		data.forwarder_Ref = lines[6][2]
		data.status_loc_code = lines[3][6]
		data.equipment_initials = lines[3][7]
		data.equipment_no = lines[3][8]
		data.container_code = lines[3][10]
		data.status_loc_code = lines[3][11]
		data.status_loc_code_alias = lines[3][12]
		data.country_code = lines[8][2]
		data.country_code = lines[8][2]
		data.ets_port_of_loading = lines[8][4]
		data.eta_port_of_discharge = lines[8][5]
		data.career_scac = lines[8][10]
		data.ocean_vessel = lines[8][13]
		data.place_of_receipt = lines[9][3]
		data.port_of_loading = lines[10][3]
		data.port_of_discharge = lines[11][3]
		data.place_of_delivery = lines[12][3]

		return data

