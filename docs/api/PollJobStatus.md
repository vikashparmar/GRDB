# Polling API
To get live job status

Endpoint: https://SITE.amazonaws.com/ENV/rates/pollJobStatus

### Sample Request (JSON)
```json
{ 
	"senderID": "string", 
	"accessToken": "string", 
	"receiverID": "string", 
	
	"jobID": 23, 
		OR 
	"requestID": 23, 
	
	"getRowCounts": true, 
	"getTimestamps": true, 
	"getDurations": true, 
	"getErrors": true, 
	"getWarnings": true, 
}
```
### Normal Response 
Notes:
- `status` and `statusCode` is as per Appendix B
- `errors.code` and `warnings.code` is as per Appendix A
- `active` will be true if the job is in progress, false if COMPLETED/ERROR
```json
{ 
	"success": true, 
	"jobID": 23, 
	"requestID": "JOB-MXZ-324", 
	"status": "CREATED",
	"statusCode": 1, 	
	"active": true,
	"appVersion": "1.0.7", 
	"rowCounts":{ 
		"total": 200, 
		"error": 15, 
		"validated": 150 
	}, 
	"timestamps": { 
		"jobStart": "YYYY-MM-DD HH:MM: SS:MS", 
		"jobEnd": "YYYY-MM-DD HH:MM: SS:MS", 
		"validationStart": "YYYY-MM-DD HH:MM: SS:MS", 
		"validationEnd": "YYYY-MM-DD HH:MM: SS:MS", 
		"insertionStart": "YYYY-MM-DD HH:MM: SS:MS", 
		"insertionEnd": "YYYY-MM-DD HH:MM: SS:MS", 
		"waitStart": "YYYY-MM-DD HH:MM: SS:MS", 
		"waitEnd": "YYYY-MM-DD HH:MM: SS:MS", 
	}, 
	"durations": { 
		"job": 25.234, 
		"validation": 12.123, 
		"insertion": 12.234, 
		"wait": 0.0, 
	}, 
	"errors": [ 
		{ 
			"charge":4, 
			"code":123,
			"message":"The iRate field is missing." 
		}, 
		{...}, 
		{...}, 
		{...}, 
	], 
	"warnings": [ 
		{ 
			"charge":4, 
			"code":123,
			"message":"The iMinimum field is blank." 
		}, 
		{...}, 
		{...}, 
		{...}, 
	], 
} 
```
### Internal Error Response 
```json
{ 
	"success": false, 
	"errorCode": 123, 
	"errorMessage": "Failure loading system tables" 
} 
```

### Updated Response

```json
{
    "success": true,
    "jobID": 3,
    "status": "COMPLETED",
    "statusCode": 6,
    "active": false,
    "appVersion": "1.8.1",
    "durations": {
        "job": 0.0,
        "validation": 0.0,
        "insertion": 0.0,
        "wait": 0.0
    },
    "errors": [
        {
            "section": "charge",
            "field": "",
            "charge": 1,
            "chargeCode": "FMG",
            "message": "Currency Conversion Rate from (INR) to (USD) is less than zero or not available in system for (Fumigation). ",
            "code": 3043
        },
        {
            "section": "charge",
            "field": "",
            "charge": 2,
            "chargeCode": "EDI",
            "message": "Currency Conversion Rate from (KHR) to (USD) is less than zero or not available in system for (EDI Fee). ",
            "code": 3043
        },
        {
            "section": "charge",
            "field": "",
            "charge": 1,
            "chargeCode": "FMG",
            "message": "Currency Conversion Rate from (INR) to (USD) is less than zero or not available in system for (Fumigation). ",
            "code": 3043
        },
        {
            "section": "charge",
            "field": "",
            "charge": 2,
            "chargeCode": "EDI",
            "message": "Currency Conversion Rate from (KHR) to (USD) is less than zero or not available in system for (EDI Fee). ",
            "code": 3043
        },
        {
            "section": "charge",
            "field": "",
            "charge": 1,
            "chargeCode": "FMG",
            "message": "Currency Conversion Rate from (INR) to (USD) is less than zero or not available in system for (Fumigation). ",
            "code": 3043
        },
        {
            "section": "charge",
            "field": "",
            "charge": 2,
            "chargeCode": "EDI",
            "message": "Currency Conversion Rate from (KHR) to (USD) is less than zero or not available in system for (EDI Fee). ",
            "code": 3043
        }
    ],
    "warnings": []
}
```