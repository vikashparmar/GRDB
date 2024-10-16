# import the 'framework' package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
from framework.grdb.apiValidation.rules.BulkRateRule import BulkRateRule
from framework.grdb.api.RateApiHandler import RateApiHandler
from framework.grdb.enums.RateApiType import RateApiType

class PushRate():
	def __init__(self):
		 pass

def main(event, context):

	# handle this rate insertion API request and return a valid JSON/XML response
	return RateApiHandler.handle(event, "bulkRateRequest", "bulkRateResponse", RateApiType.BulkRate, BulkRateRule())
	