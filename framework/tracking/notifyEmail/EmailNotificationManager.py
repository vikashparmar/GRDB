from framework.tracking.notifyEmail.AwsSesEmailSender import AwsSesEmailSender
from framework.SSI.core.AppDatabase import AppDatabase
from framework.SSI.job.AppJob import AppJob
from framework.SSI.tables.SSIJobTable import SSIJobTable

class EmailNotificationManager:

	@staticmethod
	def send(db:AppDatabase, job:AppJob):
		# Update the job table with the current status and the error message
		# self.job.CurrentStatus = 'VALIDATION FAILED'
		# self.job.ErrorMessage = str(job.failed_validations)
		# self.job.update()
		SSIJobTable.set_status_validation_error(db, str(job.failed_validations))

		#Get the email ID and name of the Customer/Member and see if they are subscribed or not
		result = db.master().select_all_safe('SELECT sei_Member.cCompanyname, sei_Member_setting.cValue FROM sei_Member INNER JOIN sei_Member_setting ON sei_Member.iMemberID = sei_Member_setting.iMemberID WHERE sei_Member_setting.iProgramID=(select iProgramID from gen_Program where cCode=%s) AND sei_Member_setting.cCode = %s AND sei_Member.cCompanycode = %s;', ('SSI', 'cAdditionalMail', job.cSender,))

		# If the customer/Member is subscribed the prepare the email body and send the email
		if result.__len__() > 0:
			params = {
				"filename" : job.cFileName,
				"status_code" : job.xmlDocument.getXmlTags('./ShipmentStatusDetails/StatusCode'),
				"customer_alias" : job.failed_validations[0]['customer_alias'],
				"cCompanyname" : result[0][0],
				"booking_number" : job.failed_validations[0]['booking_number'],
				"arrival_notice_number" : job.failed_validations[0]['arrival_notice_number'],
				"status_type" : 'e'
			}
			
			print("Sending emails...")
			# print('vikash.parmar@encycg.com', ['pathfinderemailservice@gmail.com'], '', job.failed_validations[0]['errors'], db, params)
			# For file with attachment multi booking error email is not applied because of the email body
			AwsSesEmailSender.sendWithAttachment('vikash.parmar@encycg.com', ['pathfinderemailservice@gmail.com'], '', job.failed_validations[0]['errors'], db, params)
			AwsSesEmailSender.send('vikash.parmar@encycg.com', ['pathfinderemailservice@gmail.com'], '', job.failed_validations,db, params)

		# Delete the message from Validation queue
		# try:
		#	 job.sqs_message.delete()
		# except:
		#	 print("Couldn't delete message from validation queue")
	