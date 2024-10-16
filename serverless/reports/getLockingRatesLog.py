# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import json
import os
from framework.formats.objects.DateTimes import DateTimes
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService
from framework.grdb.auth.AuthToken import AuthToken
from framework.grdb.routingGuide.RoutingGuideMatrix import RoutingGuideMatrix

class LockingRatesLog():

	def __init__(self, cust_name, rate_type, file_type, file_name, file_size, upload_on ,uploaded_by, show_log, error_log, status):
		self.cust_name = cust_name
		self.rate_type = rate_type
		self.file_type = file_type
		self.file_name = file_name
		if file_size == None:
			file_size = 0
		self.file_size = file_size
		self.upload_on = upload_on
		self.uploaded_by = uploaded_by
		self.show_log = show_log
		self.error_log = error_log
		self.status = status

def main(event, context):

	try:
		
		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()

		if err is not None:
			return err

		# AUTHENTICATING THE ACCESS TOKEN RECEIVED IN HEADERS FROM THE CLIENT SIDE APP
		token_valid = AuthToken.validate(db, event)
		if token_valid[0]==False:
			print("LOCKING RATES LOG --- INVALID ACCESS TOKEN. USER NOT AUTHORIZED. RETURNING 401.")
			return RestApiService.encode_response(401, 'JSON', None, {"message":"User is not authorized to access this information."})
			# return {"statusCode":401,  "headers": RestApiService.headers(), "body":json.dumps({"message":"User is not authorized to access this information."})}

		queryEnder=''
		queryEnder_values = []
		limiter_values = []
		query_values = []
		pagination_values = []
		lockingReportsArray=[]
		queryParams = event['queryStringParameters']
		dateTuple= (queryParams['startDate'], queryParams['endDate'])

		# TO HANDLE SETTING FROM AND TO DATE TO CURRENT DATE IF IT IS NULL IN QUERY PARAMS
		dateTuple = DateTimes.ensureTuple(dateTuple)

		# UPDATING THE queryEnder(DYNAMIC PART OF QUERY - WHERE CLAUSE) ACCORDING TO FILE TYPE RECEIVED
		if len(queryParams['custName']) > 0 and queryParams['custName'] != 'null':
			queryEnder = queryEnder + " and UPPER(cCustomerName) LIKE UPPER(%s)"
			queryEnder_values.append(queryParams['custName'] + '%')
		if len(queryParams['officeCode']) > 0 and queryParams['officeCode'] != 'null':
			queryEnder = queryEnder + " and UPPER(cMemberCode) LIKE UPPER(%s)"
			queryEnder_values.append(queryParams['officeCode'] + '%')
		if len(queryParams['fileName']) > 0 and queryParams['fileName'] != 'null':
			queryEnder = queryEnder + " and UPPER(cOriginalFilename) LIKE UPPER(%s)"
			queryEnder_values.append(queryParams['fileName'] + '%')
		if len(queryParams['fileType']) > 0 and queryParams['fileType'] != 'null' and queryParams['fileType'] != 'ALL':
			queryEnder = queryEnder + " and UPPER(cSheetType) = UPPER(%s)"
			queryEnder_values.append(queryParams['fileType'])
		if len(queryParams['jobStatus']) > 0 and queryParams['jobStatus'] != 'null' and queryParams['jobStatus'] != 'ALL':
			queryEnder = queryEnder + " and UPPER(cStatus) = UPPER(%s)"
			queryEnder_values.append(queryParams['jobStatus'])

		# LIMITER IS THE VARIABLE TO HANDLES THE PART OF QUERY FOR THE LIMIT AND OFFSET, THAT IS, PAGINATION
		limit = queryParams['limit']
		counter=queryParams['counter']

		limiter =" limit %s offset %s"
		limiter_values = [int(limit), int(int(limit)*int(counter))] 

		subQuery = "SELECT iJobID FROM tra_Error_Log WHERE cComment LIKE '%" +  str(RoutingGuideMatrix.RoutingGuideErrorDict[5][0]) + "%' GROUP BY iJobID"

		searchQuery = "SELECT cCustomerName, cSheetType, cFileType, cOriginalFilename, iFileSize, tCreated, cUserName, cFilePath, cErrorLogFilepath, cStatus FROM grdb_Job WHERE tCreated BETWEEN %s and %s" + queryEnder  + " and iJobID IN (" + subQuery + ") ORDER BY tCreated DESC " + limiter
		query_values = [dateTuple[0], dateTuple[1]] + queryEnder_values + limiter_values

		queryForPagination = "SELECT COUNT(iJobID) FROM grdb_Job WHERE tCreated BETWEEN %s and %s" + queryEnder + " and iJobID IN (" + subQuery + ")" 
		pagination_values = [dateTuple[0], dateTuple[1]] + queryEnder_values
		pagination = 0
		
		myresult =db.module().select_all_safe(searchQuery, query_values, True)
		pagination =db.module().select_all_safe(queryForPagination, pagination_values, True)
		
		for r in myresult:
			valueDict=r
			lockingReport={}
			lockingReport = LockingRatesLog(valueDict['cCustomerName'],valueDict['cSheetType'], valueDict['cFileType'], valueDict['cOriginalFilename'], valueDict['iFileSize'], str(valueDict['tCreated']), valueDict['cUserName'], valueDict['cFilePath'], valueDict['cErrorLogFilepath'], valueDict['cStatus'])
				
			uR=lockingReport.__dict__
			lockingReportsArray.append(uR)

		pagination = pagination[0]
		pagination = pagination['COUNT(iJobID)']
		# print(lockingReportsArray)
		return RestApiService.encode_response(200, 'JSON', None, {"data":lockingReportsArray, "pagination":pagination})
		# return {"statusCode":200,"headers": RestApiService.headers(),  "body":json.dumps({"data":lockingReportsArray, "pagination":pagination})}

	except Exception as e:
		print("EXCEPTION IN LOCKING RATES LOG REPORT API")
		print(e)
		return RestApiService.encode_response(500, 'JSON', None, {"message":"Facing some issues fetching your information. Please refresh or retry later."})
		# return {"statusCode":500,"headers": RestApiService.headers(), "body":json.dumps({"message":"Facing some issues fetching your information. Please refresh or retry later."})}
