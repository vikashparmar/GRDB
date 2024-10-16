# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import json
from datetime import date
from framework.formats.objects.DateTimes import DateTimes
from framework.grdb.auth.AuthToken import AuthToken
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService
from framework.grdb.enums.JobStatus import JobStatus

# THIS FUNCTION WILL BE CALLED DIRECTLY BY SERVERLESS
def main(event, context):
	
	try:
		
		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()

		if err is not None:
			return err
		
		token_valid = AuthToken.validate(db, event)
		if token_valid[0]==False:
			print("TOP ROW --- INVALID ACCESS TOKEN. USER NOT AUTHORIZED. RETURNING 401.")
			# return {"statusCode":401, "headers": RestApiService.headers(), "body":json.dumps({"message":"User is not authorized to access this information."})}
			return RestApiService.encode_response(401, 'JSON', None, {"message":"User is not authorized to access this information."})

		# TODAY'S DATE, BECAUSE IF THE QUERY PARAMS ARE NULL DUE TO ERROR ON CLIENT, THE FROM AND TO DATE WILL BE SET TO CURRENT DATE

		queryEnder = ""
		queryEnder_values = []

		queryParams =event['queryStringParameters']
		dateTuple= (queryParams['startDate'], queryParams['endDate'])

		# TO HANDLE SETTING FROM AND TO DATE TO CURRENT DATE IF IT IS NULL IN QUERY PARAMS
		dateTuple = DateTimes.ensureTuple(dateTuple)

		# UPDATING THE queryEnder(DYNAMIC PART OF QUERY - WHERE CLAUSE) ACCORDING TO FILE TYPE RECEIVED
		if queryParams['fileType'] == 'FOB' or queryParams['fileType'] == 'PLC' or queryParams['fileType'] == 'OFR':
			queryEnder = " and cSheetType = %s "
			queryEnder_values.append(queryParams['fileType'])
		
		# UPDATING queryEnder WITH THE FROM AND TO DATE
		queryEnder = "WHERE tCreated BETWEEN %s and %s" + queryEnder  
		queryEnder_values = [dateTuple[0], dateTuple[1]] + queryEnder_values
		

		# FUNCTION TO HANDLE FETCHING ALL THE DATA FROM DB, THIS RETURNS THE DATA, WHICH IS STORED IN metricsOutput
		metricsOutput = getFileCount(db, queryEnder, queryEnder_values)
		
		print(metricsOutput)
   
		# return {"statusCode":200,  "headers": RestApiService.headers(), "body":json.dumps(metricsOutput)}
		return RestApiService.encode_response(200, 'JSON', None, metricsOutput)
	
	except Exception as e:
		print("EXCEPTION IN TOP ROW METRICS API")
		print(e)
		return RestApiService.encode_response(500, 'JSON', None, {"message":"Facing some issues fetching your information. Please refresh or retry later.","status":500})
		# return {"statusCode":500,  "headers": RestApiService.headers(), "body":json.dumps({"message":"Facing some issues fetching your information. Please refresh or retry later.","status":500})}


# HELPER FUNCTION TO ACTUALLY FETCH THE DATA FROM DB
def getFileCount(db, queryEnder, queryEnder_values):
	# HANDLES RUNNING ALL QUERIES BASED ON THE queryCondition OBJECT
	try:
		count={}
		queryCondition = {
			"created1":   ["(cStatus=%s)", [JobStatus.CREATED] ],
			"created":    ["(cStatus=%s OR cStatus=%s OR cStatus=%s OR cStatus=%s OR cStatus=%s)", [JobStatus.ERROR, JobStatus.FILE_FORMAT_ERROR, JobStatus.FILE_NAME_FORMAT_ERROR, JobStatus.FILE_SIZE_EXCEEDED, JobStatus.ABORTED] ],
			"queued":     ["(cStatus=%s)", [JobStatus.QUEUED] ],
			"validating": ["(cStatus=%s)", [JobStatus.STEP1_VALIDATING] ],
			"waiting":    ["(cStatus=%s)", [JobStatus.STEP2_WAITING] ],
			"inserting":  ["( cStatus=%s)", [JobStatus.STEP3_INSERTING] ],
			"completed":  ["(cStatus=%s)", [JobStatus.COMPLETED] ],
			"fileFOB":    ["cSheetType ='FOB'", []],
			"filesOFR":   ["cSheetType ='OFR'", []],
			"filesPLC":   ["cSheetType ='PLC'", []],
			"api":        ["cSource ='API'", []],
			"ftp":        ["cSource ='FTP'", []],
			"external":   ["cSource ='EXTERNAL'", []],
			"s3":         ["cSource ='S3_BUCKET'", []],
		}

		for key in queryCondition:
			query ="SELECT COUNT(iJobID) FROM grdb_Job " +queryEnder +" and " + queryCondition[key][0]
			values = queryEnder_values + queryCondition[key][1]
			result=db.module().select_all_safe(query, values, True)
			valueKey="COUNT(iJobID)"	 
			count[key] = result[0][valueKey]
		
		query = "SELECT AVG(tFormatValDuration), AVG(tValidateDuration), AVG(tInsertDuration), COUNT(iJobID) FROM grdb_Job " + queryEnder
		values = queryEnder_values
		result = db.module().select_all_safe(query, values, True)
		if result[0]["AVG(tFormatValDuration)"]==None:
			result[0]["AVG(tFormatValDuration)"] = 0
		if result[0]["AVG(tValidateDuration)"]==None:
			result[0]["AVG(tValidateDuration)"] = 0
		if result[0]["AVG(tInsertDuration)"]==None:
			result[0]["AVG(tInsertDuration)"] = 0
		if result[0]["COUNT(iJobID)"]==None:
			result[0]["COUNT(iJobID)"] = 0
		count['process_time'] = int(result[0]["AVG(tFormatValDuration)"] + result[0]["AVG(tValidateDuration)"])
		count['insertion_time'] = int(result[0]["AVG(tInsertDuration)"])
		count['api_usage'] = int(result[0]["COUNT(iJobID)"])
		

		# CUSTOMER WISE TABLE S
		query = "SELECT cCustomerName, COUNT(*) FROM grdb_Job " + queryEnder + " and cStatus<>'FILE_NAME_FORMAT_ERROR'  GROUP BY cCustomerName"
		result = db.module().select_all_safe(query, values, True)
		customerWise = result
		query = "SELECT cCustomerName, COUNT(*) FROM grdb_Job " + queryEnder + " and (cStatus='COMPLETED' or cStatus='ERROR' or cStatus='FILE_FORMAT_ERROR' or cStatus='FILE_NAME_FORMAT_ERROR') GROUP BY cCustomerName;"
		result = db.module().select_all_safe(query, values, True)
		totalCustomers = 0
		sumOfCustomerProcessing = 0
		for rec in customerWise:
			rec['processing'] = 0
			rec['total'] = rec['COUNT(*)']
			customerName = rec['cCustomerName']
			for processing in result:
				if processing['cCustomerName'] == customerName:
					rec['processing'] = processing['COUNT(*)']
					sumOfCustomerProcessing = int(rec['processing'])
					totalCustomers = totalCustomers + int(rec['processing'])
					break
		count['customerWise'] = customerWise 
		count['sumOfCustomerProcessing'] = totalCustomers 


		# MEMBER WISE TABLE 
		query = "SELECT cMemberCode, COUNT(*) FROM grdb_Job " + queryEnder + " and cStatus<>'FILE_NAME_FORMAT_ERROR'  GROUP BY cMemberCode"
		result = db.module().select_all_safe(query, values, True)
		memberWise = result
		query = "SELECT cMemberCode, COUNT(*) FROM grdb_Job " + queryEnder + " and (cStatus='COMPLETED' or cStatus='ERROR' or cStatus='FILE_FORMAT_ERROR' or cStatus='FILE_NAME_FORMAT_ERROR') GROUP BY cMemberCode;"
		result = db.module().select_all_safe(query, values, True)
		totalMembers = 0
		sumOfMemberProcessing = 0
		for rec in memberWise:
			rec['processing'] = 0
			rec['total'] = rec['COUNT(*)']
			memberName = rec['cMemberCode']
			for processing in result:
				if processing['cMemberCode'] == memberName:
					rec['processing'] = processing['COUNT(*)']
					sumOfMemberProcessing = int(rec['processing'])
					totalMembers = totalMembers +int(rec['processing'])
					break
		count['memberWise'] = memberWise 
		count['sumOfMemberProcessing'] = totalMembers 
		return count

	except Exception as e:
		print("EXCEPTION IN TOP ROW METRICS API, IN CONNECTING TO DB OR FETCHING QUERIES")
		print(e)
		return RestApiService.encode_response(500, 'JSON', None, {"message":"Facing some issues fetching your information. Please refresh or retry later.","status":500})
		# return {"statusCode":503,  "headers": RestApiService.headers(), "body":json.dumps({"message":"Connection to database failed. Refresh the page or retry later.","status":500})}