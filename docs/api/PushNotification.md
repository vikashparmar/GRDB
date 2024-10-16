# Push Notifications
Push notifications will be sent from GRDB to the Client Server to notify client about job status:

### Sample Push Notification (JSON)
Notes:
- `status` and `statusCode` is as per Appendix B
- `errors.code` and `warnings.code` is as per Appendix A
- `active` will be true if the job is in progress, false if COMPLETED/ERROR
- `metricType` can be "JOB" / "VALIDATION" / "INSERTION" / "WAIT"
```json
{ 
	"jobID": 23, 
	"requestID": "JOB-MXZ-324", 
	"status": "CREATED",
	"statusCode": 1, 	
	"active": true,
	"appVersion": "1.0.7", 
	"metricType": "VALIDATION",
	"metrics": { 
		"start": "YYYY-MM-DD HH:MM:SS:MS", 
		"end": "YYYY-MM-DD HH:MM:SS:MS", 
		"duration": 25.123, 
	},
	"errors":[ 
		{ 
			"charge":4, 
			"code":123,
			"message":"The iRate field is missing." 
		}, 
		{...}, 
		{...}, 
		{...}, 
	], 
	"warnings":[ 
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