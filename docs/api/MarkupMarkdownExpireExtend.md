## Mark Up Mark Down Expire Extend API
In this API we have to do the both combined what we do in MarkUpMarkDown API and ExpireExtend API.

### Sample Request (JSON)
```json
{
	"type":"OFR" ,
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
				"destinationCountry": "CN",
				"destinationLocation":""
			},
			{
				"originCountry": "US",
				"originLocation": "",
				"destinationCountry": "",
				"destinationLocation":"INAMD"
			}
		],
	  	"exclude": [
			{
				"originCountry": "AD",
				"originLocation": "",
				"destinationCountry": "",
				"destinationLocation":"CNZGA"
			}
		  ]
	},
	"charges": [
		{
			"chargeName": "Documentation",
			"chargeCode": "DOC",
			"aspect": "OFR",
			"currency": "USD",
			"markupType": "Percent",
			"rate": -50,
			"basis": "CW",
			"minimum": -50,
			"maximum": -50,
			"oldExpirationDate": "2021-11-30",
			"effectiveDate": "2021-11-01",
			"expirationDate": "2021-12-25",
			"scaleUom": "W",
			"from": 1,
			"to": 10,
			"notes": "markDownPercent&expire",
			"conditional": "M"    
		},
		{
			"chargeName": "Ocean Freight",
			"chargeCode": "OFR",
			"aspect": "OFR",
			"currency": "U$D",
			"markupType": "Percent",
			"rate": -50 ,
			"basis": "CW",
			"minimum": -50,
			"maximum": -50,
			"oldExpirationDate": "2021-11-30",
			"effectiveDate": "2021-11-01",
			"expirationDate": "2021-12-25",
			"scaleUom": "W",
			"from": 1,
			"to": 10,
			"notes": "markDownPercent&expire",
			"conditional": "M"    
		}
	]
}
```

### Sample Request (XML)
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<markupMarkdownExpireExtendRequest>
	<type>OFR</type>
	<version>string</version>
	<senderID>ency</senderID>
	<accessToken>string</accessToken>
	<receiverID>string</receiverID>
	<requestID>JOB-MXZ-324</requestID>
	<header>
		<customer>MDCTEST2</customer>
		<memberSCAC>SHPT</memberSCAC>
		<memberOfficeCode>SSCL</memberOfficeCode>
		<quotingRegion>string</quotingRegion>
		<originDestination>
			<originCountry>AD</originCountry>
			<originLocation></originLocation>
			<destinationCountry></destinationCountry>
			<destinationLocation>CNNGB</destinationLocation>
		</originDestination>
		<originDestination>
			<originCountry>US</originCountry>
			<originLocation></originLocation>
			<destinationCountry></destinationCountry>
			<destinationLocation>INAMD</destinationLocation>
		</originDestination>
		<exclude>
			<originCountry>AD</originCountry>
			<originLocation></originLocation>
			<destinationCountry></destinationCountry>
			<destinationLocation>CNZGA</destinationLocation>
		</exclude>
	</header>
	<charges>
		<chargeName>Documentation</chargeName>
		<chargeCode>DOC</chargeCode>
		<aspect>OFR</aspect>
		<currency>USD</currency>
		<markupType>Flat</markupType>
		<rate>100</rate>
		<basis>CW</basis>
		<minimum>100</minimum>
		<maximum>100</maximum>
		<oldExpirationDate>2021-11-30</oldExpirationDate>
		<effectiveDate>2021-11-01</effectiveDate>
		<expirationDate>2021-12-10</expirationDate>
		<scaleUom>W</scaleUom>
		<from>1</from>
		<to>10</to>
		<notes>string</notes>
		<conditional>M</conditional>
	</charges>
   <charges>
		<chargeName>Ocean Freight</chargeName>
		<chargeCode>OFR</chargeCode>
		<aspect>OFR</aspect>
		<currency>USD</currency>
		<markupType>Percent</markupType>
		<rate>-50</rate>
		<basis>CW</basis>
		<minimum>-50</minimum>
		<maximum>-50</maximum>
		<oldExpirationDate>2021-11-30</oldExpirationDate>
		<effectiveDate>2021-11-01</effectiveDate>
		<expirationDate>2021-12-10</expirationDate>
		<scaleUom>W</scaleUom>
		<from>1</from>
		<to>10</to>
		<notes>string</notes>
		<conditional>M</conditional>
	</charges>
</markupMarkdownExpireExtendRequest>
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