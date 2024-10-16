import sys
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import pathlib
from framework.system.MemoryService import MemoryService
from framework.AppConfig import AppConfig


class LogService:

	logger = None

	deep_join = lambda L: ' '.join([LogService.deep_join(x) if type(x) is list else x for x in L]) # type: ignore

	@staticmethod
	def _init():

		# WGP-478: Disable logging to disk on AWS lambda because disk is read-only
		if not AppConfig.IS_LAMBDA and LogService.logger is None:

			# create and return logger which writes to disk (name can be anything)
			LogService.logger = AppLogger().get_logger(AppConfig.APP_RESOURCENAME) 

	@staticmethod
	def print(*args):
		if AppConfig.PRINT:
			if len(args) == 1 and isinstance(args[0], str):
				print("Print: " + args[0])
			else:
				try:
					print("Print: " + LogService.deep_join(args))
				except:
					print(args)


	@staticmethod
	def log(text:str):
		if AppConfig.LOG_INFO:

			# Only use logger subsystem for online testing to bypass annoying errors that appear on local testing
			# ('The process cannot access the file because it is being used by another process:')
			if AppConfig.LOCAL_TESTING or AppConfig.IS_LAMBDA:
				if AppConfig.LOG_MEMORY:
					print("Info:  " + MemoryService.getMemoryUsedStr() + " - " + str(text))
				else:
					print("Info:  " + str(text))
			else:
				if LogService.logger is None:
					LogService._init()
				if AppConfig.LOG_MEMORY:
					LogService.LogService.print(MemoryService.getMemoryUsedStr() + " - " + str(text))
				else:
					LogService.LogService.print(text)


	@staticmethod
	def error(text:str, exception = None):
		if AppConfig.LOG_ERRORS:

			# Generate a stack trace at this point
			# which also includes information about the caller
			exc_type, exc_obj, exc_tb = sys.exc_info()
			final_error = ''
			if exc_tb is None:
				final_error = (f"Global scope error: {text}")

			# If no exception is given, just trace the text and stack
			elif exception is None:
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				final_error = (f"{text}, Filename: {fname}, Line: {exc_tb.tb_lineno}")

			# If exception is given, trace the exception info as well
			else:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] # type: ignore
				final_error = (f"{text}, Filename: {fname}, Line: {exc_tb.tb_lineno}, Exception: {exc_type}, {str(exception)}") # type: ignore

			# Only use logger subsystem for online testing to bypass annoying errors that appear on local testing
			# ('The process cannot access the file because it is being used by another process:')
			if AppConfig.LOCAL_TESTING or AppConfig.IS_LAMBDA:
				print("Error: " + final_error)
			else:
				if LogService.logger is None:
					LogService._init()
				LogService.logger.error(final_error)
		


class AppLogger(object):
	def __init__(self):
		self.log_directory_path = "/var/log/containers"
		self.log_filename = os.path.join(self.log_directory_path, AppConfig.LOG_FILE_NAME)
		log_dir = os.path.join(self.log_directory_path, AppConfig.LOG_APP_NAME)
		pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)

	def get_logger(self, logger_name):
		logger = logging.getLogger(logger_name)
		logger.setLevel(logging.INFO)

		file_handler = TimedRotatingFileHandler(self.log_filename, when='m', interval=15)
		file_handler.setLevel(logging.INFO)
		f_format = logging.Formatter('%(levelname)s - %(message)s')
		file_handler.setFormatter(f_format)
		logger.addHandler(file_handler)
		console_handler = logging.StreamHandler()
		console_handler.setFormatter(f_format)
		logger.addHandler(console_handler)
		return logger