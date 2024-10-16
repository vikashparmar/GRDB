# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import json
import calendar
import datetime
from dateutil.relativedelta import relativedelta
from framework.formats.objects.DateTimes import DateTimes
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService
from framework.grdb.auth.AuthToken import AuthToken

class DataSourceGraphFile():
		def __init__(self,date,date_specifics):
			self.date = date
			self.date_specifics = date_specifics

db, err = ApiDatabase.connect()

def main(event, context):
	try:
		# connect to DB or exit with REST API error if unable to connect
		if err is not None:
			return err
		
		# AUTHENTICATING THE ACCESS TOKEN RECEIVED IN HEADERS FROM THE CLIENT SIDE APP
		token_valid = AuthToken.validate(db, event)
		if token_valid[0]==False:
			print("GRAPH DATA SOURCE ROW --- INVALID ACCESS TOKEN. USER NOT AUTHORIZED. RETURNING 401.")
			# return {"statusCode":401,  "headers": RestApiService.headers(), "body":json.dumps({"message":"User is not authorized to access this information."})}
			return RestApiService.encode_response(401, 'JSON', None, {"message":"User is not authorized to access this information."})
	
		queryEnder=''
		processedSourceGraphArray=[]
		query_values = []
		
		queryParams =event['queryStringParameters']
		dateTuple= (queryParams['startDate'], queryParams['endDate'])
		dateRangeFilterType = (queryParams['dateRangeFilterType'])

		# TO HANDLE SETTING FROM AND TO DATE TO CURRENT DATE IF IT IS NULL IN QUERY PARAMS
		dateTuple = DateTimes.ensureTuple(dateTuple)

		# UPDATING THE queryEnder(DYNAMIC PART OF QUERY - WHERE CLAUSE) ACCORDING TO FILE TYPE RECEIVED
		if queryParams['fileType'] == 'FOB' or queryParams['fileType'] == 'OFR' or queryParams['fileType']=="PLC":
			queryEnder = " AND cSheetType =%s"
		if queryEnder != '':
			query_values.append(queryParams['fileType'])

		# if month then handle accodingly 
		if dateRangeFilterType == 'month':
			myresult = prepareDataForMonth(queryEnder, query_values,  dateTuple[1])
			for rec in myresult:
				dataSourceGraph=DataSourceGraphFile(rec["month"], rec["data"])
				processedSourceGraphArray.append(dataSourceGraph.__dict__)
			return {"statusCode":200,"headers": RestApiService.headers(), "body":json.dumps(processedSourceGraphArray)}
		# if single day or today case, then handle accordingly
		elif (dateRangeFilterType == 'today' or (dateRangeFilterType == 'custom' and (queryParams['startDate'] == queryParams['endDate']))):
			myresult = prepareDataForOneDay(queryEnder, query_values, dateTuple[0].split(' ')[0])
			return {"statusCode":200,"headers": RestApiService.headers(), "body":json.dumps(myresult)}
		# these steps happen only for week and custom date range of more than 1 day 
		else:
			searchQuery = "SELECT date(tCreated) ,cSource, SUM(iFileSize) FROM grdb_Job WHERE tCreated BETWEEN %s AND %s" +queryEnder + " GROUP BY date(tCreated), cSource ORDER BY date(tCreated)"
			query_values = [dateTuple[0], dateTuple[1]] + query_values
			myresult = db.module().select_all_safe(searchQuery, query_values, True) 
					
			
			date_counter= "2024-02-03"
			dateSpec={}
			c=0
			for r in myresult:
				valueDict= r
				if valueDict['cSource'] != '' and valueDict['date(tCreated)'] != None:
			
					processedSourceGraph={}
					if valueDict['SUM(iFileSize)']==None:
						valueDict['SUM(iFileSize)'] = 0
					if c==0:
						c=1
						date_counter = str(valueDict['date(tCreated)'])
						dateSpec[valueDict['cSource']] = int(valueDict['SUM(iFileSize)'])
				
					elif date_counter != str(valueDict['date(tCreated)']):
						processedSourceGraph=DataSourceGraphFile(date_counter, dateSpec)
						dataSourceGraph=processedSourceGraph.__dict__
						processedSourceGraphArray.append(dataSourceGraph)
						date_counter = str(valueDict['date(tCreated)'])
						dateSpec ={}
						dateSpec[valueDict['cSource']] = int(valueDict['SUM(iFileSize)'])
					
					else:
						dateSpec[valueDict['cSource']] = int(valueDict['SUM(iFileSize)'])
			 
			dataSourceGraph=DataSourceGraphFile(date_counter, dateSpec)
			processedSourceGraphArray.append(dataSourceGraph.__dict__)
			return RestApiService.encode_response(200, 'JSON', None, processedSourceGraphArray)
			# return {"statusCode":200,"headers": RestApiService.headers(), "body":json.dumps(processedSourceGraphArray)}

	except Exception as e:
		print("EXCEPTION IN GRAPHS API")
		print(e)
		return RestApiService.encode_response(404, 'JSON', None, {"message":"Facing some issues fetching your information. Please refresh or retry later.","status":500})
		# return {"statusCode":404,"headers": RestApiService.headers(), "body":json.dumps({"message":"Facing some issues fetching your information. Please refresh or retry later.","status":500})}

def prepareDataForOneDay(queryEnder, query_ender_values, date):

	# initializing variables
	finalArray = []
	date = date + ' '
	interval = 3
	i=0
	
	# loop to fetch all interval data 
	searchQuery = "SELECT SUM(iFileSize) FROM grdb_Job WHERE tCreated BETWEEN %s AND %s AND cSource=%s" + queryEnder
	while i*interval<24:
		print(i*interval)
		api,external,ftp,s3=0,0,0,0
		for x in ('API', 'EXTERNAL', 'FTP', 'S3_BUCKET'):
			values = [date + str(i*interval) + ':00:00', date + str((i+1)*interval-1) + ':59:59', x] + query_ender_values
			myresult = db.module().select_all_safe(searchQuery, values, True)
			
			if myresult[0]["SUM(iFileSize)"] == None:
				myresult[0]["SUM(iFileSize)"] = 0
			if x=='API':
				api = int(myresult[0]["SUM(iFileSize)"])
			elif x=='EXTERNAL':
				external = int(myresult[0]["SUM(iFileSize)"])
			elif x=='FTP':
				ftp = int(myresult[0]["SUM(iFileSize)"])
			elif x=='S3_BUCKET':
				s3 = int(myresult[0]["SUM(iFileSize)"])
		myresult = {"timeIntervalStart":str(str(i*interval) + ':00:00'), "timeIntervalEnd":str(str((i+1)*interval-1) + ':59:59'), "api": api,"s3":s3,"external":external,"ftp":ftp}
		finalArray.append(myresult)
		i=i+1
	return finalArray

def prepareDataForMonth(queryEnder, query_ender_values, dateToday):
	i=0
	finalArray = []
	d = datetime.datetime.strptime(str(dateToday), '%Y/%m/%d %H:%M:%S')
	searchQuery = "SELECT SUM(iFileSize) FROM grdb_Job WHERE tCreated BETWEEN %s AND %s AND cSource=%s" + queryEnder
	while i<12:
		startDate = str(d.year) + '-' + str(d.month) + '-01 00:00:00'
		endDate = str(d.year) + '-' + str(d.month) + '-' + str(calendar.monthrange(d.year, d.month)[1]) +' 23:59:59'
		sourceWiseData = []
		for x in ('API', 'EXTERNAL', 'FTP', 'S3_BUCKET'):
			values = [startDate, endDate, x] + query_ender_values
			myresult = db.module().select_all_safe(searchQuery, values, True)
			if myresult[0]["SUM(iFileSize)"] == None:
				sourceWiseData.append({x: 0 })
			else:
				sourceWiseData.append({x: int(myresult[0]["SUM(iFileSize)"]) })
		finalArray.append({"month":startDate, "data":sourceWiseData})
		d = (datetime.datetime.strptime(str(d), '%Y-%m-%d %H:%M:%S') - relativedelta(months=1))
		i=i+1
	return finalArray