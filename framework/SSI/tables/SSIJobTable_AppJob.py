from framework.SSI.core.AppDatabase import AppDatabase
from framework.SSI.tables.GenUserTable import GenUserTable
from framework.system.LogService import LogService

#------------------------------------------------------------------------------------
# 							ONLY USE WITHIN KUBERNETES!

# IMPORTANT! This file CANNOT add dependency to AppJob since it is used within AppJob
# and that would cause a circular dependency which Python crashes with.
# Therefore it uses AppJob properties but we cannot use static typing.
#------------------------------------------------------------------------------------

class SSIJobTable_AppJob:
	
	# load the job's user details from gen_User table based on the current job ID
	# Returns true if job exists, false if job with given ID could not be found.
	@staticmethod
	def loadJobMetadata(job):
		
		if job.iJobID is not None:

			# get user name and other details of the current job
			get_user_details_query = "SELECT cStatus, iStatus FROM wei_Jobs WHERE iJobID = %s"
			qyery_values = [str(job.iJobID)]
			metadata = job.db.module().select_all_safe(get_user_details_query, qyery_values)
			if len(metadata)>0:
				
				# get job details of the user
				job.job_status = metadata[0][2]
				
				# check if a job is inactive or not
				if int(metadata[0][3]) < 0:
					job.job_is_active = False
				
					programID = 0 # TODO

					ftp_ok, member_id = GenUserTable.isUserAllowedFtpUpload(job.db, programID, job.user_id)
					job.member_id = member_id

					# get FTP upload details
					if ftp_ok:
						HOST, PORT, USERNAME, PASS, ACKPATH = GenUserTable.getMemberFtpDetails(job.db, programID, job.member_id)
						if HOST is None:
							LogService.log(f"Job: WARNING: Cannot find any FTP settings in gen_Configuration for member ID {str(member_id)}")
						else:
							job.member_FTP_host = HOST
							job.member_FTP_port = PORT
							job.member_FTP_user = USERNAME
							job.member_FTP_pass = PASS
							job.member_FTP_ack_folder = ACKPATH


				else:
					LogService.log(f"Job: WARNING: Cannot find any user in gen_User with the cUsername of {str(job.user_name)}")

				# at least job data loaded correctly
				return True
			else:
				LogService.log(f"Job: ERROR: Cannot find any job with the ID of {str(job.iJobID)}")
				
		return False
