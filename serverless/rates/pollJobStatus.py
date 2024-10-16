# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService
from framework.formats.objects.DictLookup import DictLookup
from framework.formats.objects.Primitives import Primitives
from framework.grdb.enums.JobStatus import JobStatus
from framework.formats.objects.DateTimes import DateTimes
from framework.grdb.core.tables.JobTable_Lambdas import JobTable_Lambdas
from framework.grdb.enums.JobProcessStatus import JobProcessStatus

class PushRate():
	def __init__(self):
		pass

def main(event, context):
	try:
		request_format = 'JSON'
		responseTag = 'pollJobStatusResponse'
		# get the data from request by decoding XML or JSON format into an object
		data, request_format, error_resp = RestApiService.decode_request(event, "pollJobStatus", responseTag)
		if error_resp is not None:
			return error_resp

		jobID = DictLookup.getValue(data,'jobID')
		requestID = DictLookup.getValue(data,'requestID')

		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()

		if err is not None:
			return err
		# fetch the data corresponding to the job id passed 
		if jobID is not None:
			value = jobID
			column = 'iJobID'
			query = "SELECT iJobID from grdb_Job WHERE iJobID=%s AND cUserName=%s"
			myresult = db.module().select_all_safe(query, [jobID, DictLookup.getValue(data,'senderID')], True)
			if len(myresult) == 0:
				return RestApiService.failure_response(401, request_format, responseTag, "JobID is not found, or you don't have permission to view this information (5).")
		elif requestID is not None and len(requestID) > 0:
			value = requestID
			column = 'cRequestID'
		else:
			return RestApiService.failure_response(400, request_format, responseTag, "Both requestID and jobID cannot be null.")
			
		query = "SELECT cUserName FROM grdb_Job WHERE {}=%s".format(column)
		myresult = db.module().select_all_safe(query, [value], True)
		if len(myresult) > 0:
			# fetch job metadata
			query = "SELECT iJobID, iTotalRowCount, iErrorRowCount, iValidatedRowCount, tJobStart, tJobEnd, tValidateStart, tValidateEnd, tInsertStart, tInsertEnd, tWaitStart, tWaitEnd, tJobDuration, tValidateDuration,tInsertDuration, tWaitDuration, cAppVersion, cStatus, cValidateErrors, cValidateWarnings, cProcessStatus FROM grdb_Job WHERE {}=%s".format(column)
			myresult = db.module().select_all_safe(query, [value], True)
			job = myresult[0]
			status = job['cStatus']
			job_id = job['iJobID']
			process_status = job['cProcessStatus']
			
			# create result obj with job info
			final_data = {
				"success":True,
				"jobID": job_id, 
				"status":status,
				"statusCode":JobStatus.CODES[status],
				"active":(status in JobStatus.IN_PROGRESS_STATUSES),
				"appVersion":job['cAppVersion'],
				"processStatus": process_status
			}
			# create value for rowcounts if wanted by client
			if DictLookup.getValueAsBool(data, 'getRowCounts') == True:
				final_data['rowCounts']  = createRowCount(job)
				
			# create value for timestapms if wanted by client
			if DictLookup.getValueAsBool(data, 'getTimestamps') == True:
				final_data['timestamps']  = createTimestamps(job)
				
			# create value for durations if wanted by client
			if DictLookup.getValueAsBool(data, 'getDurations') == True:
				final_data['durations']  = createDurations(job)
			
			# create value for errors if wanted by client
			if DictLookup.getValueAsBool(data, 'getErrors') == True:
				# get errors from DB
				final_data['errors'] = JobTable_Lambdas.decodeLogToJson(job['cValidateErrors'])
			
			# create value for warnings if wanted by client
			if DictLookup.getValueAsBool(data, 'getWarnings') == True:
				# Warnings to be added only if the job status is all processed  WGP-906
				if process_status == JobProcessStatus.ALL_PROCESSED:
					# get errors from DB
					final_data['warnings'] = JobTable_Lambdas.decodeLogToJson(job['cValidateWarnings'])

			# valid input must be status code 200
			return RestApiService.encode_response(200, request_format, responseTag, final_data)

		elif column == 'cRequestID' and not myresult:
			return RestApiService.failure_response(404, request_format, responseTag, "Cannot find job with specified RequestID")
		else:
			# invalid input must be status code 400
			return RestApiService.failure_response(400, request_format, responseTag, "No such job exists.")

	except Exception as e:
		# internal server errer must be status code 500
		print(e)
		return RestApiService.failure_response(500, request_format, responseTag, "System Error : " + str(e))

# creating dictionary for RowCounts
def createRowCount(job):
	result = {}
	result['total'] = Primitives.parseInt(job['iTotalRowCount'])
	result['error'] = Primitives.parseInt(job['iErrorRowCount'])
	result['validated'] = Primitives.parseInt(job['iValidatedRowCount'])
	return result

# creating dictionary for Timestamps 
def createTimestamps(job):
	result = {}
	result['jobStart'] = DateTimes.printISO(job['tJobStart'])
	result['jobEnd'] = DateTimes.printISO(job['tJobEnd'])
	result['validationStart'] = DateTimes.printISO(job['tValidateStart'])
	result['validationEnd'] = DateTimes.printISO(job['tValidateEnd'])
	result['insertionStart'] = DateTimes.printISO(job['tInsertStart'])
	result['insertionEnd'] = DateTimes.printISO(job['tInsertEnd'])
	result['waitStart'] = DateTimes.printISO(job['tWaitStart'])
	result['waitEnd'] = DateTimes.printISO(job['tWaitEnd'])
	return result

# creating dictionary for Durations
def createDurations(job):
	result = {}
	result['job'] = DateTimes.printDelta(job['tJobDuration'])
	result['validation'] = DateTimes.printDelta(job['tValidateDuration'])
	result['insertion'] = DateTimes.printDelta(job['tInsertDuration'])
	result['wait'] = DateTimes.printDelta(job['tWaitDuration'])
	return result


