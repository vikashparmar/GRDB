# import the 'framework' package
from errno import E2BIG
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import libraries
import json
import time
from datetime import datetime
from framework.grdb.core.AppJob import AppJob
from framework.grdb.core.tables.JobTable_SQS import JobTable_SQS
from framework.grdb.core.AppGlobal import AppGlobal
from framework.grdb.enums.JobOldStatus import JobOldStatus
from framework.grdb.enums.JobStatus import JobStatus
from framework.grdb.enums.JobProcessStatus import JobProcessStatus
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService
from framework.cloud.message.AwsSqsQueueService import AwsSqsQueueService
from framework.cloud.storage.AwsS3Service import AwsS3Service
from framework.cloud.storage.FtpClient import FtpClient
from framework.system.HealthService import HealthService
from framework.grdb.processor.InputFileProcessor import InputFileProcessor
from framework.grdb.core.AppDatabase import AppDatabase
from framework.system.FileService import FileService
from framework.formats.objects.Strings import Strings
from framework.grdb.infra.PodTable import PodTable
from framework.formats.xlsx.DatabaseRecordToExcelConverter import DatabaseRecordToExcelConverter
from framework.grdb.enums.PushEventType import PushEventType


LogService.log(f"SQS Listener Version: {AppConfig.APP_VERSION}, Environment: {AppConfig.ENVIRONMENT_NAME}")

def dispose_all():

	# close DB connection
	AppDatabase.dispose()

	# close FTP connnection
	FtpClient.dispose_any()



# MAIN MESSAGE LOOP
# Reads messages from SQS queue and then processes those files
# Only used in Cloud workflow
def cloudMessageLoop():

	# WGP-918: Only make DB connections after a valid job is found
	db:AppDatabase = None

	message = None
	last_completed_time = time.time()
	globe:AppGlobal = None
	try:

		last_updated_time = time.time()
		bucket = None

		while True:

			try:
				LogService.log(f"Queue list {AppConfig.SQS_ALL_QUEUE_LIST}")
				LogService.log(f"Job: Checking for hung jobs...")

				hung_job_id = 0
				current_message = None

				#-----------------------------------------------------------------------
				# read from priority queues
				for queue_url in AppConfig.SQS_ALL_QUEUE_LIST:

					receipt_handles = []

					# fetch 1 message from priority queue
					got_message = AwsSqsQueueService.fetch_message(queue_url, receipt_handles)
					if got_message is not None:
						LogService.log(f"Job: found message in {queue_url}")

						# setting the current queue
						current_message = got_message

						# fetch 1 message from common queue
						AwsSqsQueueService.fetch_message(AppConfig.SQS_INPUT_QUEUE, receipt_handles)
						break


				LogService.log(f"Job: Out of the priority loop")

				#-----------------------------------------------------------------------
				# if any message found
				if current_message is not None:

					message = current_message
					LogService.log(message)

					# get path from message -- eg: 'old_file_path' = "oganbhoj/grdb/08-20-2021/20-08-2021_13-31-11-729937_SHPT_OFR_CLASQUIN_20210614_131611615_77.csv"
					got_message, bucket, old_file_path, job_id = extractMessageMetadata(message)

					if got_message:
						LogService.log(f"Job: Started Job ID {job_id}")

						jobs_to_do = []


						#---------------------------------------------------------------
						#						JOB PART 1
						try:

							# load globals for the first job in the pod
							if db is None:
								# WGP-918: Only make DB connections after a valid job is found
								db = AppDatabase.connect()
							if globe is None:
								globe = AppGlobal(db, loadAll=True)


							# extract original file name -- eg: "SHPT_OFR_CLASQUIN_20210614_131611615_77.csv"
							original_file_name = Strings.afterFirst(Strings.afterLast(Strings.afterLast(old_file_path, "/"), "-"), "_")
							
							LogService.log(f"Job: Start processing : {original_file_name}")

							# create job context
							# Added globe object : WGP-692
							
							main_job:AppJob = AppJob(job_id, Strings.afterLast(old_file_path, "/"), bucket + '/' + old_file_path,
								old_file_path, original_file_name, db, globe)

							hung_job_id, hung_job = findAnyHungJob(main_job, db, globe)

							if hung_job:
								# lock the job to prevent other pods from processing it
								JobTable_SQS.jobLock(db, hung_job_id)

								# wait for a seconds to ensure that other pods can't process the same job
								time.sleep(1)

								# Again check if the job is still in retrying state and has same pod name
								is_job_locked_by_currenct_pod =  JobTable_SQS.isJobLocked(db, hung_job_id)

								if not is_job_locked_by_currenct_pod:
									pass
								elif hung_job.job_retries_count >= AppConfig.MAX_JOB_RETRIES:
									# if the job has reached max retries, then dont process it
									LogService.log(f"Job: Job ID {hung_job_id} has exceeded max retries. Skipping...")
									hung_job.db.module().update_record('grdb_Job', 'iJobID', hung_job.job_id,{
										"cStatus" : JobStatus.ABORTED
									})
								elif hung_job.job_retries_count < AppConfig.MAX_JOB_RETRIES:
									# if the job has not reached max retries, then process it
									jobs_to_do.append(hung_job.job_id)
									
									# increase job retries count
									hung_job.job_retries_count += 1
									
									# update job retry count in  grdb_job table
									hung_job.db.module().update_record('grdb_Job', 'iJobID', hung_job.job_id,{
										'iRetriesCount': hung_job.job_retries_count
									})
									LogService.log(f"Job: Increased job retries count for job ID {hung_job_id}. Current retries: {hung_job.job_retries_count}")

							# after the hung job process the current job
							jobs_to_do.append(job_id)
							LogService.log(f"Job: Job IDs to process : {jobs_to_do}")
							
						except Exception as e1:
							# POINT 1 of handling job failure
							# if globals failed to load or metadata queries failed
							LogService.error("ERROR during job part 1", e1)
							if 'main_job' in locals():
								onJobFailure(main_job, receipt_handles)
							else:
								LogService.log("Cannot move job to ERROR status because no AppJob available")
						#---------------------------------------------------------------



						# LOOP THROUGH MANADATORY JOBS AND DO NOT EXIT UNTILL THEY ARE COMPLETE
						for job_id in jobs_to_do:	

							#-------------------------------------------------
							# Load the releavant job object
							if job_id == hung_job_id:
								job = hung_job

							elif job_id == main_job.job_id:
								job = main_job

								# WGP-330 - same job being processed multiple times by different pods
								if job.job_status != JobStatus.QUEUED and job.job_status != JobStatus.CREATED:
									LogService.log(f"WARNING: Skipped job ID {str(job_id)} because it is in {job.job_status} state rather than CREATED or QUEUED state.")
									continue
							else:
								break

							#---------------------------------------------------------------
							#							JOB PART 2
							try:
								LogService.log(f"Job: Starting job ID {job_id}")

								# WGP-783 : If inactive skip the job
								if isJobInactive(job, receipt_handles):
									continue
								else:

									# validate the filename & file contents using the business rules
									processor = InputFileProcessor()
									processor.process(globe, job)
									LogService.log(f"Job: Completed job ID {job_id}!")


									# delete the fetched job's messages
									AwsSqsQueueService.delete_messages(receipt_handles)

							except Exception as e2:
								# POINT 2 of handling job failure
								# if any error occured during validation or insertion

								# if the hung job failed, dont bother deleting the main job's messages
								LogService.error("ERROR during job part 2", e2)
								if job_id == hung_job_id:
									onJobFailure(job, [])
								else:
									onJobFailure(job, receipt_handles)
							#---------------------------------------------------------------



						# after each message has been processed,
						# check if need to shutdown
						if not HealthService.continue_app():
							LogService.log("Job: SHUT DOWN POD as it has run for more than healthy limit.")
							return


					# save the time the last job completed
					# so the pod can be killed after X seconds
					last_completed_time = time.time()

				else:
					LogService.log("Job: No messages found in SQS")

					# Checks for cool off time before destroying the pod
					if (time.time() - last_completed_time) > AppConfig.POD_COOLOFF:
						LogService.log("Job: SHUT DOWN POD as it has past cooloff period.")
						return


			except Exception as e3:
				#----------------------------------------------------
				#			ONLY FOR NON-JOB CODE ERRORS
				LogService.error("ERROR during job loop", e3)

				# save the time the last job completed
				# so the pod can be killed after X seconds
				last_completed_time = time.time()
				#----------------------------------------------------

		return

	except Exception as e4:

		# Log error
		LogService.error("ERROR in cloud message loop", e4)

	return



# WGP-887: Ensure top level errors caught on per job basis & changes to error handling
def isJobInactive(job, receipt_handles):
	
	#	JOB INACTIVE HANDLING (iStatus=0)
	if not job.job_is_active:

		# delete the fetched job's messages
		AwsSqsQueueService.delete_messages(receipt_handles)

		# move the job file to error folder
		job.job_status_folder = "error"

		# making status inactive in Job table
		JobTable_SQS.jobInactive(job.db, job.job_id)
		LogService.log(f"WARNING: Skipped job ID {str(job.job_id)} because it is in INACTIVE state.")

		return True

	return False




# WGP-887: Ensure top level errors caught on per job basis & changes to error handling
def onJobFailure(job, receipt_handles):

	#	JOB FAILURE ERROR HANDLING
	
	#	IMPORTANT! ALL THE INNER FUNCTIONS SHOULD HANDLE
	#	THEIR OWN ERRORS SO DOES NOT CRASH AT THIS POINT.

	# delete the fetched job's messages
	AwsSqsQueueService.delete_messages(receipt_handles)

	# change job status to ERROR
	JobTable_SQS.jobCrashed2(job)

	# send email for rate upload error on failure
	job.sendEmail('rate_upload_errors', "system error")

	# move the job file to error folder
	job.job_status_folder = "error"

	# send push notification for status ERROR
	job.sendNotification(PushEventType.ERROR, None, False)

	# Move message to dead queue
	#LogService.log("Job: Moving message to dead queue")
	#if message:
	#	message_body = json.loads(message['Body'])
	#	AwsSqsQueueService.send_message_to_dead_queue(json.dumps(message_body), str(message_body['job_id']))



def findAnyHungJob(main_job, db, globe):
	# retry a dead job or hung job: WGP-178
	# get the conflict set (any previous jobs that this job is waiting on)
	conflicts = None
	#conflicts = JobTable_SQS.waitLoop_getConflicts(main_job)
	conflicts = JobTable_SQS.waitLoop_getConflictHandler(main_job)
	if len(conflicts) > 0:

		# first conflicting job is the “dependent job”
		# extract its job ID
		hung_job_id = conflicts[0][0]
		LogService.log(f"Job: Found Hung Job : {hung_job_id}")

		# check if the previous "dependant job" is hung
		job_is_hung, job_pod_name = JobTable_SQS.isJobHung(hung_job_id, db)
		if job_is_hung:
			return prepareHungJob(db, globe, hung_job_id, job_pod_name)

	return None, None



def prepareHungJob(db, globe, hung_job_id, job_pod_name):

	# marking the pod to delete for hung job
	PodTable.markPodForDeletion(db, job_pod_name)

	# to make sure to process the hung job first
	hung_fp, hung_bucket, hung_old_file_path, hung_original_file_name = JobTable_SQS.getJobInfo(hung_job_id, db)			

	# create job context
	# Added globe object : WGP-692
	hung_job:AppJob = AppJob(hung_job_id, hung_fp[-1], hung_bucket + '/' + hung_old_file_path,
		hung_old_file_path, hung_original_file_name, db, globe)

	# setting retried flag true
	hung_job.retried_job = True
	LogService.log(f"Job: Found Hung Job: {hung_job_id}")

	return hung_job_id, hung_job



def processLocalFiles():

	db:AppDatabase = AppDatabase.connect()

	# abort entire process if local data file does not exits
	for i in range(len(AppConfig.LOCAL_INPUT_FILES)):
		if not FileService.file_exists(AppConfig.LOCAL_INPUT_FILES[i]):
			raise ValueError(f"The local file does not exist! : {AppConfig.LOCAL_INPUT_FILES[i]}")

	globe:AppGlobal = AppGlobal(db, loadAll=True)

	for i in range(len(AppConfig.LOCAL_INPUT_FILES)):
		processLocalFile(db, globe, i+1, AppConfig.LOCAL_INPUT_FILES[i])

	# disconnect from all DB connections and close transaction if any
	dispose_all()


# returns Tuple of (success, bucket, file_path, new_filepath, job_id)
def extractMessageMetadata(message):
	try:
		metadata = json.loads(message['Body'])
		bucket = metadata['bucket']
		path = metadata['path']
		job_id = metadata['job_id']
		return True, bucket, path, job_id
	except Exception as e:
		LogService.error("Message cannot be processed", e)
		return False, None, None, None



# Local file testing workflow
# - simply reads and validates a local file
# - does not use any AWS resources, except for the MySQL DB
# - does not modify any AWS resources, except for the MySQL DB
def processLocalFile(db:AppDatabase, globe:AppGlobal, index, localFilePath):

	LogService.print('Begin Local Processing of: ', localFilePath)

	# modify setting path as many internal functions use it
	localFilePath = localFilePath.replace('\\', '/')
	AppConfig.LOCAL_INPUT_FILE = localFilePath

	# create a virtual cloud path that looks exactly like live paths
	# created by the lambda trigger functions and added to SQS queue
	local_filename_ext = localFilePath.split('/')[-1]
	cloud_timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S-%f')
	cloud_file_path = AppConfig.LOCAL_CLOUD_PATH + cloud_timestamp + '_' + local_filename_ext

	# normal path processing
	job_id = AppConfig.LOCAL_JOB_ID
	fp = Strings.splitPath(cloud_file_path)
	bucket = 'LOCAL'

	# extract original file name
	original_file_name = Strings.afterFirst(Strings.afterLast(Strings.afterLast(cloud_file_path, "/"), "-"), "_")

	# create job context
	# Added globe object : WGP-692
	job:AppJob = AppJob(job_id, fp[-1], bucket + '/' + cloud_file_path,
		cloud_file_path, original_file_name, db, globe)

	# Validate the filename & file contents using the business rules
	processor = InputFileProcessor()
	processor.process(globe, job)

	LogService.print('End of Local Processing')

	# To record the sql queries from dbs in xlsx file
	if AppConfig.LOCAL_TESTING and AppConfig.LOCAL_RECORD_QUERIES:		
		if not os.path.exists("query_output/"):
			os.makedirs("query_output/")

		# To record the queries from master db and module db
		DatabaseRecordToExcelConverter.convert(db.master().table_records, "query_output/masterDbRecords"+str(index)+".xlsx")
		DatabaseRecordToExcelConverter.convert(db.module().table_records, "query_output/moduleDbRecords"+str(index)+".xlsx")
		LogService.log(f"SQL Queries has been recorded")

	return True, 1


def main():
	
	if AppConfig.LOCAL_TESTING:
		# local pipeline
		processLocalFiles()
	else:
		# cloud environment
		cloudMessageLoop()

	# disconnect from all DB connections and close transaction if any
	dispose_all()

	LogService.log(f"All work done, pod shutting down....")




# Main entry point used for debugging and production
if __name__ == '__main__':
	LogService.log("Starting SQS listener...")
	main()