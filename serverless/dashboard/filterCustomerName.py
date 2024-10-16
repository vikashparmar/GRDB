# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import json
from datetime import date
from framework.grdb.auth.AuthToken import AuthToken
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService

# THIS FUNCTION IS FOR RETURNING CUSTOMER NAME MATCHING THE FILTERS ENTERED BY USER
def main(event, context):
		
	try:	
		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()
		if err is not None:
			return err
		
		# AUTHENTICATING THE ACCESS TOKEN RECEIVED IN HEADERS FROM THE CLIENT SIDE APP
		# token_valid = AuthToken.validate(db, event)
		# if token_valid[0]==False:
		#	 print("TOP ROW --- INVALID ACCESS TOKEN. USER NOT AUTHORIZED. RETURNING 401.")
		#	 return {"statusCode":401,  "headers": RestApiService.headers(), "body":json.dumps({"message":"User is not authorized to access this information."})}

		queryEnder = ""

		result = {}
		custArray = []
		
		try:
			# Fetching the all customer name
			query ="SELECT cCustomerName FROM grdb_Job GROUP BY cCustomerName"
			result=db.module().select_all_safe(query, [], True)
			print(result)
		except Exception as e:
			print("EXCEPTION IN FILTER CUSTOMER NAME. DATABASE CONNECTION")
			print(e)
			return RestApiService.encode_response(503, 'JSON', None, 
					json.dumps({"message":"Connection to database failed. Refresh the page or retry later."}))
		
		return RestApiService.encode_response(200, 'JSON', None, json.dumps(result))
	
	except Exception as e:
		print("EXCEPTION IN FILTER CUSTOMER NAME")
		print(e) 
		return RestApiService.encode_response(500, 'JSON', None, 
				json.dumps({"message":"Facing some issues fetching your information. Please refresh or retry later."}))

