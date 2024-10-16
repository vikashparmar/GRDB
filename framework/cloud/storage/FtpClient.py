import os
import sys
import ftplib
from dateutil import parser
from datetime import datetime
from io import BytesIO, StringIO
from framework.AppConfig import AppConfig
from framework.formats.objects.Files import Files
from framework.formats.objects.Strings import Strings
from framework.formats.objects.Urls import Urls
from framework.system.LogService import LogService
from framework.formats.objects.Primitives import Primitives

class FtpClient:
	lastClient = None



	#---------------------------------------------------------------------
	# 							DYNAMIC API
	#---------------------------------------------------------------------

	def __init__(self, host:str, username:str, password:str, port:int) -> None:

		# new client
		self.host = host
		self.port = port
		self.username = username
		self.password = password
		self.ftpClient = None
		self.alive = False
		# connect to FTP server now
		self.connectFTP()
		

	def connectFTP(self):
		if self.ftpClient is None:
			try:
				self.ftpClient = ftplib.FTP()
				self.ftpClient.connect(self.host, self.port)
				self.ftpClient.login(self.username, self.password)
				self.ftpClient.encoding = "utf-8"
				self.alive = True
				return True
			except Exception as e:
				LogService.error("FTP: Error while connecting to the FTP server", e)
		return False

	def reconnect(self):
		if self.ftpClient is None or not self.is_alive():
			self.dispose()
			self.connectFTP()
		
	def is_alive(self):
		if self.ftpClient:
			try:
				# Ping to FTP server, Returns success `200 OK` if connection is alive
				self.ftpClient.voidcmd('NOOP')
				return True
			except:
				return False
		else:
			return False
			

	def dispose(self):
		if self.ftpClient is not None:
			try:
				self.ftpClient.close()
			except Exception as e:
				LogService.error("FTP: Error while disconnecting from the FTP server", e)
			self.ftpClient = None
			self.alive = False


	def isSuccess(self, resp):
		return len(resp) >= 3 and resp.startswith('2') and resp[1].isdigit() and resp[2].isdigit()


	def upload(self, destination_folder, file_name, file) -> bool:
		self.reconnect()
		if self.ftpClient is not None:
			try:
				self.ftpClient.cwd(destination_folder)
				self.ftpClient.storbinary(f"STOR {file_name}", file)
				return True
			except Exception as e:
				LogService.error("FTP: Error while uploading file to FTP server", e)
		return False


	def getListing(self, directory, type_arg):
		self.reconnect()
		if self.ftpClient is not None:
			try:
				self.ftpClient.cwd(directory)
				if type_arg == 'Name':
					return self.ftpClient.nlst()
				if type_arg == 'Machine':
					return self.ftpClient.mlsd()
			except Exception as e:
				LogService.error("FTP: Error while getting file listing of '"+directory+"' from the FTP server", e)
		return []


	def getFileDateModified(self, path) -> datetime:
		self.reconnect()
		if self.ftpClient is not None:
			try:
				resp = self.ftpClient.sendcmd("MDTM " + path)
				if self.isSuccess(resp):
					rawDate = resp[4:].strip() # eg: 20211201105212
					finalDate = parser.parse(rawDate) # a datetime object
					return finalDate
				return None
			except Exception as e:
				LogService.error("FTP: Error while getting file modified date of '"+path+"' from the FTP server", e)
		return None


	def getFileSize(self, path) -> int:
		self.reconnect()
		if self.ftpClient is not None:
			try:
				resp = self.ftpClient.sendcmd("SIZE " + path)
				if self.isSuccess(resp):
					rawNum = resp[4:].strip() # eg: 12313213
					finalNum = Primitives.parseInt(rawNum)
					return finalNum
				return 0
			except Exception as e:
				LogService.error("FTP: Error while getting file size of '"+path+"' from the FTP server", e)
		return 0


	def downloadToMemory(self, path) -> bytes:
		self.reconnect()
		if self.ftpClient is not None:
			try:
				memFile = BytesIO()
				resp = self.ftpClient.retrbinary('RETR ' + path, memFile.write)
				data = memFile.getvalue()
				return data
			except Exception as e:
				LogService.error("FTP: Error while downloading the file '"+path+"' from the FTP server", e)
		return None


	def deleteFile(self, path) -> bool:
		self.reconnect()
		if self.ftpClient is not None:
			try:
				resp = self.ftpClient.delete(path)
				return True
			except Exception as e:
				LogService.error("FTP: Error while downloading the file '"+path+"' from the FTP server", e)
		return False



	#---------------------------------------------------------------------
	# 							STATIC API
	#---------------------------------------------------------------------

	@staticmethod
	def get_instance(host, username, password, port, autoDisconnect):


		# return last client if the host and user are same
		if FtpClient.lastClient is not None and FtpClient.lastClient.alive == True and FtpClient.lastClient.is_alive():
			if FtpClient.lastClient.host == host and FtpClient.lastClient.username == username:

				# reuse last client
				return FtpClient.lastClient
			else:

				# disconnect if server changed and if auto disconnection wanted (means it keeps only 1 active client)
				if autoDisconnect:
					FtpClient.lastClient.dispose()
					FtpClient.lastClient = None
		

		# connect new client
		try:
			LogService.log(f"FTP: Connecting to FTP server: {host}")

			# new client
			newClient = FtpClient(host, username, password, port)
			FtpClient.lastClient = newClient
			return newClient

		except Exception as e:
			LogService.error("FTP: Failed to connect to FTP server", e)


	@staticmethod
	def dispose_any():
		if FtpClient.lastClient is not None:
			FtpClient.lastClient.dispose()


	# Upload the given file data bytes to the FTP Server or to local disk if testing locally
	#@staticmethod
	#def upload_file_V1(file_data, system_user_name, file_name_ext):
	#
	#	ftp_path = f"{AppConfig.FTP_ROOT}/{system_user_name}/{AppConfig.FTP_FOLDER}"
	#
	#	# Do not modify AWS resources in local testing mode
	#	if AppConfig.LOCAL_TESTING:
	#		LogService.log(f"FTP: Saving file for '{ftp_path}/{file_name_ext}' to simulate upload to FTP")
	#
	#		if not os.path.exists('output'):
	#			os.makedirs('output')
	#		if isinstance(file_data, BytesIO):
	#			file_data = file_data.getbuffer()
	#			with open("output/" + file_name_ext, "wb") as file:
	#				file.write(file_data)
	#		# for string
	#		else:
	#			with open("output/" + file_name_ext, "w") as file:
	#				file.write(file_data)
	#
	#	else:
	#
	#		try:
	#			# if this systemuser is authorized to upload files to FTP
	#			if AppConfig.IS_LIVE_CLOUD and system_user_name in AppConfig.FTP_EXTERNAL_USERS:
	#				
	#				# Upload file to FTP Server
	#				LogService.log(f"FTP: Upload file to '{ftp_path}/{file_name_ext}'")
	#				client = FtpClient.get_instance(AppConfig.FTP_HOST, AppConfig.FTP_USER, AppConfig.FTP_PASS, AppConfig.FTP_PORT, True)
	#				client.upload(ftp_path, file_name_ext, file_data)
	#			else:
	#				LogService.log(f"FTP: Uploading file to FTP server skipped due to unauthorized username '{system_user_name}'")
	#
	#		except Exception as err:
	#			LogService.error("FTP: Error while uploading to FTP server", err)



	# Upload the given file data bytes to the FTP Server or to local disk if testing locally
	@staticmethod
	def upload_file_V2(file_data, system_user_name, file_name_ext, exportPath, host, port, user, password):

		# `AppConfig.FTP_ROOT` & `system_user_name` should not be used
		# `exportPath` is the EXPORTPATH from DB config - eg: "/home/edi_shipco_prod/downloadc/grdb/"
		ftp_full_path = Urls.combine(exportPath, file_name_ext)

		# Do not modify AWS resources in local testing mode
		if AppConfig.LOCAL_TESTING:
			LogService.log(f"FTP: Saving file for '{ftp_full_path}' to simulate upload to FTP")

			Files.saveOutputFile(file_name_ext, file_data)

		else:

			try:
				# if running on staging or production cloud
				if AppConfig.IS_LIVE_CLOUD:

					# Upload file to FTP Server
					LogService.log(f"FTP: Uploading file to '{ftp_full_path}'")
					client = FtpClient.get_instance(host, user, password, port, True)
					client.upload(exportPath, file_name_ext, file_data)

				else:
					LogService.log(f"FTP: Uploading file to FTP server skipped due to develop environment")

			except Exception as err:
				LogService.error("FTP: Error while uploading to FTP server", err)
