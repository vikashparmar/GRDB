import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from framework.cloud.email.BaseEmailClient import BaseEmailClient
from framework.AppConfig import AppConfig
from framework.formats.objects.Strings import Strings
from framework.system.LogService import LogService


class SMTPEmailClient(BaseEmailClient):

	smtp_client = None
	STARTTLS = False

	def __init__(self, STARTTLS=False):
		SMTPEmailClient.STARTTLS = STARTTLS

	# Returns an SMTP client by creating the client on the first call
	# and reusing the same client for all the other calls
	def smtp_get_client(self):
		# Retry if unable to connect to SMTP
		tries = AppConfig.SMTP_RETRIES
		for attempt in range(1,tries+1):
			if SMTPEmailClient.smtp_client is None:
				try:
					SMTPEmailClient.smtp_client = smtplib.SMTP(AppConfig.SMTP_HOST, AppConfig.SMTP_PORT)

					if SMTPEmailClient.STARTTLS:
						SMTPEmailClient.smtp_client.starttls()

					if Strings.exists(AppConfig.SMTP_USER) and Strings.exists(AppConfig.SMTP_PASS):
						SMTPEmailClient.smtp_client.login(AppConfig.SMTP_USER, AppConfig.SMTP_PASS)

					LogService.log("Email: Successfully created SMTP client")
					return SMTPEmailClient.smtp_client
				except smtplib.SMTPAuthenticationError as e:
					# Do not retry if authentication fails
					LogService.error("Email: Authentication failed. Incorrect SMTP Credentials provided.")
					SMTPEmailClient.smtp_client = None
					return None
				except Exception as e:
					LogService.error(f"Email: Attempt: {attempt}/{tries}: Failed to establish connection with SMTP.", e)
					SMTPEmailClient.smtp_client = None
			else:
				return SMTPEmailClient.smtp_client
		LogService.error(f"Exhausted all {tries} attempts to connect to SMTP.")
		return None
	
	
		
	# send email using smtp client
	def send(self, sourceEmail:str, destEmails:list[str], ccEmails:list[str], bccEmails:list[str], subject:str, body:str):
		try:
			client = self.smtp_get_client()
			
			if client is None:
				raise Exception("Failure in creation of SMTP client")

			try:
				validate_connection = client.noop()
				# Raise error if SMTP client connection expired (SMTP: 250 OK)
				if validate_connection[0] != 250:
					raise smtplib.SMTPServerDisconnected("SMTP connection to server is no longer valid.")
			except smtplib.SMTPServerDisconnected as e:
				# clear the connection and re-establish connection only if connection was lost
				SMTPEmailClient.smtp_client = None
				client = self.smtp_get_client()

			# create the message
			msg = MIMEMultipart()
			msg['From'] = sourceEmail
			msg['To'] = ','.join(destEmails)
			msg['Cc'] = ','.join(ccEmails)
			msg['Bcc'] = ','.join(bccEmails)
			msg['Subject'] = subject
			msg.attach(MIMEText(body, 'html'))
			
			# send the message
			client.sendmail(sourceEmail, destEmails, msg.as_string())
			return True
		except Exception as e:
			LogService.error("Email: SMTP failed to send email. ", e)
			return False