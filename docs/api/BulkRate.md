# Bulk Rate API
In this API, records are fetched from write (header) table in bulk and process them.

### Sample Request (JSON)
```json
{
    "type": "OFR",
	"version": "1.0",
	"senderID": "Ency",
	"accessToken": "string",
	"receiverID": "string",
	"requestID": "JOB-MXZ-324",
	"header": {
		"customer": "MDCTEST4",
		"memberSCAC": "SHPT",
		"memberOfficeCode": "SSCL",
		"quotingRegion": "string",
		"originDestination": [
			{
				"originCountry": "US",
				"originLocation": "",
				"destinationCountry": "CN",
				"destinationLocation": ""
			},
			 {
				"originCountry": "",
				"originLocation": "ADALV",
				"destinationCountry": "",
				"destinationLocation": "CNNGB"
			}
		],
		"exclude": [
			{
				"originCountry": "",
				"originLocation": "US",
				"destinationCountry": "",
				"destinationLocation": "IN"
			},
			{
				"originCountry": "",
				"originLocation": "USNYC",
				"destinationCountry": "",
				"destinationLocation": "INAMD"
			}
		],
		"deleteAllRate": false
	},
	"charges": [
		{
			"chargeName": "Origin Documentation",
			"chargeCode": "DOC",
			"aspect": "DEN",
			"currency": "USD",
			"rate": 1171,
			"basis": "W",
			"minimum": 0,
			"maximum": 10,
			"effectiveDate": "2021-01-01",
			"expirationDate": "2021-01-30",
			"scaleUom": "W",
			"from": 104,
			"to": 282,
			"notes": "string",
			"conditional": "C",
			"delete": false,
			"insertIfNotFound": true
		},
		{
			"chargeName": "Origin THC",
			"chargeCode": "THC",
			"aspect": "HAZ",
			"currency": "USD",
			"rate": 1172,
			"basis": "WM",
			"minimum": 9,
			"maximum": 30,
			"effectiveDate": "2021-02-01",
			"expirationDate": "2021-02-28",
			"scaleUom": "M",
			"from": 10,
			"to": 28,
			"notes": "string",
			"conditional": "M",
			"delete": false,
			"insertIfNotFound": true
		}
	]
}
```

### Sample Request (XML)
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<bulkRateRequest>
	<type>OFR</type>
	<version>string</version>
	<senderID>ency</senderID>
	<accessToken>string</accessToken>
	<receiverID>string</receiverID>
	<requestID>JOB-MXZ-324</requestID>
	<header>
		<customer>MDCTEST2</customer>
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
		<deleteAllRate>true</deleteAllRate>
	</header>
	<charges>
		<chargeName>Documentation</chargeName>
		<chargeCode>DOC</chargeCode>
		<aspect>DEN</aspect>
		<currency>USD</currency>
		<rate>1000</rate>
		<basis>CW</basis>
		<minimum>1</minimum>
		<maximum>10</maximum>
		<effectiveDate>2021-11-01</effectiveDate>
		<expirationDate>2021-11-30</expirationDate>
		<scaleUom>M</scaleUom>
		<from>10</from>
		<to>28</to>
		<notes>BulkRateUPDATE</notes>
		<conditional>M</conditional>
		<delete>false</delete>
		<insertIfNotFound>true</insertIfNotFound>
	</charges>
	 <charges>
		<chargeName>Ocean Freight</chargeName>
		<chargeCode>OFR</chargeCode>
		<aspect>DEN</aspect>
		<currency>USD</currency>
		<rate>2000</rate>
		<basis>CW</basis>
		<minimum>1</minimum>
		<maximum>10</maximum>
		<effectiveDate>2021-11-01</effectiveDate>
		<expirationDate>2021-11-30</expirationDate>
		<scaleUom>M</scaleUom>
		<from>10</from>
		<to>28</to>
		<notes>BulkRateUPDATE</notes>
		<conditional>C</conditional>
		<delete>false</delete>
		<insertIfNotFound>true</insertIfNotFound>
	</charges>
	 <charges>
		<chargeName>Container Loading</chargeName>
		<chargeCode>CLD</chargeCode>
		<aspect>DEN</aspect>
		<currency>USD</currency>
		<rate>3000</rate>
		<basis>CW</basis>
		<minimum>1</minimum>
		<maximum>10</maximum>
		<effectiveDate>2021-11-01</effectiveDate>
		<expirationDate>2021-11-30</expirationDate>
		<scaleUom>W</scaleUom>
		<from>10</from>
		<to>28</to>
		<notes>BulkRateUPDATE</notes>
		<conditional>C</conditional>
		<delete>false</delete>
		<insertIfNotFound>true</insertIfNotFound>
	</charges>
</bulkRateRequest>
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