# Change config file
import sys
import json

# Read command line arguments
sftp_server_id = sys.argv[1]
resource_name = sys.argv[2]
environment = sys.argv[3]
security_group_id = sys.argv[4]
private_subnet_ids = sys.argv[5]
serverless_lambda_iam_arn = sys.argv[6]

# Load config file
config_file_path = f"config/{environment}.json"
with open(config_file_path, "r+") as config_file:
	config = json.load(config_file)

	if private_subnet_ids:
		# Parse subnets IDs
		private_subnet_ids = private_subnet_ids.replace("\n", "")
		private_subnet_ids = private_subnet_ids.replace("[", "")
		private_subnet_ids = private_subnet_ids.replace("]", "")
		private_subnet_ids = private_subnet_ids.replace(" ", "")
		private_subnet_ids = private_subnet_ids.split(",")

		subnet_id_1 = private_subnet_ids[0]
		subnet_id_2 = private_subnet_ids[1]
		config["subNetId1"] = subnet_id_1
		config["subNetId2"] = subnet_id_2

	if sftp_server_id:
		config["sftpServerId"] = sftp_server_id

	if resource_name:
		config["resourceName"] = resource_name

	if security_group_id:
		config["securityGroupId"] = security_group_id

	if serverless_lambda_iam_arn:
		config["iamArn"] = serverless_lambda_iam_arn

	config_file.seek(0)
	json.dump(config, config_file)
	config_file.truncate()
