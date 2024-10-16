# Expire Extend API
In this API we fetch records based `oldExpirationDate` and process them 

### Sample Request (JSON)
```json
{
	"type": "OFR",
	"version": "string",
	"senderID": "ency",
	"accessToken": "string",
	"receiverID": "string",
	"requestID": "JOB-MXZ-324",
	"header": {
		"customer": "MDCTEST3",
		"memberSCAC": "SHIPCO",
		"memberOfficeCode": "SSCL",
		"quotingRegion": "string",
		"originDestination": [
			{
				"originCountry": "AD",
				"originLocation": "",
				"destinationCountry": "",
				"destinationLocation": "CNNGB"
			},
			{
				"originCountry": "US",
				"originLocation": "",
				"destinationCountry": "IN",
				"destinationLocation": ""
			}
		],
		"exclude": [
			{
				"originCountry": "",
				"originLocation": "ADALV",
				"destinationCountry": "",
				"destinationLocation": "CNZGA"
			}
		]
	},
	"charges": [
		{
			"chargeName": "Ocean Frieght",
			"chargeCode": "OFR",
			"aspect": "OFR",
			"currency": "US",
			"rate": 200,
			"basis": "CW",
			"minimum": 5,
			"maximum": 10,
			"effectiveDate": "2021-11-10",
			"expirationDate": "2021-12-30",
			"oldExpirationDate": "2021-12-10",
			"scaleUom": "W",
			"from": 1,
			"to": 10,
			"notes": "ExpireCase2",
			"conditional": "M"
		},
		{
			"chargeName": "Documentation",
			"chargeCode": "DOC",
			"aspect": "OFR",
			"currency": "USD",
			"rate": 200,
			"basis": "CW",
			"minimum": 5,
			"maximum": 10,
			"effectiveDate": "2021-11-10",
			"expirationDate": "2021-12-30",
			"oldExpirationDate": "2021-12-10",
			"scaleUom": "W",
			"from": 1,
			"to": 10,
			"notes": "ExpireCase2",
			"conditional": "M"
		}
	]
}
```

### Sample Request (XML)

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<expireExtendRequest>
	<type>OFR</type>
	<version>string</version>
	<senderID>ency</senderID>
	<accessToken>string</accessToken>
	<receiverID>string</receiverID>
	<requestID>JOB-MXZ-324</requestID>
	<header>
		<customer>MDCTEST3</customer>
		<memberSCAC>SHPT</memberSCAC>
		<memberOfficeCode>string</memberOfficeCode>
		<quotingRegion>string</quotingRegion>
		<originDestination>
			<originCountry></originCountry>
			<originLocation>ADALV</originLocation>
			<destinationCountry></destinationCountry>
			<destinationLocation>CNNGB</destinationLocation>
		</originDestination>
		<originDestination>
			<originCountry>AD</originCountry>
			<originLocation></originLocation>
			<destinationCountry></destinationCountry>
			<destinationLocation>CNZGA</destinationLocation>
		</originDestination>
		<exclude>
			<originCountry>US</originCountry>
			<originLocation></originLocation>
			<destinationCountry></destinationCountry>
			<destinationLocation>INAMD</destinationLocation>
		</exclude>
	</header>
	<charges>
		<chargeName>Documentation</chargeName>
		<chargeCode>DOC</chargeCode>
		<aspect>OFR</aspect>
		<currency>USD</currency>
		<rate>200</rate>
		<basis>CW</basis>
		<minimum>10</minimum>
		<maximum>130</maximum>
		<effectiveDate>2021-11-01</effectiveDate>
		<expirationDate>2021-12-10</expirationDate>
		<oldExpirationDate>2021-11-30</oldExpirationDate>
		<scaleUom>W</scaleUom>
		<from>1</from>
		<to>10</to>
		<notes>EXTEND</notes>
		<conditional>M</conditional>
	</charges>
	<charges>
		<chargeName>Ocean Freight</chargeName>
		<chargeCode>OFR</chargeCode>
		<aspect>OFR</aspect>
		<currency>USD</currency>
		<rate>200</rate>
		<basis>CW</basis>
		<minimum>10</minimum>
		<maximum>130</maximum>
		<effectiveDate>2021-11-01</effectiveDate>
		<expirationDate>2021-12-10</expirationDate>
		<oldExpirationDate>2021-11-30</oldExpirationDate>
		<scaleUom>W</scaleUom>
		<from>1</from>
		<to>10</to>
		<notes>EXTEND</notes>
		<conditional>M</conditional>
  	</charges>
</expireExtendRequest>
```

### Sample Correct Response
```json
{
	"success": true,
	"schemaValid": true,
	"jobID": 13
}
```

### Sample Error Response
```json
{
	"success": true,
	"schemaValid": false,
	"schemaErrors": [
		{
			"charge": "envelope",
			"code": 400,
			"message": "User(senderID) not validated"
		}
	]
}
```