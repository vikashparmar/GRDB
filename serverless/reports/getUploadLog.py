# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import json
import os
from framework.formats.objects.DateTimes import DateTimes
from framework.grdb.auth.AuthToken import AuthToken
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService



class UploadLogReport():

	# def __init__(self, status, user_id, rate_format,file_type,file_name, file_size):
	def __init__(self, rate_type, status, cust_name, office_id, file_type, file_name, created_at, file_size, user_id,
				 last_updated_at, start_time, end_time, file_path, data_inserted, error_row_num, total_row_num, error_log, source):
		self.rate_type = rate_type
		self.status = status
		self.cust_name = cust_name
		self.office_id = office_id
		# self.rate_format =rate_format
		self.file_type = file_type
		self.file_name = file_name
		self.created_at = created_at
		if file_size == None:
			file_size = 0
		self.file_size = file_size
		self.user_id = user_id
		if last_updated_at == None:
			last_updated_at = 'N/A'
		self.last_updated_at = last_updated_at
		self.file_path = file_path
		# self.file_size =file_size
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
		self.start_time = start_time
		self.end_time = end_time
		self.error_log = error_log
		self.source = source


def main(event, context):
	try:
		
		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()
		if err is not None:
			return err
		
		# AUTHENTICATING THE ACCESS TOKEN RECEIVED IN HEADERS FROM THE CLIENT SIDE APP
		token_valid = AuthToken.validate(db, event)
		if token_valid[0] == False:
			print("UPLOAD LOG --- INVALID ACCESS TOKEN. USER NOT AUTHORIZED. RETURNING 401.")
			return RestApiService.encode_response(401, 'JSON', None, {"message": "User is not authorized to access this information."})
			# return {"statusCode": 401, "headers": RestApiService.headers(),
			# 		"body": json.dumps({"message": "User is not authorized to access this information."})}

		queryEnder = ''
		queryEnder_values = []
		limiter_values = []
		query_values = []
		pagination_values = []
		uploadReportArray = []
		queryParams = event['queryStringParameters']
		dateTuple = (queryParams['startDate'], queryParams['endDate'])
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
			if queryParams['jobStatus'] == 'ERROR':
				queryEnder = queryEnder + " and (cStatus = %s or cStatus = %s or cStatus = %s)"
				queryEnder_values.append('ERROR')
				queryEnder_values.append('FILE_FORMAT_ERROR')
				queryEnder_values.append('FILE_NAME_FORMAT_ERROR')
			else:
				queryEnder = queryEnder + " and cStatus = %s"
				queryEnder_values.append(queryParams['jobStatus'])
		if len(queryParams['dataSource']) > 0 and queryParams['dataSource'] != 'null' and queryParams['dataSource'] != 'ALL':
			queryEnder = queryEnder + " and cSource = %s"
			queryEnder_values.append(queryParams['dataSource'])
		# LIMITER IS THE VARIABLE TO HANDLES THE PART OF QUERY FOR THE LIMIT AND OFFSET, THAT IS, PAGINATION
		limit = queryParams['limit']
		counter = queryParams['counter']
		limiter = " limit %s offset %s"
		limiter_values = [int(limit), int(int(limit) * int(counter))]
		searchQuery = "SELECT * FROM grdb_Job WHERE tCreated BETWEEN %s and %s".format() + queryEnder + " and cFileType='online' ORDER BY tCreated DESC "  + limiter
		query_values = [dateTuple[0], dateTuple[1]] + queryEnder_values + limiter_values
		queryForPagination = "SELECT COUNT(iJobID) FROM grdb_Job WHERE tCreated BETWEEN %s and %s".format() + queryEnder
		pagination_values = [dateTuple[0], dateTuple[1]] + queryEnder_values
		pagination = 0
		myresult = db.module().select_all_safe(searchQuery, query_values, True)
		pagination = db.module().select_all_safe(queryForPagination, pagination_values, True)
		for r in myresult:
			valueDict = r
			uploadReport = {}
			# uploadReport =UploadLogReport(valueDict['status'],valueDict['user_id'], valueDict['rate_format'], valueDict['file_type'], valueDict['file_path'][valueDict['file_path'].rindex('/')+1:],str(valueDict['file_size']) + " Bytes")
			uploadReport = UploadLogReport(valueDict['cSheetType'], valueDict['cStatus'], valueDict['cCustomerName'],
										   valueDict['cMemberCode'], valueDict['cFileType'], valueDict['cOriginalFilename'],
										   str(valueDict['tCreated']), valueDict['iFileSize'], valueDict['cUserName'],
										   str(valueDict['tLastUpdated']),
											str(valueDict['tFormatValStart']), str(valueDict['tValidateEnd']),
										valueDict['cFilePath'], valueDict['cDataInserted'], valueDict['iErrorRowCount'], valueDict['iTotalRowCount'], valueDict['cErrorLogFilepath'], valueDict['cSource'])

			uR = uploadReport.__dict__
			uploadReportArray.append(uR)
		pagination = pagination[0]
		pagination = pagination['COUNT(iJobID)']
		print(uploadReportArray)
		return RestApiService.encode_response(200, 'JSON', None, {"data": uploadReportArray, "pagination": pagination})
		# return {"statusCode": 200, "headers": RestApiService.headers(),
		# 		"body": json.dumps({"data": uploadReportArray, "pagination": pagination})}

	except Exception as e:
		print("EXCEPTION IN UPLOAD LOG REPORT API")
		print(e)
		return RestApiService.encode_response(500, 'JSON', None, {"message": "Facing some issues fetching your information. Please refresh or retry later."})
		# return {"statusCode": 500, "headers": RestApiService.headers(), "body": json.dumps(
		# 	{"message": "Facing some issues fetching your information. Please refresh or retry later."})}
