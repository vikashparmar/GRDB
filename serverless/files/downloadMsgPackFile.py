# import the 'framework' package
import sys
import os
import msgpack
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import json
from framework.system.RestApiService import RestApiService
from framework.cloud.storage.AwsS3Service import AwsS3Service
from framework.grdb.api.ApiDatabase import ApiDatabase


def main(event, context):
    try:

        # connect to DB or exit with REST API error if unable to connect
        db, err = ApiDatabase.connect()

        if err is not None:
            return err
            
        query_strings = event['queryStringParameters']
        if query_strings:
            file_path = query_strings['file_path']
            if file_path:
                presigned_url = ''
                print(file_path)
                searchQuery = "SELECT * FROM grdb_Job WHERE cFilePath=%s;"
                query_values = [str(file_path)]
                myresult = db.module().select_all_safe(searchQuery, query_values, True)
                jobID = myresult[0]['iJobID']

                searchQuery = "SELECT cRequestBody FROM grdb_API_requestLogs WHERE iJobID=%s"
                query_values = [int(jobID)]
                myresult = db.module().select_all_safe(searchQuery, query_values, True)
                msgpack_file_path = myresult[0]['cRequestBody']

                # fetch the file and bucket names 
                file_name = msgpack_file_path.split('/',1)[1]
                bucket_name = msgpack_file_path.split('/')[0]
                s3_client = AwsS3Service.get_client()

                presigned_url = s3_client.generate_presigned_url('get_object',
                                            Params={'Bucket': bucket_name,
                                                    'Key': file_name},
                                            ExpiresIn=3600)
                # print(presigned_url)
                return RestApiService.encode_response(200, 'JSON', None, {"download_url":str(presigned_url)})
                # return {"statusCode": 200,"headers": RestApiService.headers(), "body": json.dumps({"download_url":str(presigned_url)})}
        # return {"statusCode": 400,"headers": RestApiService.headers(), "body": json.dumps({"message": "Invalid input data"})}
        return RestApiService.encode_response(400, 'JSON', None, {"message": "Invalid input data"})
    except Exception as e:
        print("Error while creating pre signed url")
        print(e)