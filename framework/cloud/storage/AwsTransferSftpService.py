import boto3
import botocore.exceptions
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService
from framework.cloud.auth.AwsIamService import *

class AwsTransferSftpService:

	client = None

	@staticmethod
	def get_client():
		if AwsTransferSftpService.client is None:
			print("Creating SFTP client")
			AwsTransferSftpService.client = boto3.client('transfer',
				region_name=AppConfig.AWS_REGION,
				aws_access_key_id=AppConfig.AWS_KEY1,
				aws_secret_access_key=AppConfig.AWS_KEY2)
		return AwsTransferSftpService.client


	@staticmethod
	def create_user(sftp_server_id, username, role_arn, s3_bucket_name, ssh_public_key):
		try:
			resource_name = AppConfig.APP_RESOURCENAME
			print(f"Creating user: {username} in sftp server: {sftp_server_id}")
			response = AwsTransferSftpService.get_client().create_user(
				HomeDirectory=f"/{s3_bucket_name}/{username}",
				Role=role_arn,
				ServerId=sftp_server_id,
				SshPublicKeyBody=ssh_public_key,
				Tags=[
					{
						'Key': f"{resource_name}",
						'Value': 'true'
					},
				],
				UserName=username
			)

			print(response)
			msg, status = "Successfully created sftp user", True
		except botocore.exceptions.ParamValidationError:
			msg, status = "failed to create sftp user: Invalid parameters", False
			print(msg)
		except botocore.exceptions.ClientError as error:
			if error.response['Error']['Code'] == 'ResourceExistsException':
				msg, status = "User already exists", False
				print(msg)
			else:
				msg, status = "Failed to create sftp user", False
				print(msg)
				print(error.response)
		return msg, status



	# Create role, policy and sftp user
	@staticmethod
	def ensure_user_exists(username, ssh_public_key, s3_bucket_name, s3_bucket_arn, sftp_server_id):
		role_id, role_arn = AwsIamService.create_iam_role_and_policy(username, s3_bucket_arn)
		if role_id and role_arn:
			return AwsTransferSftpService.create_user(sftp_server_id, username, role_arn, s3_bucket_name, ssh_public_key)
		else:
			msg, status = "Failed to create role and policy, skipping sftp user creation...", False
			return msg, status