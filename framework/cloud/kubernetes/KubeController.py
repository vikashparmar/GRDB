import subprocess

from framework.system.LogService import LogService

class KubeController:
	
	@staticmethod
	def getRunningPods():
		process = subprocess.run(['sudo','kubectl','get','pods','-o','wide'],stdout=subprocess.PIPE, universal_newlines=True)
		array = process.stdout.split('\n')[1:]
		pod_ids = []
		for x in array:
			data = x.split()
			if len(data)>1:
				pod_ids.append(data)
		return pod_ids

	@staticmethod
	def deleteRunningPod(podName):
		try:
			process = subprocess.run(['sudo','kubectl','delete','pods',podName],stdout=subprocess.PIPE, universal_newlines=True)
			print(process.stdout)
			return True
		except Exception as e:
			LogService.error(f"Error: Error in deleting Pod {podName}", e)
			return False
	
	@staticmethod
	def deleteAllPods():
		try:
			process = subprocess.run(['sudo','kubectl','delete','--all','pods','--namespace=default','--grace-period=0','--force'],
									stdout=subprocess.PIPE, universal_newlines=True)
			print(process.stdout)
			return True
		except Exception as e:
			LogService.error(f"Error: Error in deleting all pods", e)
			return False