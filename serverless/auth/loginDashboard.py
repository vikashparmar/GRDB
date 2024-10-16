# import the 'framework' package
import sys
import os
from urllib.parse import unquote
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import json
from framework.grdb.auth.UserAuthentication import UserAuthentication
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService
from framework.AppConfig import AppConfig
from framework.grdb.core.tables.GenUserTable import GenUserTable
# endpoint to return the authentication result for dashboard 
def main(event, context):
	body = event['queryStringParameters']
	if body:
	
		# read request
		userid = body['userid']
		password = body['password']
		userid = unquote(userid)
		password = unquote(password)

		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()
		if err is not None:
			return err

		# validate user/pass
		data,result = UserAuthentication.validate_username_password(db, userid, password)
		if result == True:
			# check for dashboard access, file dashboard is accessible to the user with iSectionID of 1457 and iStatus = 0 in gen_Userpermission table
			file_dashboard_sectionid = GenUserTable.getSectionIDByName(db, AppConfig.FILE_DASHBOARD_ACCESS_PERMISSION)
			it_dashboard_sectionid = GenUserTable.getSectionIDByName(db, AppConfig.IT_DASHBOARD_ACCESS_PERMISSION)
			file_permission_result = GenUserTable.isUserAllowedSection(db, userid, file_dashboard_sectionid)
			it_permission_result = GenUserTable.isUserAllowedSection(db, userid, it_dashboard_sectionid)
			
			# it_permission_result = None
			if file_permission_result or it_permission_result:
				response = json.dumps({"result": True, "file": file_permission_result, "it": it_permission_result, "token": data['auth_token'], "user":userid})
			# else:
			# 	return {"statusCode": 200,"headers": RestApiService.headers(), "body": json.dumps({"result": True, "file": True, "it": False, "token": data['auth_token'], "user":userid})}
			else:
				response = json.dumps({"result": True, "file": False, "it": False, "token": data['auth_token']})
		else:
			response = json.dumps({"result": False})
		return RestApiService.encode_response(200, 'JSON', None, response)
