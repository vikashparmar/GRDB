# import the 'framework' package
import sys
import os
import calendar
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import datetime
import json
from framework.formats.objects.DateTimes import DateTimes
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService
from framework.grdb.auth.AuthToken import AuthToken

class ProcessedGraphFile():
	def __init__(self,date,size_processed, interval_end=None):
		self.date =date
		self.size_processed = size_processed
		self.interval_end = interval_end

def main(event, context):
   
	try:
		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()

		if err is not None:
			return err

		# AUTHENTICATING THE ACCESS TOKEN RECEIVED IN HEADERS FROM THE CLIENT SIDE APP
		token_valid = AuthToken.validate(db, event)
		if token_valid[0]==False:
			print("PROCESSED GRAPH ROW --- INVALID ACCESS TOKEN. USER NOT AUTHORIZED. RETURNING 401.")
			return RestApiService.encode_response(401, 'JSON', None, {"message":"User is not authorized to access this information."})
			# return {"statusCode":401,  "headers": RestApiService.headers(), "body":json.dumps({"message":"User is not authorized to access this information."})}
	
		queryEnder = ''
		query_ender_values = []
		processedGraphArray=[]
		queryParams = event['queryStringParameters']
		dateTuple= (queryParams['startDate'], queryParams['endDate'])
		dateRangeFilterType = (queryParams['dateRangeFilterType'])
		
		# TO HANDLE SETTING FROM AND TO DATE TO CURRENT DATE IF IT IS NULL IN QUERY PARAMS
		dateTuple = DateTimes.ensureTuple(dateTuple)
		
		# BULDING QUERY BASED ON FILE TYPE REQUESTED
		if queryParams['fileType'] == 'FOB' or queryParams['fileType'] == 'OFR' or queryParams['fileType']=="PLC":
			queryEnder = " AND cSheetType =%s"
			query_ender_values.append(queryParams['fileType'])

		if (dateRangeFilterType == 'today' or (dateRangeFilterType == 'custom' and (queryParams['startDate'] == queryParams['endDate']))):
			myresult = prepareDataForOneDay(db, queryEnder, query_ender_values, dateTuple[0].split(' ')[0])
			for r in myresult:
				valueDict= r
				if valueDict['data']['SUM(iFileSize)']==None:
					valueDict['data']['SUM(iFileSize)']=0
				processedGraph={}
				processedGraph = ProcessedGraphFile(str(valueDict['timeIntervalStart']) ,int(valueDict['data']['SUM(iFileSize)']), str(valueDict['timeIntervalEnd']))
				pG=processedGraph.__dict__
				processedGraphArray.append(pG)
		elif dateRangeFilterType == 'week' or dateRangeFilterType == 'custom':
			searchQuery = "SELECT date(tCreated) ,SUM(iFileSize) FROM grdb_Job WHERE tCreated BETWEEN %s AND %s" + queryEnder+ " GROUP BY date(tCreated) ORDER By date(tCreated)"
			values = [dateTuple[0], dateTuple[1]] + query_ender_values
			myresult = db.module().select_all_safe(searchQuery, values, True)
			# CREATING THE ARRAY OF RESULTS WITH THE HELP OF ABOVE DEFINED CLASS
			for r in myresult:
				valueDict= r
				if valueDict['SUM(iFileSize)']!=None:
					processedGraph={}
					processedGraph = ProcessedGraphFile(str(valueDict['date(tCreated)']), int(valueDict['SUM(iFileSize)']))
					pG=processedGraph.__dict__
					processedGraphArray.append(pG)
		elif dateRangeFilterType == 'month':
			myresult = prepareDataForMonth(db, queryEnder, query_ender_values, dateTuple[1])
			for r in myresult:
				valueDict= r
				if valueDict['data']['SUM(iFileSize)']==None:
					valueDict['data']['SUM(iFileSize)']=0
				processedGraph={}
				processedGraph = ProcessedGraphFile(str(valueDict['month']) ,int(valueDict['data']['SUM(iFileSize)']))
				pG=processedGraph.__dict__
				processedGraphArray.append(pG)
				
		print(processedGraphArray)
		return RestApiService.encode_response(200, 'JSON', None, processedGraphArray)
		# return {"statusCode":200,"headers": RestApiService.headers(), "body":json.dumps(processedGraphArray)}

	except Exception as e:
		print("EXCEPTION IN LEFT GRAPH API")
		print(e)
		return RestApiService.encode_response(500, 'JSON', None, {"message":"Facing some issues fetching your information. Please refresh or retry later."})
		# return {"statusCode":500,"headers": RestApiService.headers(), "body":json.dumps({"message":"Facing some issues fetching your information. Please refresh or retry later."})}

def prepareDataForOneDay(db, queryEnder, query_ender_values, date):

	# initializing variables
	finalArray = []
	date = date + ' '
	interval = 3
	i=0
	
	# loop to fetch all interval data 
	searchQuery = "SELECT SUM(iFileSize) FROM grdb_Job WHERE tCreated BETWEEN %s AND %s" + queryEnder
	while i*interval<24:
		values = [date + str(i*interval) + ':00:00', date + str((i+1)*interval-1) + ':59:59'] + query_ender_values
		myresult = db.module().select_all_safe(searchQuery, values, True)
		myresult = {"timeIntervalStart":str(str(i*interval) + ':00:00'), "timeIntervalEnd":str(str((i+1)*interval-1) + ':59:59'), "data": myresult[0]}
		finalArray.append(myresult)
		i=i+1
	return finalArray

def prepareDataForMonth(db, queryEnder, query_ender_values, dateToday):
	i=0
	finalArray = []
	d = datetime.datetime.strptime(str(dateToday), '%Y/%m/%d %H:%M:%S')
	searchQuery = "SELECT SUM(iFileSize) FROM grdb_Job WHERE tCreated BETWEEN %s AND %s" + queryEnder
	while i<12:
		startDate = str(d.year) + '-' + str(d.month) + '-01 00:00:00'
		endDate = str(d.year) + '-' + str(d.month) + '-' + str(calendar.monthrange(d.year, d.month)[1]) +' 23:59:59'
		values = [startDate, endDate] + query_ender_values
		myresult = db.module().select_all_safe(searchQuery, values, True)
		finalArray.append({"month":startDate, "data":myresult[0]})
		d = (datetime.datetime.strptime(str(d), '%Y-%m-%d %H:%M:%S') - relativedelta(months=1))
		i=i+1
	return finalArray