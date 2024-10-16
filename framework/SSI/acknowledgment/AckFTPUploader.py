from framework.SSI.acknowledgment.AckXMLGenerator import AckXMLGenerator
from framework.formats.zip.ZipEncoder import ZipEncoder
from framework.cloud.storage.FtpClient import FtpClient
from framework.system.LogService import LogService
from framework.SSI.job.AppJob import AppJob

class AckFTPUploader:

	# Save correct log to ZIP file and upload on FTP
	@staticmethod
	def upload(job:AppJob):

		# generate the xml
		xml = AckXMLGenerator.generate(job)

		# connect to FTP and upload
		if job.member_allowed_ftp and job.member_FTP_host is not None:

			upload_data = xml

			FtpClient.upload_file_V2(upload_data, job.systemuser_name, job.result_correctlog_filename,
				job.member_FTP_ack_folder, job.member_FTP_host, job.member_FTP_port, job.member_FTP_user, job.member_FTP_pass)
		else:
			LogService.log(f"Log: Skipped uploading acknowledgment to FTP server due to unauthorized username '{job.cSender}'")
			LogService.print(f"Log: Skipped uploading acknowledgment to FTP server due to unauthorized username '{job.cSender}'")