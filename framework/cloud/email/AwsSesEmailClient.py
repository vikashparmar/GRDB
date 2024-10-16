import boto3
from framework.cloud.email.BaseEmailClient import BaseEmailClient
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService


class AwsSesEmailClient(BaseEmailClient):

	boto3_ses_client = None

	
	# Returns an SES client by creating the client on the first call
	# and reusing the same client for all the other calls
	def ses_get_client(self):
		if AwsSesEmailClient.boto3_ses_client is None:
			try:
				AwsSesEmailClient.boto3_ses_client = boto3.client('ses',
					region_name=AppConfig.AWS_REGION,
					aws_access_key_id=AppConfig.AWS_KEY1,
					aws_secret_access_key=AppConfig.AWS_KEY2)
			except Exception as e:
				LogService.error("Email: Cannot connect to SES", e)
				return False
			LogService.log("Email: Successfully created SES client")
		return AwsSesEmailClient.boto3_ses_client
		

	
	# send an email
	def send(self, sourceEmail:str, destEmails:list[str], ccEmails:list[str], bccEmails:list[str], subject:str, body:str):

		try:
			# send email using AWS SES
			ses = self.ses_get_client()
			ses.send_email(
				Source = sourceEmail,
				Destination = {'ToAddresses' : destEmails,
								'CcAddresses': ccEmails,
								'BccAddresses': bccEmails},
				Message = {
					'Subject': {
						'Data': subject,
						'Charset': 'UTF-8'
					},
					'Body': {
						'Html': {
							'Data': body,
							'Charset':'UTF-8'
						}
					}
				}
			)
			return True
		except Exception as e:
			LogService.error("Email: SES failed to send email. ", e)
			return False
