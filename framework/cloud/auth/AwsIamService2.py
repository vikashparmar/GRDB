
import json
import botocore.exceptions
from framework.cloud.auth.AwsIamService import AwsIamService
from framework.AppConfig import AppConfig



class AwsIamService2:


	@staticmethod
	def create_iam_role_and_policy(username, s3_bucket_arn):
		resource_name = AppConfig.APP_RESOURCENAME
		role_name = f"{resource_name}-sftp-{username}-user-role"

		if not AwsIamService2.check_if_role_exists(role_name):
			AwsIamService2.create_iam_role(username, role_name)
			AwsIamService2.attach_iam_role_policy(role_name, username, s3_bucket_arn)
		return



	@staticmethod
	def check_if_role_exists(role_name):
		try:
			AwsIamService.get_iam_client().get_role(RoleName=role_name)
			print("Role already exists, skipping creation...")
			return True

		except botocore.exceptions.ClientError as error:
			if error.response['Error']['Code'] == "NoSuchEntity":
				print("Role doesn't exists, creating new one...")
			else:
				print("Error while checking if role exists")
				print(error.response['Error']['Code'])
			return False



	@staticmethod
	def create_iam_role(username, role_name):
		resource_name = AppConfig.APP_RESOURCENAME
		role_policy_document = {
			"Version": "2012-10-17",
			"Statement": [
				{
					"Effect": "Allow",
					"Principal": {
						"Service": "transfer.amazonaws.com"
					},
					"Action": "sts:AssumeRole"
				}
			]
		}

		try:
			AwsIamService.get_iam_client().create_role(
				RoleName=role_name,
				AssumeRolePolicyDocument=json.dumps(role_policy_document),
				Tags=[
					{
						'Key': 'name',
						'Value': f"{resource_name}-sftp-{username}-user-role"
					},
					{
						'Key': f"{resource_name}",
						'Value': 'true'
					},
				]
			)
			print(f"Successfully created role")

		except botocore.exceptions.ClientError as error:
			if error.response['Error']['Code'] == 'EntityAlreadyExists':
				print("Role already exists")
			else:
				print(f"Error while creating role: {error.response['Error']['Code']}")



	@staticmethod
	def attach_iam_role_policy(role_name, username, s3_bucket_arn):
		try:
			resource_name = AppConfig.APP_RESOURCENAME
			policy_name = f"{resource_name}-sftp-{username}-user-policy"
			policy_document = {
				"Version": "2012-10-17",
				"Statement": [
					{
						"Sid": "AllowListingFolder",
						"Effect": "Allow",
						"Action": [
							"s3:ListBucket",
							"s3:GetBucketLocation"
						],
						"Resource": [s3_bucket_arn],
						"Condition": {
							"StringLike": {
								"s3:prefix": [
									f"{username}/*",
									f"{username}"
								]
							}
						}
					},
					{
						"Sid": "AllowReadWriteToObject",
						"Effect": "Allow",
						"Action": [
							"s3:PutObject",
							"s3:GetObject",
							"s3:DeleteObjectVersion",
							"s3:DeleteObject",
							"s3:GetObjectVersion"
						],
						"Resource": f"{s3_bucket_arn}/{username}/*"
					},
					{
						"Sid": "TransferAccess",
						"Effect": "Allow",
						"Action": "transfer:*",
						"Resource": "*"
					}
				]
			}

			response = AwsIamService.get_iam_client().put_role_policy(
				RoleName=role_name,
				PolicyName=policy_name,
				PolicyDocument=json.dumps(policy_document)
			)
			print(response)
		except botocore.exceptions.ParamValidationError:
			print("failed to attach role policy: Invalid parameters")
			return
		except botocore.exceptions.ClientError as error:
			print("Failed to attach role policy")
			print(error.response)
			return
		else:
			print("Successfully created policy and role")
			return
