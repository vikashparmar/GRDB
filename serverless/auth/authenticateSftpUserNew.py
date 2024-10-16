# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import base64
import os
import json
from framework.grdb.auth.AuthToken import AuthToken
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.cloud.storage.AwsTransferSftpService import AwsTransferSftpService
from framework.AppConfig import AppConfig
from framework.system.RestApiService import RestApiService


# Lambda function to authenticate sftp user with ssh key file upload
def main(event, context):
	try:
		
		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()

		if err is not None:
			return err

		# Validating the token
		token_valid, username = AuthToken.validate(db, event)

		if token_valid:
			print("User authenticated")

			success = False
			file_content = event['body']
			ssh_public_key = base64.b64decode(file_content).decode("utf-8")
			print(ssh_public_key)

			# calculating the server endpoint
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
			return RestApiService.encode_response(401, 'JSON', None, json.dumps({"message": "Invalid auth token"}))
	except Exception as e:
		print(e)
		return {}
	else:
		return RestApiService.encode_response(200, 'JSON', None, json.dumps({"result": msg, "success": success}))
