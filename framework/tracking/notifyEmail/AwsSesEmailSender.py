from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from framework.cloud.email.AwsSesEmailClient import AwsSesEmailClient
from framework.AppConfig import AppConfig
import jinja2, json

class AwsSesEmailSender:

	SSITemplate:str = None

	def init():
		if AwsSesEmailSender.SSITemplate is None:
			templateLoader = jinja2.FileSystemLoader(searchpath="./")
			templateEnv = jinja2.Environment(loader=templateLoader)
			AwsSesEmailSender.SSITemplate = templateEnv.get_template(AppConfig.EMAIL_SSI_TEMPLATE_PATH)


	@staticmethod
	def send(From, To, Subject, failed_validations, db, params):

		AwsSesEmailSender.init()

		result = db.master().select_all_safe("SELECT DATE_FORMAT(NOW(),'%M %e, %Y') as Currentdate,DATE_FORMAT(NOW(),'%Y') as Year,cHeader, cFooter FROM gen_Template WHERE cTitle = 'wwaonline_main' and iStatus>= 0;", None)[0]
		RESERVEDtopicTextTop = f"""Dear {params['cCompanyname']},<br><br>

					Please note the file {params['filename']} with status code {params['status_code']} for CustomerAlias '{params['customer_alias']}' has failed without being processed as the data provided for fields below is not as per WWA standards : <br><br>"""
		RESERVEDtopicTextBottom = """Please refer the below link for shipment status validation rules that need to be followed with respect to WWA.<br>   <br>
										
					http://www.wwalliance.com/wiki/index.php/Shipment_Status_Validation_Rules<br><br>
					
					Regards, <br><br>
					
					World Wide Alliance,<br><br>"""
		TemplateData = { 
			"RESERVEDfullDate" : result[0], 
			"RESERVEDyear" : result[1], 
			"RESERVEDtopicTextTop" : RESERVEDtopicTextTop, 
			"RESERVEDtopicTextBottom" : RESERVEDtopicTextBottom,
			"webHost" : "awsstaging.www.wwaalliance.com/", 
			"ShipmentStatusErrorRow" : []
		}
		# client = boto3.client('ses', region_name=config['AWS']['REGION'], aws_access_key_id = config['AWS']['ACCESS_KEY'], aws_secret_access_key = config['AWS']['SECRET_ACCESS_KEY'])

		# if params['status_type'] == 'e':
		#	 Reference = "Booking Number"
		#	 Value = params['booking_number']
		# elif params['status_type'] == 'i':
		#	 Reference = "Arrival Notice Number"
		#	 Value = params['arrival_notice_number']

		index = 1
		for failed_validation in failed_validations:
			Reference = "Booking Number" if failed_validation['status_type'] == 'e' else "Arrival Notice Number"
			Value = failed_validation['booking_number'] if failed_validation['status_type'] == 'e' else failed_validation['arrival_notice_number']
			for error in failed_validation['errors']:
				TemplateData['ShipmentStatusErrorRow'].append({ "SrNo" : index, "Reference" : Reference , "Value" : Value, "Errordetails" : f"{error}" })
				index = index + 1
		
		# create ses client
		ses = AwsSesEmailClient()
		client = ses.ses_get_client()

		# un comment below lines when you have access to AWS SES Service to send emails
		# response = client.send_templated_email(
		#	 Source=From,
		#	 Destination={
		#		 'ToAddresses': To,
		#		 'CcAddresses': []
		#	 },
		#	 Template=AppConfig.EMAIL_TEMPLATE_NAME,
		#	 TemplateData=str(json.dumps(TemplateData))
		# )

		# print(f"Email Sent to {To}")
	@staticmethod
	def sendWithAttachment(From, To, Subject, errors, db, params):

		AwsSesEmailSender.init()

		result = db.master().select_all_safe("SELECT DATE_FORMAT(NOW(),'%M %e, %Y') as Currentdate,DATE_FORMAT(NOW(),'%Y') as Year,cHeader, cFooter FROM gen_Template WHERE cTitle = 'wwaonline_main' and iStatus>= 0;", None)[0]

		TemplateData = { 
			"RESERVEDfullDate" : result[0], 
			"RESERVEDyear" : result[1], 
			"webHost" : "awsstaging.www.wwaalliance.com/", 
			"ShipmentStatusErrorRow" : []
		}
		body_errors = ''
		if params['status_type'] == 'e':
			Reference = "Booking Number"
			Value = params['booking_number']
		elif params['status_type'] == 'i':
			Reference = "Arrival Notice Number"
			Value = params['arrival_notice_number']
		for index, error in enumerate(errors):
			TemplateData['ShipmentStatusErrorRow'].append({ "SrNo" : index+1, "Reference" : Reference, "Value" : Value, "Errordetails" : f"{error}" })
			body_errors += f'- {error}\n'

		Body=f"""
	Dear {params['cCompanyname']},

	Attached you will find a report of shipment status import validation errors for filename {params['filename']} with status code {params['status_code']} for CustomerAlias '{params['customer_alias']}'.

	Please note the file has failed without being processed as the data provided for fields below is not as per WWA standards : 
	{body_errors}

	Please refer the below link for shipment status validation rules that need to be followed with respect to WWA.   


	https://www.wwalliance.com/wiki/index.php/Shipment_Status_Validation_Rules

	Regards, 

	World Wide Alliance,
		"""

		msg = MIMEMultipart()
		msg["Subject"] = f"Test email from pnqeibetab.wwalliance.com : Shipment Status Import Validation Errors file {params['filename']}"
		msg["From"] = From
		msg["To"] = ','.join(To)

		# Set message body
		body = MIMEText(Body, "plain")
		msg.attach(body)

		# filename = "shipmentimportvalidationerrors.html"

		# with open(filename, "rb") as attachment:
		part = MIMEApplication(template.render(TemplateData=TemplateData))
		part.add_header("Content-Disposition",
						"attachment",
						filename="shipmentimportvalidationerrors.html")
		msg.attach(part)

		ses = AwsSesEmailClient()
		client = ses.ses_get_client()
		# un comment below lines when you have access to AWS SES Service to send emails
		# response = client.send_raw_email(
		#	 Source=From,
		#	 Destinations=To,
		#	 RawMessage={"Data": msg.as_string()}
		# )
		# print(f"Email Sent to {To}")
