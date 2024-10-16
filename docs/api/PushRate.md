# Push Rate API

Endpoint: https://SITE.amazonaws.com/ENV/rates/pushRate

Push Rate API allows for rate insertion and job status tracking for the same using polling or interrupt-driven events.

Tracking:
- Client server can call the `pollJobStatus` API method at any time to poll the status of a specific job
- GRDB supports push notifications by calling third-party client REST API server, so that client can obtain interrupt-driven job status notifications 
- Client API server can implement the Push notifications API method according to our specifications, so that they can receive push notifications about live job status 

![workflow](/.github/images/push_rate_workflow.png)

### Sample Request (JSON)

Notes:
- `type` can be "PLC" / "FOB" / "OFR"
- `charges.scaleUom` can be "W" / "M"
```json
{ 
	"type": "FOB", 
	"version": "1.0", 
	"senderID": "string", 
	"accessToken": "string", 
	"receiverID": "string", 
	"requestID": "JOB-MXZ-324",
	"header": { 
		"customer": "string", 
		"memberSCAC": "AB", 
		"memberOfficeCode": "string", 
		"originRegion": "string", 
		"originInlandCFS": "ABCD", 
		"originConsolCFS": "AB", 
		"portOfLoading": "AB", 
		"transhipment1": "ABCD", 
		"transhipment2": "AB", 
		"transhipment3": "A", 
		"destinationRegion": "string", 
		"portOfDischarge": "AB", 
		"destinationConsolCFS": "ABC", 
		"destinationInlandCFS": "ABC", 
		"quotingRegion": "string", 
		"deleteAllRate": false 
	}, 
	"charges": [ 
		{ 
			"chargeName": "string", 
			"chargeCode": "string", 
			"aspect": "string", 
			"currency": "USD", 
			"rate": 11716500000000.2, 
			"basis": "string", 
			"minimum": -31641799999999.8, 
			"maximum": -41910699999999.8, 
			"effectiveDate": "YYYY-MM-DD", 
			"expirationDate": "YYYY-MM-DD", 
			"scaleUom": "W", 
			"from": 10409300000000.2, 
			"to": 28200000000000.2, 
			"notes": "string", 
			"delete": false, 
			"mandatory": false
		}, 
		{...}, 
		{...}, 
		{...}, 
	] 
}
```
### Sample Request (XML)
```xml
<?xml version="1.0" encoding="UTF-8"?> 
<pushRateRequest> 
	<type>PLC</type> 
	<version>1.0</version> 
	<senderID>oganbhoj</senderID> 
	<accessToken>string</accessToken> 
	<receiverID>string</receiverID> 
	<requestID>JOB-MXZ-324</requestID> 
	<header> 
		<customer>string</customer> 
		<memberSCAC>AB</memberSCAC> 
		<memberOfficeCode>string</memberOfficeCode> 
		<originRegion>string</originRegion> 
		<originInlandCFS>ABCD</originInlandCFS> 
		<originConsolCFS>AB</originConsolCFS> 
		<portOfLoading>AB</portOfLoading> 
		<transhipment1>ABCD</transhipment1> 
		<transhipment2>AB</transhipment2> 
		<destinationRegion>string</destinationRegion> 
		<portOfDischarge>AB</portOfDischarge> 
		<destinationConsolCFS>ABC</destinationConsolCFS> 
		<destinationInlandCFS>ABC</destinationInlandCFS> 
		<quotingRegion>string</quotingRegion> 
		<deleteAllRate>false</deleteAllRate> 
	</header> 
	<charges> 
			<chargeName>string</chargeName> 
			<chargeCode>string</chargeCode> 
			<aspect>string</aspect> 
			<currency>USD</currency> 
			<rate>11716500000000.2</rate> 
			<basis>string</basis> 
			<minimum>-31641799999999.8</minimum> 
			<maximum>-41910699999999.8</maximum> 
			<effectiveDate>YYYY-MM-DD</effectiveDate> 
			<expirationDate>YYYY-MM-DD</expirationDate> 
			<scaleUom>W</scaleUom> 
			<from>10409300000000.2</from> 
			<to>28200000000000.2</to> 
			<notes>string</notes> 
			<delete>false</delete> 
			<mandatory>false</mandatory> 
	</charges> 
	<charges>
			<chargeName>string</chargeName> 
			<chargeCode>string</chargeCode> 
			<aspect>string</aspect> 
			<currency>USD</currency> 
			<rate>11716500000000.2</rate> 
			<basis>string</basis> 
			<minimum>-31641799999999.8</minimum> 
			<maximum>-41910699999999.8</maximum> 
			<effectiveDate>YYYY-MM-DD</effectiveDate> 
			<expirationDate>YYYY-MM-DD</expirationDate> 
			<scaleUom>W</scaleUom> 
			<from>10409300000000.2</from> 
			<to>28200000000000.2</to> 
			<notes>string</notes> 
			<delete>false</delete> 
			<mandatory>false</mandatory> 
	</charges> 
</pushRateRequest> 
```
### Valid Schema Response 
```json
{ 
	"success": true, 
	"schemaValid": true, 
	"jobID": 23, 
}
```
### Invalid Schema Response
Notes:
- `schemaErrors.code` is as per Appendix A
```json
{ 
	"success": true, 
	"schemaValid": false, 
	"schemaErrors":[ 
		{ 
			"charge":4, 
			"code":123,
			"message":"The iRate field is missing." 
		}, 
		{...}, 
		{...}, 
		{...}, 
	] 
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