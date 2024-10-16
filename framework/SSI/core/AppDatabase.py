import sys
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService
from framework.system.DatabaseService import DatabaseService

# WGP-516: Merge both DB engines into single implementation used across lambda and SQS listener
class AppDatabase:
	instance = None

	# main MySQL DBs used in the program
	_master_db:DatabaseService
	_module_db:DatabaseService

	# Loads the main DB, and retry 15 times x 2 seconds so retries for 30 seconds.
	def __init__(self):
		self._master_db = None
		self._module_db = None


	# get the existing connection to the master DB, or connect to it if we are not connected.
	# WGP-939: Lazy connect to master/module DBs on first query
	def master(self) -> DatabaseService:

		if self._master_db is None or self._master_db.conn is None: # 2nd check is very important for lambdas!
			LogService.log("Connect to Master DB...")

			# WGP-403: Separate out the master DB (read only) and module DB (GRDB specific data)
			# connect to master DB
			self._master_db = DatabaseService.connect_retry_loop(15,
				AppConfig.MASTER_DB_HOST, AppConfig.MASTER_DB_PORT, AppConfig.MASTER_DB_DATABASE,
				AppConfig.MASTER_DB_USER, AppConfig.MASTER_DB_PASS)

			# if failed to connect, hard exit the python program and shut down the pod
			if self._master_db is None:
				AppDatabase.dispose()
				sys.exit()
				return

		return self._master_db


	# get the existing connection to the module DB, or connect to it if we are not connected.
	# WGP-939: Lazy connect to master/module DBs on first query
	def module(self) -> DatabaseService:

		if self._module_db is None or self._module_db.conn is None: # 2nd check is very important for lambdas!
			LogService.log("Connect to Module DB...")

			# WGP-403: Separate out the master DB (read only) and module DB (GRDB specific data)
			# connect to GRDB module DB
			self._module_db = DatabaseService.connect_retry_loop(15,
				AppConfig.MODULE_DB_HOST, AppConfig.MODULE_DB_PORT, AppConfig.MODULE_DB_DATABASE,
				AppConfig.MODULE_DB_USER, AppConfig.MODULE_DB_PASS)

			# if failed to connect, hard exit the python program and shut down the pod
			if self._module_db is None:
				AppDatabase.dispose()
				sys.exit()
				return

		return self._module_db

	# disconnect from all DB connections and close transaction if any
	def disconnect(self):
		if self._master_db is not None:
			self._master_db.dispose()
			LogService.log("Sucessfully disconnected from Master DB!")
		if self._module_db is not None:
			self._module_db.dispose()
			LogService.log("Sucessfully disconnected from Module DB!")

	# Returns an AppDatabase instance, reusing it the second time
	@staticmethod
	def connect():
		if AppDatabase.instance is None:
			AppDatabase.instance = AppDatabase()
		return AppDatabase.instance

	# disconnect from all DB connections and close transaction if any
	@staticmethod
	def dispose():
		LogService.log("Disconnect from DBs (if any)")
		if AppDatabase.instance is not None:
			AppDatabase.instance.disconnect()
			AppDatabase.instance = None