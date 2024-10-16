# import the 'framework' package
from logging import currentframe
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import json
import datetime
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService
from framework.grdb.auth.AuthToken import AuthToken
from framework.grdb.infra.PodTable import PodTable
from framework.formats.objects.DateTimes import DateTimes 
from framework.AppConfig import AppConfig
from framework.grdb.infra.HeartbeatService import HeartbeatService

def main(event, context):
	try:
		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()

		if err is not None:
			return err
		
		queryParams =event['queryStringParameters']
		print(queryParams)
		
		# AUTHENTICATING THE ACCESS TOKEN RECEIVED IN HEADERS FROM THE CLIENT SIDE APP
		token_valid = AuthToken.validate(db, event)
		if token_valid[0]==False:
			print("IT Dashboard --- INVALID ACCESS TOKEN. USER NOT AUTHORIZED. RETURNING 401.")
			# return {"statusCode":401,  "headers": RestApiService.headers(), "body":json.dumps({"message":"User is not authorized to access this information."})}		
			return RestApiService.encode_response(401, 'JSON', None, {"message":"User is not authorized to access this information."})

			
		queryEnder = ''

		if len(queryParams['podName']) > 0 and queryParams['podName'] != 'null':
			queryEnder = queryEnder + " and UPPER(grdb_Pod.cPodName) LIKE UPPER('{}%')".format(queryParams['podName'])
		if len(queryParams['fileName']) > 0 and queryParams['fileName'] != 'null':
			queryEnder = queryEnder + " and UPPER(grdb_Job.cOriginalFilename) LIKE UPPER('{}%')".format(queryParams['fileName'])

		# query = "SELECT grdb_Pod.cPodName, cNodeId, cIP, cPodStatus, tAge, cOriginalFilename, cStatus FROM grdb_Pod JOIN grdb_Job WHERE grdb_Pod.cPodName = grdb_Job.cPodName"

		myresult = PodTable.getRunningPodsAndJobs(db, queryEnder)
		mypodcount = PodTable.getRunningPodsCountByStatus(db, queryEnder)
		totalpods = PodTable.getRunningPodsCount(db, queryEnder)
		for rec in myresult:
			rec['podHung'] = HeartbeatService.isPodHung(rec, True)
			rec['tHeartbeat'] = str(rec['tHeartbeat'])
			rec['tAge'] = DateTimes.convertUnixTimestampToDHMS(rec['tAge'])
		return RestApiService.encode_response(401, 'JSON', None, {"data":(myresult),"count":(mypodcount), "totalcount":(totalpods)})
		# return {"statusCode":200,"headers": RestApiService.headers(), "body":json.dumps({"data":(myresult),"count":(mypodcount), "totalcount":(totalpods)})}


	except Exception as e:
		print("EXCEPTION IN JOB LOGS API")
		print(e)
		return RestApiService.encode_response(500, 'JSON', None, {"message":"Facing some issues fetching your information. Please refresh or retry later."})
		# return {"statusCode":500,"headers": RestApiService.headers(), "body":json.dumps({"message":"Facing some issues fetching your information. Please refresh or retry later.","status":500})}