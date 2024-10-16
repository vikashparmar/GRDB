
import json
import boto3
import botocore.exceptions
from framework.AppConfig import AppConfig

client = None


class AwsIamService:

	client = None


	@staticmethod
	def get_iam_client():
		if AwsIamService.client is None:
			print("Creating IAM client")
			AwsIamService.client = boto3.client('iam',
				region_name=AppConfig.AWS_REGION,
				aws_access_key_id=AppConfig.AWS_KEY1,
				aws_secret_access_key=AppConfig.AWS_KEY2)
		return AwsIamService.client


	@staticmethod
	def create_iam_role_and_policy(username, s3_bucket_arn):
		resource_name = AppConfig.APP_RESOURCENAME
		role_name = f"{resource_name}-sftp-{username}-user-role"

		status, role_id, role_arn = AwsIamService.check_if_role_exists(role_name)

		if not status:
			role_id, role_arn = AwsIamService.create_iam_role(username, role_name)

			policy_name = f"{resource_name}-sftp-{username}-user-policy"

			policy_arn = AwsIamService.create_iam_policy(username, s3_bucket_arn, policy_name)
			print(f"policy arn: {policy_arn}")

			AwsIamService.attach_iam_role_policy(policy_arn, role_name)

		response_data = {
			"role_id": role_id,
			"role_arn": role_arn,
			"role_name": role_name
		}
		print(response_data)

		return role_id, role_arn



	@staticmethod
	def check_if_role_exists(role_name):
		try:
			response = AwsIamService.get_iam_client().get_role(RoleName=role_name)

			role_id, role_arn = response['Role']['RoleId'], response['Role']['Arn']

			print("Role already exists, skipping creation...")

			return True, role_id, role_arn

		except botocore.exceptions.ClientError as error:
			if error.response['Error']['Code'] == "NoSuchEntity":
				print("Role doesn't exists, creating new one...")
			else:
				print("Error while checking if role exists")
				print(error.response['Error']['Code'])
			return False, None, None



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
			response = AwsIamService.get_iam_client().create_role(
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

			role_id, role_arn = response['Role']['RoleId'], response['Role']['Arn']
			return role_id, role_arn

		except botocore.exceptions.ClientError as error:
			if error.response['Error']['Code'] == 'EntityAlreadyExists':
				print("Role already exists")
				return role_name, "", ""
			else:
				print(f"Error while creating role: {error.response['Error']['Code']}")
				return None, None, None



	@staticmethod
	def check_if_policy_exists(role_name, policy_name):
		try:

			response = AwsIamService.get_iam_client().get_role_policy(
				RoleName=role_name,
				PolicyName=policy_name
			)
			print(response)
			return True
		except botocore.exceptions.ClientError as error:
			if error.response['Error']['Code'] == 'NoSuchEntity':
				print("Policy doesn't exists")
			else:
				print(f"Error while checking policy exists: {error.response['Error']['Code']}")
			return False


	@staticmethod
	def create_iam_policy(username, s3_bucket_arn, policy_name):
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
					"Resource": f"{s3_bucket_arn}",
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
					"Resource": f"{s3_bucket_arn}/{username}*"
				}
			]
		}
		try:
			response = AwsIamService.get_iam_client().create_policy(
				PolicyName=policy_name,
				PolicyDocument=json.dumps(policy_document)
			)
			return response['Policy']['Arn']

		except botocore.exceptions.ClientError as error:
			if error.response['Error']['Code'] == 'EntityAlreadyExists':
				print("Policy already exists")
				return ""
			else:
				print(f"Error while creating policy: {error.response['Error']['Code']}")
				return None


	@staticmethod
	def attach_iam_role_policy(policy_arn, role_name):
		try:
			response = AwsIamService.get_iam_client().attach_role_policy(
				PolicyArn=policy_arn,
				RoleName=role_name,
			)
		except botocore.exceptions.ParamValidationError:
			print("failed to attach role policy: Invalid parameters")
		except botocore.exceptions.ClientError as error:
			print("Failed to attach role policy")
			print(error.response)
		return
