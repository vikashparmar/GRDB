import sys
import os
from framework.formats.yaml.YamlConfigLoader import YamlConfigLoader
# from framework.grdb.infra.PriorityConfigLoader import PriorityConfigLoader


class AppConfig:

	# Versioning
	APP_VERSION = '1.0.1'
	APP_RESOURCENAME = 'tracking'

	# Check if being run locally in VS Code or if run in automated test
	COMMAND_LINE_ARGS = sys.argv
	LOCAL_TESTING = '--local' in COMMAND_LINE_ARGS
	LOCAL_AUTOMATED_TESTING = False

	# Settings Loader
	FRAMEWORK_DIR = os.path.dirname(os.path.abspath(__file__))
	yaml = YamlConfigLoader(FRAMEWORK_DIR + "/config.yaml")

	# Change this if you are locally debugging
	LOCAL_JOB_ID = yaml.getInt('local', 'jobID', 1000)
	LOCAL_FILE_LOG_ID = yaml.getInt('local', 'fileID', 1000)
	LOCAL_MODIFY_DB = yaml.getBool('local', 'modifyDB', False)
	LOCAL_CLOUD_PATH = yaml.getStr('local', 'cloudPath')
	LOCAL_INPUT_FILE = ''
	LOCAL_INPUT_FILES = yaml.getMultilineList('local', 'inputFiles')
	LOCAL_BLOCKED_TABLES = ['grdb_Job']		# these tables will not be modified during local testing in any condition
	LOCAL_SEND_EMAIL = yaml.getBool('local', 'sendEmail', False)
	LOCAL_RECORD_QUERIES = yaml.getBool('local', 'recordSQL', False)

	# AWS Config
	AWS_REGION = yaml.getStr('aws', 'region')
	AWS_KEY1 = yaml.getStr('aws', 'accessKeyId')
	AWS_KEY2 = yaml.getStr('aws', 'secretAccessKey')

	# S3 Config
	S3_UPLOAD_BUCKET = yaml.getStr('s3', 'uploadBucket')
	S3_PROCESSING_BUCKET = yaml.getStr('s3', 'processingBucket')
	S3_API_ORIGINAL_REQUEST_BUCKET = yaml.getStr('s3', 'apiLogBucket')

	# Printing and logging
	PRINT = LOCAL_TESTING
	LOG_INFO = yaml.getBool('log', 'info')
	LOG_ERRORS = yaml.getBool('log', 'errors')
	LOG_MEMORY = yaml.getBool('log', 'memory')
	LOG_APP_NAME = yaml.getStr('log', 'appName')
	LOG_FILE_NAME = yaml.getStr('log', 'fileName')

	# Email config
	PRINT = LOCAL_TESTING
	EMAIL_PROTOCOL = yaml.getStr('email', 'protocol').lower()
	EMAIL_SOURCE = yaml.getStr('email', 'sourceEmail')
	EMAIL_DEST = []
	EMAIL_SENDER = 'WWA'
	EMAIL_REPORTURL = '#'
	EMAIL_TEMPLATE_NAME = 'validation_13'

	# Email SMTP server config
	SMTP_RETRIES = 1
	SMTP_PORT = yaml.getInt('smtp', 'port')
	SMTP_HOST = yaml.getStr('smtp', 'host')
	SMTP_USER = yaml.getStr('smtp', 'user')
	SMTP_PASS = yaml.getStr('smtp', 'pass')

	# Email templates
	EMAIL_SSI_TEMPLATE_PATH = "framework/SSI/emailTemplates/SSI_validation_email_attachment.html"

	# Master Database
	MASTER_DB_HOST = yaml.getStr('master', 'host')
	MASTER_DB_PORT = yaml.getInt('master', 'port')
	MASTER_DB_USER = yaml.getStr('master', 'user')
	MASTER_DB_PASS = yaml.getStr('master', 'pass')
	MASTER_DB_DATABASE = yaml.getStr('master', 'database')

	# Module Database
	MODULE_DB_HOST = yaml.getStr('module', 'host')
	MODULE_DB_PORT = yaml.getInt('module', 'port')
	MODULE_DB_USER = yaml.getStr('module', 'user')
	MODULE_DB_PASS = yaml.getStr('module', 'pass')
	MODULE_DB_DATABASE = yaml.getStr('module', 'database')

	BATCH_WRITES = False
