from datetime import datetime
from lxml import etree #pip install lxml
from framework.SSE.clients.dir_client import DIRClient
from framework.SSE.clients.ftp_client import FTPClient
from framework.SSE.clients.sftp_client import SFTPClient
from framework.SSE.job.AppJob import AppJob
from framework.SSE.tables.weiExportMessageLogTable import weiExportMessageLog
from framework.SSE.tables.weiFileLogNewTable import weiFileLogNew
from framework.SSE.tables.weiFileMetaDataLogTable import weiFileMetaDataLog
from framework.SSE.tables.weiJobsTable import weiJobs
from framework.system.LogService import LogService


class SendFile:
    @staticmethod
    def send(db, job:AppJob, data, module_type=None, start_time=""):
        # check the entry for file is in wei_Export_message_log or not according to module type
        if module_type == "TS":
            shipment_ids = job.ts_shipment_id_list
            fetched_files = weiExportMessageLog.select(db, {'queryType': 'TS'}, shipment_ids=job.ts_shipment_id_list)
            customer_log_details = job.ts_customer_log_details
            member_log_details = job.ts_member_log_details
        elif module_type == "SS":
            shipment_ids = job.sse_shipment_id_list
            fetched_files = weiExportMessageLog.select(db, {'queryType': 'SS'}, shipment_ids=job.sse_shipment_id_list)
            customer_log_details = job.ss_customer_log_details
            member_log_details = job.ss_member_log_details
        else:
            LogService.print(f"SSE: Please provide the valid module type")

        fetched_file_list = [i.get('iShipmentdetailID') for i in fetched_files]
        sent_to_list = [id for id in shipment_ids if id not in fetched_file_list]

        # check that there is any file
        if len(data) > 0:
            for row in range(len(data)):
                # collect values to be inserted
                shipment_detail_id = data[row].get("iShipmentdetailID")
                if shipment_detail_id in sent_to_list:
                    status_code = int(data[row].get("cStatusCode"))
                    career_scac = data[row].get("cCarrierSCAC")
                    current_status = "FILE GENERATED"
                    error_message = "File is not sent"
                    status = 0

                    if len(member_log_details) > 0:
                        # collect data for member entries
                        member_program_id = member_log_details[row].get("program_id")
                        member_file_name = member_log_details[row].get("file_name")
                        member_file_path = member_log_details[row].get("file_dest") + "/" + member_file_name
                        member_file_format = member_log_details[row].get("file_format")
                        member_file_type = member_log_details[row].get("file_type")
                        member_file_transfer_type = member_log_details[row].get("file_transfer_type")
                        member_sender = member_log_details[row].get("sender")
                        member_receiver = member_log_details[row].get("receiver")
                        customer_alias = member_log_details[row].get("customerAlias")
                        member_file_sent_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # convert to specific format (remove timestamp)
                        
                        member_values = (shipment_detail_id, member_program_id, status_code, career_scac,
                                        member_file_name, member_file_sent_time)


                        # insert the data for member
                        weiExportMessageLog.insert(db, values=member_values)

                        # extract data for member job logs
                        member_log_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        member_job_log_values = (member_file_name, member_file_path, member_program_id,
                                                 member_file_format, member_file_type, current_status, error_message,
                                                 member_sender, member_receiver, start_time, member_log_end_time, status)

                        # insert member logs
                        last_member_log_id = weiJobs.insert(db, values=member_job_log_values)

                        # extract data for member file data logs
                        entered_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        member_file_data_log_values = (member_file_name, member_file_path, member_program_id,
                                                       error_message, member_sender, member_receiver, customer_alias,
                                                       member_file_sent_time, start_time, member_log_end_time,
                                                       entered_time)
                        # insert member file data logs
                        last_member_file_log_id = weiFileLogNew.insert(db, values=member_file_data_log_values)
                        
                        # extracting the member meta data and insert into table
                        SendFile.fetch_and_insert_meta_data(db, last_member_file_log_id, member_log_details[row])

                    if len(customer_log_details) > 0:
                        # collect data for customer entries
                        customer_program_id = customer_log_details[row].get("program_id")
                        customer_file_name = customer_log_details[row].get("file_name")
                        customer_file_path = customer_log_details[row].get("file_dest") + "/" + customer_file_name
                        customer_file_format = customer_log_details[row].get("file_format")
                        customer_file_type = customer_log_details[row].get("file_type")
                        customer_file_transfer_type = customer_log_details[row].get("file_transfer_type")
                        customer_sender = customer_log_details[row].get("sender")
                        customer_receiver = customer_log_details[row].get("receiver")
                        customer_alias = customer_log_details[row].get("customerAlias")
                        customer_file_sent_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # convert to specific format (remove timestamp)
                        customer_values = (shipment_detail_id, customer_program_id, status_code, career_scac,
                                        customer_file_name, customer_file_sent_time)

                        # insert the data for customer
                        weiExportMessageLog.insert(db, values=customer_values)

                        # extract data for customer job logs
                        customer_log_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        customer_job_log_values = (customer_file_name, customer_file_path, customer_program_id,
                                                   customer_file_format, customer_file_type, current_status,
                                                   error_message, customer_sender, customer_receiver, start_time,
                                                   customer_log_end_time, status)

                        # insert customer logs
                        last_customer_log_id = weiJobs.insert(db, values=customer_job_log_values)

                        # extract data for customer file data logs
                        entered_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        customer_file_data_log_values = (customer_file_name, customer_file_path, customer_program_id,
                                                         error_message, customer_sender, customer_receiver, customer_alias,
                                                         customer_file_sent_time, start_time, customer_log_end_time,
                                                         entered_time)
                        # insert customer file data logs
                        last_customer_file_log_id = weiFileLogNew.insert(db, values=customer_file_data_log_values)

                        # extracting the customer meta data and insert into table
                        SendFile.fetch_and_insert_meta_data(db, last_customer_file_log_id, customer_log_details[row])

                    # Send file to member
                    # if member_file_transfer_type == "DIR":
                        # DIRClient.send(member_receiver, member_file_name)
                    # elif member_file_transfer_type == "FTP":
                        # FTPClient.send(member_receiver, member_file_name)
                    # elif member_file_transfer_type == "SFTP":
                        # SFTPClient.send(member_receiver, member_file_name)
                    # else:
                        # pass

                    # Send file to customer
                    # if customer_file_transfer_type == "DIR":
                        # DIRClient.send(customer_receiver, customer_file_name)
                    # elif customer_file_transfer_type == "FTP":
                        # FTPClient.send(customer_receiver, customer_file_name)
                    # elif customer_file_transfer_type == "SFTP":
                        # SFTPClient.send(customer_receiver, customer_file_name)
                    # else:
                        # pass

                    # if data[row].get("cStatustype") == "E":
                    #     # Send file to member	
                    #     SFTPClient.send(member_receiver[row], file_name)
                    # else:
                    #     # Send file to member and customer	
                    #     SFTPClient.send(member_receiver[row], file_name)

                    # update Job logs after the file is sent
                    # log_sent_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # weiJobs.update(db, job, data_query={"logID": last_member_log_id, "currentStatus": "FILE SENT", "sentTime": log_sent_time})
                    # weiJobs.update(db, job, data_query={"logID": last_customer_log_id, "currentStatus": "FILE SENT", "sentTime": log_sent_time})
                else:
                    LogService.print(f"SSE: Files are already sent for shipmentdetailID {shipment_detail_id}")
            return True
        else:
            LogService.print("SSE: No files to sent")
    
    def fetch_and_insert_meta_data(db, file_log_id, log_detail):
        """Fetching the Meta Data from file and Inserted into wei_File_Meta_Data_Log table"""
        data_dict = {}
        log_file_name = log_detail.get('file_name')
        tags_checking_list = ['BookingNumber', 'ArrivalNoticeNumber', 'OBLNumber', 'LotNumber', 'ShipperReference',
                            'ForwarderReference', 'ConsigneeReference', 'CommunicationReference', 'CustomerAlias']
        tree = etree.parse('framework/SSE/files_generated/' + log_file_name)
        tree_root = tree.getroot()

        for elem in tree_root[1]:
            if elem.tag in tags_checking_list and elem.text not in (None, ''):
                data_dict[elem.tag] = elem.text
            elif elem.tag == 'StatusCode' and elem.text not in (None, ''):
                if elem.text in (51, 52, 53, '51', '52', '53'):
                    data_dict[elem.tag] = '10' + str(elem.text)
                else:
                    data_dict[elem.tag] = elem.text

        for key, val in data_dict.items():
            entered_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            value_list = (file_log_id, key, val, 0, entered_time)
            weiFileMetaDataLog.insert(db, values=value_list)