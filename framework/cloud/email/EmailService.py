import json
from framework.cloud.email.BaseEmailProcessor import BaseEmailProcessor
from framework.cloud.email.BaseEmailClient import BaseEmailClient
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService

class EmailService:


	# send an email to the user given as well as the system config EMAIL_DEST users
	@staticmethod
	def sendTemplatedEmail(templates_dir:str, trigger:str, title:str,
		user_email:str, processor:BaseEmailProcessor, metadata:dict, client:BaseEmailClient, toEmails, ccEmails, bccEmails):


		# on local testing only print message and exit
		if AppConfig.LOCAL_TESTING and not AppConfig.LOCAL_SEND_EMAIL:
			LogService.log(f"Email: Skipped sending email for: {title} ({trigger})")
			return

		

		# log to cloudwatch
		LogService.log(f"Email: Preparing to send email for trigger: {title} ({trigger})")
		
		
		# read the JSON containing the template metadata
		file = open(templates_dir + '/index.json', 'r')
		mailData = file.read()
		mailObj = json.loads(mailData)
		
		
		
		# extract the HTML body from the template
		subject= mailObj['templates'][trigger]['subject']


		template_path = str(mailObj['templates'][trigger]['path']).replace('templates/', '/')
		file = open(templates_dir + template_path, 'r')
		body_lines = file.readlines()
		body = ''.join(body_lines)
		

		# add the props into the template
		body, subject = processor.process(body, mailObj['templates'][trigger], metadata, subject)



		# clone the dest emails since we need to change them
		destEmail = AppConfig.EMAIL_DEST[:]
		
		# honor the destination email ID only if not local testing
		if not AppConfig.LOCAL_TESTING:
			if user_email is not None and len(user_email)>0:
				destEmail.append(user_email.strip())

		if not toEmails:
			toEmails = destEmail

		# send email using given client
		client.send(AppConfig.EMAIL_SOURCE, toEmails, ccEmails, bccEmails, subject, body)

		# send email using given client
		if client.send(AppConfig.EMAIL_SOURCE, toEmails, ccEmails, bccEmails, subject, body):
			# log to cloudwatch only if email was sent
			LogService.log(f"Email: Sent email '{str(subject)}' to {str(destEmail)}")

