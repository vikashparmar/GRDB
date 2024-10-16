import time
from framework.AppConfig import AppConfig
from framework.system.LogService import LogService

class HealthService:

	# record start of app
	app_start_time = time.process_time() / 60 		# convert to minutes

	# check if should stop
	@staticmethod
	def continue_app():
		cur_time = time.process_time() / 60 		# convert to minutes
		run_time = round(cur_time - HealthService.app_start_time) # convert to minutes
		
		LogService.log(f"HEALTH: System running for {str(run_time)} minutes...")

		if run_time > AppConfig.POD_MAX_DURATION:
			LogService.log("HEALTH: SYSTEM SHOULD SHUTDOWN!")
			return False

		LogService.log("HEALTH: System can continue!")
		return True