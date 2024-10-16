# import the 'framework' package
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import librariesimport json
import os
from framework.grdb.auth.UserAuthentication import UserAuthentication
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.cloud.auth.AwsIamService2 import AwsIamService2
from framework.AppConfig import AppConfig
from framework.system.RestApiService import RestApiService
iam_client = None


# Lambda function to authenticate sftp user with password
def main(event, context):
	try:
		body = event['body']
		success = False
		if body:

			# read request data
			body = json.loads(body)
			username = body.get('username')
			password = body.get('password')

			# connect to DB or exit with REST API error if unable to connect
			db, err = ApiDatabase.connect()
			
			if err is not None:
				return err
			
			# Trying to authenticate the user
			if UserAuthentication.authenticate_user(db, username, password):
				s3_bucket_name = AppConfig.S3_UPLOAD_BUCKET
				s3_bucket_arn = f"arn:aws:s3:::{s3_bucket_name}"

				# creating IAM role for the current user
				AwsIamService2.create_iam_role_and_policy(username, s3_bucket_arn)
				msg = "Successfully authenticated user"
				success = True
			else:
				msg = "Invalid username or password"
		else:
			msg = "Invalid request body"
	except Exception as e:
		print("Error while validation SFTP user")
		print(e)
		return RestApiService.encode_response(500, 'JSON', None, json.dumps({"result": "Error while validation SFTP user", "success": False}))
	else:
		return RestApiService.encode_response(200, 'JSON', None, json.dumps({"result": msg, "success": success}))


