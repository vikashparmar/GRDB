# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import datetime
import json
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService
from framework.grdb.auth.AuthToken import AuthToken
from framework.formats.objects.DateTimes import DateTimes

class ErrorFile():

	def __init__(self, cust_name, office_id, file_name, created_at,error_reason, cStatus, file_path):
		self.cust_name =cust_name
		self.office_id =office_id
		if file_name==None:
			file_name = "N/A"
		self.file_name = file_name
		self.created_at = created_at
		self.error_reason =error_reason
		self.cStatus = cStatus
		self.file_path = file_path

def main(event, context):
	try:
		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()

		if err is not None:
			return err
		
		# AUTHENTICATING THE ACCESS TOKEN RECEIVED IN HEADERS FROM THE CLIENT SIDE APP
		token_valid = AuthToken.validate(db, event)
		
		if token_valid[0]==False:
			print("ERROR LOGS ROW --- INVALID ACCESS TOKEN. USER NOT AUTHORIZED. RETURNING 401.")
			# return {"statusCode":401,  "headers": RestApiService.headers(), "body":json.dumps({"message":"User is not authorized to access this information."})}
			return RestApiService.encode_response(401, 'JSON', None, {"message":"User is not authorized to access this information."})
	
		errorFileArray=[]
		queryEnder=''
		queryEnder_values = []
		limiter_values = []
		query_values= []
		pagination_values = []
		queryParams =event['queryStringParameters']

		dateTuple= (queryParams['dateFrom'], queryParams['dateTo'])

		# TO HANDLE SETTING FROM AND TO DATE TO CURRENT DATE IF IT IS NULL IN QUERY PARAMS
		dateTuple = DateTimes.ensureTuple(dateTuple) 

		# IF CLIENT RETURNS SOME NULL VALUE FOR PAGINATION VARIABLES, limit AND counter
		if queryParams['limit'] == None:
			queryParams['limit'] = 10
		if queryParams['counter'] == None:
			queryParams['counter'] = 0

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

		# LIMITER IS THE VARIABLE TO HANDLES THE PART OF QUERY FOR THE LIMIT AND OFFSET, THAT IS, PAGINATION
		limiter =" limit %s offset %s"
		limiter_values = [queryParams['limit'], str(int(queryParams['counter'])*int(queryParams['limit']))]

		successErrorFileQueryPart = "((cErrorLogFilePath is not null) or cStatus='ERROR' or cStatus='FILE_FORMAT_ERROR' or cStatus='FILE_NAME_FORMAT_ERROR')"
		searchQuery = "SELECT * FROM grdb_Job WHERE tCreated BETWEEN %s and %s and " + successErrorFileQueryPart + queryEnder + " ORDER BY tCreated DESC " +  limiter
		query_values = [dateTuple[0], dateTuple[1]] + queryEnder_values + limiter_values

		# searchQuery = "SELECT * FROM grdb_Job WHERE tCreated BETWEEN '{}' and '{}' and (cOldStatus='FILE_FORMAT_ERROR' or cOldStatus ='ERROR' or (cOldStatus='COMPLETED' AND cProcessStatus='ALL REJECTED') or (cOldStatus='COMPLETED' AND cProcessStatus='PROCESSED PARTIALLY')  or (cOldStatus='ERROR' AND cProcessStatus='FILE_FORMAT_ERROR')) ORDER BY tCreated DESC".format(startDate, changedDate) + queryEnder + limiter
		queryForPagination = "SELECT COUNT(iJobID) FROM grdb_Job WHERE tCreated BETWEEN %s and %s and ((cErrorLogFilePath is not null) or cStatus='ERROR' or cStatus='FILE_FORMAT_ERROR' or cStatus='FILE_NAME_FORMAT_ERROR')" + queryEnder
		pagination_values = [dateTuple[0], dateTuple[1]] + queryEnder_values

		pagination = 0
		try:
			myresult =db.module().select_all_safe(searchQuery, query_values, True)
			pagination =db.module().select_all_safe(queryForPagination, pagination_values, True)
		except Exception as e:
			print("EXCEPTION IN ERROR LOGS API. DATABASE CONNECTION")
			print(e)
			return RestApiService.encode_response(503, 'JSON', None, {"message":"Connection to database failed. Refresh the page or retry later.","status":500})
			# return {"statusCode":503,"headers": RestApiService.headers(), "body":json.dumps({"message":"Connection to database failed. Refresh the page or retry later.","status":500})}

		# CREATING THE ARRAY OF RESULTS WITH THE HELP OF ABOVE DEFINED CLASS
		for r in myresult:
			valueDict=r
			errorFile={}
			errorFile = ErrorFile(valueDict['cCustomerName'],valueDict['cMemberCode'],valueDict['cOriginalFilename'],str(valueDict['tCreated']), valueDict['cErrorLogFilepath'], valueDict['cStatus'], valueDict['cFilePath'])
			eF=errorFile.__dict__ 
			errorFileArray.append(eF)

		pagination = pagination[0]
		pagination = pagination['COUNT(iJobID)']
		
		print(errorFileArray)

	
		# return  {"statusCode":200,"headers": RestApiService.headers(), "body":json.dumps({"data":errorFileArray,"pagination":pagination})}
		return RestApiService.encode_response(200, 'JSON', None, {"data":errorFileArray,"pagination":pagination})
		# return  {"statusCode":200,"headers": RestApiService.headers(), "body":json.dumps({"data":["data"],"pagination":0})}
	
	except Exception as e:
		print("EXCEPTION IN ERROR LOGS API")
		print(e)
		# return {"statusCode":500,"headers": RestApiService.headers(), "body":json.dumps({"message":"Facing some issues fetching your information. Please refresh or retry later.","status":500})}
		return RestApiService.encode_response(500, 'JSON', None, {"message":"Facing some issues fetching your information. Please refresh or retry later.","status":500})
