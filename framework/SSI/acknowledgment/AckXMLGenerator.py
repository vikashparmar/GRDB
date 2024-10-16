from xml.etree.ElementTree import fromstring
from xml.etree import ElementTree
from framework.SSI.job.AppJob import AppJob

class AckXMLGenerator:
	
	@staticmethod
	def generate(job:AppJob):
		xml = """<?xml version="1.0" encoding="UTF-8"?>

		<Acknowledgement xmlns:xsi="http://www.w3.org/2001/XMLSchemainstance" xsi:noNamespaceSchemaLocation="http://www.wwalliance.com/wiki/images/f/fc/Acknowledgement_version_1.0.0.xsd">
			<AcknowledgementEnvelope>
				<SenderID>wwalliance</SenderID>
				<ReceiverID></ReceiverID>
				<Password>test</Password>
				<Type>Acknowledgement_XML</Type>
				<Version>1.0</Version>
				<EnvelopeID></EnvelopeID>
			</AcknowledgementEnvelope>
			<AcknowledgementDetails>
				<CustomerReference></CustomerReference>
				<WWAReference></WWAReference>
				<AcknowledgementType>SSI</AcknowledgementType>
				<ReferenceNumber></ReferenceNumber>
				<BookingNumber></BookingNumber>
				<AcknowledgementStatus>A</AcknowledgementStatus>
				<Remarks>Accepted</Remarks>
			</AcknowledgementDetails>
		</Acknowledgement>"""

		ack_xml = fromstring(xml)

		ack_xml.find('./AcknowledgementEnvelope/ReceiverID').text = job.cSender
		ack_xml.find('./AcknowledgementDetails/WWAReference').text = job.statuses[0].cWWAShipmentReference
		ack_xml.find('./AcknowledgementDetails/BookingNumber').text = job.statuses[0].cBookingnumber
		# ack_xml.find('./AcknowledgementEnvelope/ReceiverID').text = sender
		# ack_xml.find('./AcknowledgementEnvelope/ReceiverID').text = sender

		data = ElementTree.tostring(ack_xml, encoding='utf8', method='xml')
		return data