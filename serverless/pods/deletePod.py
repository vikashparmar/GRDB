# import the 'framework' package
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
from framework.grdb.infra.PodTable import PodTable
from framework.grdb.auth.AuthToken import AuthToken
from framework.system.RestApiService import RestApiService
from framework.grdb.api.ApiDatabase import ApiDatabase

def main(event, context):
    try:
        # connect to DB or exit with REST API error if unable to connect
        db, err = ApiDatabase.connect()

        if err is not None:
            return err

        # AUTHENTICATING THE ACCESS TOKEN RECEIVED IN HEADERS FROM THE CLIENT SIDE APP
        token_valid = AuthToken.validate(db, event)
        if token_valid[0] == False:
            print(
                "IT Dashboard --- INVALID ACCESS TOKEN. USER NOT AUTHORIZED. RETURNING 401.")
            return RestApiService.encode_response(401, 'JSON', None, 
                    json.dumps({"message": "User is not authorized to access this information."}))

        queryParams = event['queryStringParameters']
        print(queryParams)
        cPodName = queryParams['cPodName']
        # query = 'UPDATE grdb_Pod SET cAction="{"delete":"Y"}" where cPodName="{}"'.format(cPodName)

        myresult = PodTable.markPodForDeletion(db, cPodName)
        print(myresult)

        return RestApiService.encode_response(200, 'JSON', None, json.dumps({"data": str(myresult)}))


    except Exception as e:
        print("EXCEPTION IN IT DASHBOARD API")
        print(e)
        return RestApiService.encode_response(500, 'JSON', None, 
                json.dumps({"message": "Facing some issues fetching your information. Please refresh or retry later.", "status": 500}))
