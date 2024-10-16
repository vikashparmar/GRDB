# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import json
import os
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService
from framework.cloud.storage.AwsS3Service import AwsS3Service
from framework.grdb.auth.AuthToken import AuthToken
from framework.grdb.nameValidation.FileNameValidator_Lambdas import FileNameValidator_Lambdas
from framework.AppConfig import AppConfig
from framework.grdb.core.tables.JobTable_Lambdas import JobTable_Lambdas


def main(event, context):
	try:

		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()

		if err is not None:
			return err

		token_valid, user_name = AuthToken.validate(db, event)
		if token_valid:
			body = event['body']
			if body:
				file_name = json.loads(body)['file_name']
				
				# validating the name of file against the format (MemberScac_RateType_Customer_YYYYMMDD_HHMMSSsss)
				check_filename_format = FileNameValidator_Lambdas.validate(file_name)
				if check_filename_format == False:
					return RestApiService.encode_response(400, 'JSON', None, json.dumps({"message": "File name format is not correct."}))
				
				# Add job table entry for this file
				JobTable_Lambdas.onExternalUpload_insertJob(db, user_name,
					AppConfig.APP_RESOURCENAME, AppConfig.S3_PROCESSING_BUCKET, file_name, "EXTERNAL", None)

				# Create pre signed url
				# keep the file name without prefixing dates 
				print("Creating pre signed url..")
				s3_client = AwsS3Service.get_client()
				response = s3_client.generate_presigned_url('put_object',
															Params={'Bucket': AppConfig.S3_UPLOAD_BUCKET,
																	'Key': user_name + '/' +file_name},
															ExpiresIn=3600)
				print("Created pre signed url, returning response")
				return RestApiService.encode_response(200, 'JSON', None, json.dumps({"presignedUrl": response}))

			return RestApiService.encode_response(400, 'JSON', None, json.dumps({"message": "Invalid input data"}))
		else:
			return RestApiService.encode_response(401, 'JSON', None, json.dumps({"message": "Invalid auth token"}))
	except Exception as e:
		print("Error while generating pre signed url")
		print(e)
