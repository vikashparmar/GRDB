# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import json
from framework.system.RestApiService import RestApiService
from framework.cloud.storage.AwsS3Service import AwsS3Service


def main(event, context):
	try:

		# if token_valid:
		query_strings = event['queryStringParameters']
		if query_strings:
			file_path = query_strings['file_path']
			if file_path:
				file_name = file_path.split('/',1)[1]
				bucket_name = file_path.split('/')[0]
				print(bucket_name)
				print(f"Creating pre signed url for file: {file_name} in bucket: {bucket_name}")

				s3_client = AwsS3Service.get_client()
				response = s3_client.generate_presigned_url('get_object',
															Params={'Bucket': bucket_name,
																	'Key': file_name},
															ExpiresIn=3600)
				print("Created pre signed url, returning response")
				print(response)
				return {"statusCode": 200,"headers": RestApiService.headers(), "body": json.dumps({"download_url": response})}

		return {"statusCode": 400,"headers": RestApiService.headers(), "body": json.dumps({"message": "Invalid input data"})}

		# else:
		#	 return {"statusCode": 401, "body": json.dumps({"message": "Invalid auth token"})}
	except Exception as e:
		print("Error while creating pre signed url")
		print(e)
