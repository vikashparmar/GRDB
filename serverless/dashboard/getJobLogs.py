# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import datetime
import json
from framework.formats.objects.DateTimes import DateTimes
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService
from framework.grdb.auth.AuthToken import AuthToken

class ProcessedFile():
	def __init__(self, status, cust_name, office_id,file_type,file_name, created_at, file_size, user_id, last_updated_at, sheet_type, start_time, end_time, error_log, process_status, data_inserted, error_row_num, total_row_num, file_path, source):
		self.status =status
		self.cust_name =cust_name
		self.office_id =office_id
		self.file_type=file_type
		if file_name==None:
			file_name = "N/A"
		self.file_name = file_name
		self.created_at = created_at
		if file_size==None:
			file_size = 0
		self.file_size = file_size
		self.user_id = user_id
		if last_updated_at == None:
			last_updated_at = 'N/A'
		self.last_updated_at = last_updated_at
		if sheet_type == None:
			sheet_type = 'N/A'
		self.sheet_type = sheet_type
		self.start_time = start_time
		self.end_time = end_time
		self.error_log = error_log
		self.process_status = process_status
		self.data_inserted = data_inserted
		if error_row_num == None:
			error_row_num = 0
		if error_row_num == total_row_num and error_row_num > 0:
			self.partially_inserted = 'No'
		else:
			self.partially_inserted = 'Yes'
		if error_row_num == 0:
			self.exception_found = 'No'
			self.partially_inserted = 'No'
		else:
			self.exception_found = 'Yes'
		self.file_path = file_path
		self.source = source

def main(event, context):
	try:
		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()

		if err is not None:
			return err
		
		# AUTHENTICATING THE ACCESS TOKEN RECEIVED IN HEADERS FROM THE CLIENT SIDE APP
		token_valid = AuthToken.validate(db, event)
		if token_valid[0]==False:
			print("JOB LOGS ROW --- INVALID ACCESS TOKEN. USER NOT AUTHORIZED. RETURNING 401.")
			# return {"statusCode":401,  "headers": RestApiService.headers(), "body":json.dumps({"message":"User is not authorized to access this information."})}
			return RestApiService.encode_response(401, 'JSON', None, {"message":"User is not authorized to access this information."})
		
		processedFileArray=[]
		queryParams =event['queryStringParameters']
		
		dateTuple= (queryParams['dateFrom'], queryParams['dateTo'])

		# TO HANDLE SETTING FROM AND TO DATE TO CURRENT DATE IF IT IS NULL IN QUERY PARAMS
		dateTuple = DateTimes.ensureTuple(dateTuple)

		# BULDING THE QUERY BASED ON QUERY PARAMS, LIMIT, COUNTER
		queryEnder=''
		queryEnder_values = []
		limiter_values = []
		query_values= []
		pagination_values = []
		# for key in queryParams:
		#	 if key =='officeCode':
		#		 queryEnder= queryEnder+" and office_id = '{}'".format(queryParams['officeCode'])
		#	 if key =='FileName':
		#		 queryEnder= queryEnder+" and file_path LIKE '%{}'".format(queryParams['FileName'])	 
		#	 if key =='status':
		#		 queryEnder= queryEnder+" and status = '{}'".format(queryParams['status'])
		
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
			queryEnder = queryEnder + " and UPPER(cOriginalFilename) LIKE UPPER(%s)".format(queryParams['fileName'])
			queryEnder_values.append(queryParams['fileName'] + '%')
		if len(queryParams['fileType']) > 0 and queryParams['fileType'] != 'null' and queryParams['fileType'] != 'ALL':
			queryEnder = queryEnder + " and UPPER(cSheetType) = UPPER(%s)"
			queryEnder_values.append(queryParams['fileType'])
		if len(queryParams['dataSource']) > 0 and queryParams['dataSource'] != 'null' and queryParams['dataSource'] != 'ALL':
			queryEnder = queryEnder + " and cSource = %s"
			queryEnder_values.append(queryParams['dataSource'])
		if len(queryParams['fileStatus']) > 0 and queryParams['fileStatus'] != 'null' and queryParams['fileStatus'] != 'ALL':
			if queryParams['fileStatus'] == 'ERROR':
				queryEnder = queryEnder + " and (cStatus = %s or cStatus = %s or cStatus = %s or cStatus = %s or cStatus = %s)"
				queryEnder_values.append('ERROR')
				queryEnder_values.append('FILE_FORMAT_ERROR')
				queryEnder_values.append('FILE_NAME_FORMAT_ERROR')
				queryEnder_values.append('ABORTED')
				queryEnder_values.append('FILE_SIZE_EXCEEDED')

			else:
				queryEnder = queryEnder + " and cStatus = %s"
				queryEnder_values.append(queryParams['fileStatus'])

		print(queryEnder)
		print(queryEnder_values)
		# LIMITER IS THE VARIABLE TO HANDLES THE PART OF QUERY FOR THE LIMIT AND OFFSET, THAT IS, PAGINATION
		limiter =" limit %s offset %s"
		limiter_values.append(int(queryParams['limit']))
		limiter_values.append(int(int(queryParams['counter'])*int(queryParams['limit'])))

		# successErrorFileQueryPart = "(cStatus='COMPLETED' or cStatus='ERROR' or cStatus='FILE_FORMAT_ERROR' or cStatus='FILE_NAME_FORMAT_ERROR')"
		# searchQuery = "SELECT * FROM grdb_Job WHERE tCreated BETWEEN %s and %s and " + successErrorFileQueryPart + queryEnder + " ORDER BY tCreated DESC " +  limiter
		searchQuery = "SELECT * FROM grdb_Job WHERE tCreated BETWEEN %s and %s " + queryEnder + " ORDER BY tCreated DESC " +  limiter
		query_values = [dateTuple[0], dateTuple[1]] + queryEnder_values + limiter_values

		# queryForPagination = "SELECT COUNT(iJobID) FROM grdb_Job WHERE tCreated BETWEEN %s and %s and " + successErrorFileQueryPart + queryEnder
		queryForPagination = "SELECT COUNT(iJobID) FROM grdb_Job WHERE tCreated BETWEEN %s and %s " + queryEnder
		pagination_values = [dateTuple[0], dateTuple[1]] + queryEnder_values
		print(searchQuery)
		print(query_values)
		print(queryForPagination)
		print(pagination_values)
		pagination = 0
		myresult = db.module().select_all_safe(searchQuery, query_values, True)
		pagination = db.module().select_all_safe(queryForPagination, pagination_values, True)
		pagination = pagination[0]
		pagination = pagination['COUNT(iJobID)']
		# CREATING THE ARRAY OF RESULTS WITH THE HELP OF ABOVE DEFINED CLASS
		for r in myresult:
			valueDict=r
			processedFile={}
			processedFile =ProcessedFile(valueDict['cStatus'],valueDict['cCustomerName'],valueDict['cMemberCode'],valueDict['cFileType'], valueDict['cOriginalFilename'], str(valueDict['tCreated']), valueDict['iFileSize'], valueDict['cUserName'], str(valueDict['tLastUpdated']), valueDict['cSheetType'], str(valueDict['tJobStart']), str(valueDict['tJobEnd']), valueDict['cErrorLogFilepath'], valueDict['cProcessStatus'], valueDict['cDataInserted'], valueDict['iErrorRowCount'], valueDict['iTotalRowCount'], valueDict['cFilePath'], valueDict['cSource'])
			pF=processedFile.__dict__
			processedFileArray.append(pF)

		print(processedFileArray)
		return RestApiService.encode_response(200, 'JSON', None, {"data":processedFileArray, "pagination":pagination})
		# return {"statusCode":200,"headers": RestApiService.headers(), "body":json.dumps({"data":processedFileArray, "pagination":pagination})}


	except Exception as e:
		print("EXCEPTION IN JOB LOGS API")
		print(e)
		return RestApiService.encode_response(500, 'JSON', None, {"message":"Facing some issues fetching your information. Please refresh or retry later.","status":500})
		# return {"statusCode":500,"headers": RestApiService.headers(), "body":json.dumps({"message":"Facing some issues fetching your information. Please refresh or retry later.","status":500})}
