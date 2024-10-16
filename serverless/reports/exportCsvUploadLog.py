# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# import libraries
import calendar
import time
import csv
import json
from botocore.exceptions import ClientError
import os
from framework.cloud.storage.AwsS3Service import AwsS3Service
from framework.formats.objects.DateTimes import DateTimes
from framework.grdb.auth.AuthToken import AuthToken
from framework.grdb.api.ApiDatabase import ApiDatabase
from framework.system.RestApiService import RestApiService
from framework.AppConfig import AppConfig

def main(event, context):
	try:
		
		# connect to DB or exit with REST API error if unable to connect
		db, err = ApiDatabase.connect()

		if err is not None:
			return err

		queryEnder = ''
		query_ender_values = []
		uploadReportArray = []
		queryParams = event['queryStringParameters']
		dateTuple = (queryParams['startDate'], queryParams['endDate'])

		# TO HANDLE SETTING FROM AND TO DATE TO CURRENT DATE IF IT IS NULL IN QUERY PARAMS
		dateTuple = DateTimes.ensureTuple(dateTuple)

		if len(queryParams['fileType']) > 0 and queryParams['fileType'] != 'null' and queryParams['fileType'] != 'ALL':
			queryEnder = queryEnder + " and UPPER(cSheetType) = UPPER(%s)"
			query_ender_values.append(queryParams['fileType'])

		searchQuery = "SELECT * FROM grdb_Job WHERE tCreated BETWEEN %s and %s" + queryEnder + " and cFileType='online' ORDER BY tCreated DESC"
		values = [dateTuple[0], dateTuple[1]] + query_ender_values

		myresult = db.module().select_all_safe(searchQuery, values, True)
		
		# gmt stores current gmtime
		gmt = time.gmtime()
		# ts stores timestamp
		ts = calendar.timegm(gmt)
		print("starting creating csv")
		# SETTING THE FILE NAME TO BE UNIQUE AS STARTDATE_ENDDATE_FILETYPE_TIMESTAMP
		report_file_name = 'uploadlog_' + queryParams['startDate'] + "_" + queryParams['endDate'] + '_' + queryParams[
			'fileType'] + '_' + str(ts) + '.csv'
		report_file_name = report_file_name.replace("/", "-")
		report_file_name = '/tmp/' + report_file_name
		print(report_file_name)
		dirname = os.path.dirname(report_file_name)
		if not os.path.exists(dirname):
			os.makedirs(dirname)

		with open(report_file_name, 'w', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(
				["Rate Format", "Status", "Customer Name", "Office Id", "File Type", "File Name", "Created At",
				 "File Size", "User Id", "Last Updated At"])
			for r in myresult:
				valueDict = r
				writer.writerow(
					[valueDict['cSheetType'], valueDict['cStatus'], valueDict['cCustomerName'], valueDict['cMemberCode'],
					 valueDict['cFileType'],  valueDict['cOriginalFilename'], valueDict['tCreated'], valueDict['iFileSize'],
					 valueDict['cUserName'], str(valueDict['tLastUpdated'])])
		print("CSV CREATED")
		object_name = report_file_name
		file_name = report_file_name
		bucket = AppConfig.S3_PROCESSING_BUCKET
		print("starting upload")
		# If S3 object_name was not specified, use file_name
		if object_name is None:
			object_name = file_name

		# Upload the file to s3 bucket
		s3_client = AwsS3Service.get_client()
		try:
			response = s3_client.upload_file(file_name, bucket, object_name)
		except ClientError as e:
			print(e)
			print("EXCEPTION IN UPLOADING THE REPORT FILE TO S3 BUCKET")
			return {"statusCode": 500, "headers": RestApiService.headers(), "body": json.dumps(
				{"message": "Facing some issues fetching your information. Please refresh or retry later."})}

		# GENERATE PRESIGNED URL TO GET THE OBJECT AND DOWNLOAD IT ON CLIENT SIDE.
		try:
			response = s3_client.generate_presigned_url('get_object',
														Params={'Bucket': bucket,
																'Key': object_name},
														ExpiresIn=3600)
		except ClientError as e:
			print(e)
			print("EXCEPTION IN GENERATING PRE SIGNED URL TO DOWNLOAD THE REPORT FILE.")
			return RestApiService.encode_response(500, 'JSON', None, {"message":"Facing some issues fetching your information. Please refresh or retry later."})
			# return {"statusCode": 500, "headers": RestApiService.headers(), "body": json.dumps(
			# 	{"message": "Facing some issues fetching your information. Please refresh or retry later."})}

		# The response contains the presigned URL			

		return RestApiService.encode_response(500, 'JSON', None, response)
		# return {"statusCode": 200, "headers": RestApiService.headers(), "body": json.dumps(response)}

	except Exception as e:
		print("EXCEPTION IN UPLOAD LOG REPORT API")
		print(e)
		return RestApiService.encode_response(500, 'JSON', None, {"message":"Facing some issues fetching your information. Please refresh or retry later."})
		# return {"statusCode": 500, "headers": RestApiService.headers(), "body": json.dumps(
		# 	{"message": "Facing some issues fetching your information. Please refresh or retry later."})}
