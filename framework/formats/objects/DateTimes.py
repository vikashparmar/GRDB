from datetime import date, datetime

class DateTimes:

	@staticmethod
	def isValid(value, format='%Y-%m-%d'):
		try:
			datetime_object = datetime.strptime(str(value), format)
			return True
		except:
			return False
		return False

	@staticmethod
	def parse(datestring):
		try:
			datetime_object = datetime.strptime(datestring, '%Y-%m-%d')
		except:
			datetime_object = datetime.strptime(datestring, '%d-%m-%Y')
		return datetime_object

	@staticmethod
	def parseSmart(strDate):
		if len(strDate.split('-')[0]) > len(strDate.split('-')[2]):
			objDate = datetime.strptime(strDate, '%Y-%m-%d').date()
			return objDate
		else:
			date = strDate.split('-')[2]+"-"+strDate.split('-')[1]+"-"+strDate.split('-')[0]
			objDate = datetime.strptime(date, '%Y-%m-%d').date()
			return objDate

	# print date & time to standard ISO-8601 dates used by JSON
	# TODO: Generate correct coding for timezone offset
	@staticmethod
	def printISO(date):
		if date is None:
			return ''
		return date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

	# print date to standard ISO-8601 dates used by JSON
	@staticmethod
	def printDate(date):
		if date is None:
			return ''
		return date.strftime("%Y-%m-%d")

	@staticmethod
	def printDelta(delta):
		if delta is None:
			return ''
		return delta.total_seconds()

	# prints 125 seconds to something like "2h 5s" (supports year, date, hour, minute, sec)
	@staticmethod
	def printTimespan(seconds):
		years = 0
		days = 0
		if seconds >= 31536000:
			years = seconds // 31536000
			seconds %= 31536000

		if seconds >= 86400:
			days = seconds // 86400
			seconds %= 86400

		seconds = seconds % (24 * 3600)
		hour = seconds // 3600
		seconds %= 3600
		minutes = seconds // 60
		seconds %= 60
	
		result = ''
		if years != 0:
			result += str(years)+"y "
		if days != 0:
			result += str(days)+"d "
		if hour != 0:
			result += str(hour)+"h "
		if minutes != 0:
			result += str(minutes)+"m "
		if seconds != 0:
			result += str(seconds)+"s"
		return result

	@staticmethod
	def ensureTuple(dateTuple):
		today = date.today()
		if dateTuple[0] == None or dateTuple[1] == None:
			dateToday = today.strftime("%Y-%m-%d")
			print(dateToday)
			dateTuple[0] = dateTuple[1] = DateTimes._date_to_tuple(dateToday, dateToday)
			return dateTuple
		
		return DateTimes._date_to_tuple(dateTuple[0], dateTuple[1])

	@staticmethod
	def _date_to_tuple(startDate, endDate):
		return(startDate +" 00:00:00", endDate +" 23:59:59")
	
	@staticmethod
	def convertUnixTimestampToDHMS(dateTime):
		if 'd' not in dateTime:
			dateTime = '00d' + dateTime
		if 'h' not in dateTime:
			dateTime = '00h' + dateTime
		if 'm' not in dateTime:
			dateTime = '00m' + dateTime
		if 's' not in dateTime:
			dateTime = dateTime + '00'
		dateTime = dateTime.replace('d',':')
		dateTime = dateTime.replace('h',':')
		dateTime = dateTime.replace('m',':')
		dateTime = dateTime.replace('s','')
		return dateTime