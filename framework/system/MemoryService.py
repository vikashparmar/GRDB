import os
import psutil
import os


class MemoryService:

	# declare globals
	proc_info = None
	sysmem_info = None

	@staticmethod
	def _init():

		# get process info using psinfo
		proc_id = os.getpid()
		MemoryService.proc_info = psutil.Process(proc_id)
		MemoryService.sysmem_info = psutil.virtual_memory()


	@staticmethod
	def getMemoryUsedBytes():

		# one-time init if blank
		if MemoryService.proc_info is None:
			MemoryService._init()

		appmem = MemoryService.proc_info.memory_info()
		
		# just report used memory by python
		return appmem.rss



	@staticmethod
	def getMemoryUsedStr():
		used = MemoryService.getMemoryUsedBytes()
		return f"{str(round(used / 1000000))} MB"

