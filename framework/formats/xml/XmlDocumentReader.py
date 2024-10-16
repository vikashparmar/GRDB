import xml.etree.ElementTree as ET

class XmlDocumentReader:

	def __init__(self, xml) -> None:
		if type(xml) == str or type(xml) == bytes:
			self.root = ET.fromstring(xml)
		else:
			self.root = xml
	
	def getXmlTagValue(self, xpath):
		elem = self.root.find(xpath)
		val=elem.text if elem!=None else None
		return val 
	
	def getXmlTags(self, xpath):
		return self.root.findall(xpath)
	
	def searchXmlTagNested(self, tag):
		for elem in self.root.iter(tag):
			if elem.text:
				return elem.text
		return None
	