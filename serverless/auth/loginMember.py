# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# import libraries
import json
from framework.grdb.auth.UserAuthentication import UserAuthentication
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService

# take username and password and check for auth 
def main(event, context):
	body = event['body']
	if body:

		# read request
		body = json.loads(body)
		username = body.get('username')
		password = body.get('password')

		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()

		if err is not None:
			return err

		# validate user/pass
		msg, success = UserAuthentication.validate_username_password(db, username, password)

	else:
		msg = "Invalid request body"
		success = False
	return RestApiService.encode_response(200, 'JSON', None, json.dumps({"result": msg, "success": success}))
