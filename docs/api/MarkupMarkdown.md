# Mark Up Mark Down API
In this API we update rates, minimum, maximum based on the value of `markupType`.

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
		"memberSCAC": "SHPT",
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
				"originCountry": "",
				"originLocation": "USNYE",
				"destinationCountry": "",
				"destinationLocation":"INAMD"
			}
		],
		"exclude": [
			{
				"originCountry": "",
				"originLocation": "ADALV",
				"destinationCountry": "",
				"destinationLocation":"CNZGA"
			}
		]
	},
	"charges": [
		{
		"chargeName": "Ocean Frieght",
		"chargeCode": "OFR",
		"aspect": "OFR",
		"currency": "US",
		"markupType": "Flat",
		"rate": 200,
		"basis": "CW",
		"minimum": -50,
		"maximum": -50,
		"effectiveDate": "2021-11-25",
		"expirationDate": "2021-11-30",
		"scaleUom": "W",
		"from": 1,
		"to": 10,
		"notes": "markDownPercent50",
		"conditional": "M"    
		},
		{
		"chargeName": "Documentation",
		"chargeCode": "DOC",
		"aspect": "OFR",
		"currency": "U$D",
		"markupType": "Percent",
		"rate": -50,
		"basis": "CW",
		"minimum":-50,
		"maximum": -50,
		"effectiveDate": "2021-11-25",
		"expirationDate": "2021-11-30",
		"scaleUom": "W" ,
		"from": 1,
		"to": 10,
		"notes": "markDownPercent50",
		"conditional": "M"     
		}   
	]
}
```

### Sample Request (XML)
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<markupMarkdownRequest>
	<type>OFR</type>
	<version>string</version>
	<senderID>ency</senderID>
	<accessToken>string</accessToken>
	<receiverID>string</receiverID>
	<requestID>JOB-MXZ-324</requestID>
	<header>
		<customer>MDCTEST3</customer>
		<memberSCAC>SHIPCO</memberSCAC>
		<memberOfficeCode>SSCL</memberOfficeCode>
		<quotingRegion>string</quotingRegion>
		<originDestination>
			<originCountry></originCountry>
			<originLocation>ADALV</originLocation>
			<destinationCountry></destinationCountry>
			<destinationLocation>CNNGB</destinationLocation>
		</originDestination>
		<originDestination>
			<originCountry></originCountry>
			<originLocation>USNYC</originLocation>
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
		<effectiveDate>2021-11-01</effectiveDate>
		<expirationDate>2021-11-30</expirationDate>
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
		<effectiveDate>2021-11-01</effectiveDate>
		<expirationDate>2021-11-30</expirationDate>
		<scaleUom>W</scaleUom>
		<from>1</from>
		<to>10</to>
		<notes>string</notes>
		<conditional>M</conditional>
	</charges>
</markupMarkdownRequest>
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