# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import json
import os
from framework.grdb.auth.UserAuthentication import UserAuthentication
from framework.cloud.storage.AwsTransferSftpService import AwsTransferSftpService
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.AppConfig import AppConfig
from framework.system.RestApiService import RestApiService


# Lambda function to authenticate sftp user with ssh key
def main(event, context):
	body = event['body']
	success = False
	if body:

		# read request data
		body = json.loads(body)
		username = body.get('username')
		password = body.get('password')
		ssh_public_key = body.get('ssh_public_key')

		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()

		if err is not None:
			return err

		# trying to authenticate the user
		if UserAuthentication.authenticate_user(db, username, password):
			s3_bucket_name = AppConfig.S3_UPLOAD_BUCKET
			s3_bucket_arn = f"arn:aws:s3:::{s3_bucket_name}"
			sftp_server_id = AppConfig.SFTP_SERVER_ID
			sftp_server_endpoint = f"{sftp_server_id}.server.transfer.{AppConfig.AWS_REGION}.amazonaws.com"

			# If the user does not exists then create it
			msg, status = AwsTransferSftpService.ensure_user_exists(username, ssh_public_key, s3_bucket_name, s3_bucket_arn,
														  sftp_server_id)
			if status:
				msg, success = {"sftp_endpoint": sftp_server_endpoint, "username": username}, True
		else:
			msg = "Invalid username or password"
	else:
		msg = "Invalid request body"
		
	return RestApiService.encode_response(200, 'JSON', None, json.dumps({"result": msg, "success": success}))

