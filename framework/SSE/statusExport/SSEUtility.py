import re, time
from datetime import datetime
from framework.formats.x12.x12_creator import X12Creator
from framework.formats.xml.xml_creator import XMLCreator
from framework.SSE.dataCreation.ShipmentStatusData import ShipmentStatusData
from framework.SSE.dataCreation.LinkDelinkData import LinkDelinkData
from framework.SSE.dataCreation.TransShipmentData import TransShipmentData
from framework.SSE.job.AppJob import AppJob
from framework.SSE.tables.booBookingTable import booBooking
from framework.SSE.tables.fetchCustomerDetails import CustomerDetails
from framework.SSE.tables.fetchMemberDetails import MemberDetails
from framework.SSE.tables.fileBLDetailTable import fileBLDetail
from framework.SSE.tables.genLocationTable import genLocation
from framework.SSE.tables.genStatusTable import genStatus
from framework.SSE.tables.seiMemberSettingTable import seiMemberSetting
from framework.system.LogService import LogService

# if the origin and destination are same ,no need to send milestone file.
# in case of origin and destination are different ,the milestone file have to send based on status subscription by member like shipco or customer like agility 
# neeed to get the statuses for every 15min based on db_entry time or flag and then filter the statuses based on subscription 
# need to check origin and destination
# based on origin and destination need to send the milestone file.

class Utility:
    @staticmethod
    def member_data(db, job:AppJob, element):
        """
        creating the member data schema and get member origin and destination 
        """
        for place in element:
            org_data=place.get('ShipmentStatusDetails')
            data = org_data.copy()  # make a copy to remove some tags
            # remove such tags which are not required in member's schema
            schema_type = place.get('SchemaType')
            if schema_type != 'link_delink':
                del data['CarrierBookingNumber']
                del data['CarrierBillofLadingNumber']
                del data['FileNumber']
                del data['ReleaseType']
                del data['OfficeCode']
            status_code = data.get('StatusCode')
            if int(status_code) in job.member_block_statuses:
                LogService.print(f"SSE: status {status_code} was blocked for member")
                continue
            if data['RoutingDetails']['PlaceOfReceipt']!='':
                origin = data['RoutingDetails']['PlaceOfReceipt']
            else:
                origin = data['RoutingDetails']['PortOfLoading']
            if data['RoutingDetails']['PlaceOfDelivery']!='':
                destination = data['RoutingDetails']['PlaceOfDelivery']
            else:
                destination = data['RoutingDetails']['PortOfDischarge']
            
            if origin == destination:
                LogService.print(f"SSE: origin{origin} and destination {destination}are same for shipment reference {data['WWAShipmentReference']}")
                continue

            details = MemberDetails.fetch(db, job, data_query={"origin": origin,"destination": destination,'StatusCode': status_code})
            if len(details) == 0:
                LogService.print(f"SSE: {origin}")
            elif details:
                transfer_details = details.get("file_transfer_data")
                if len(transfer_details) == 0:
                    continue
                message_detail = details.get('message_detail')
                LogService.print(f"SSE: message {message_detail}")

                # Check for blocked status
                if status_code == '5':
                    fetched_block_status = seiMemberSetting.select(db, data_query={'memberID': message_detail.get('iMemberID'),
                                                                                    'programID': message_detail.get('iProgramID'),
                                                                                    'code': 'send_status_5'})
    
                    if len(fetched_block_status) > 0:
                        if fetched_block_status[0].get('cValue') in ('N', ''):
                            continue
                    else:
                        continue

                details = details.get('data')[0]
                transfer_details =transfer_details[0]
                current_time = datetime.now()
                YYYYMMDD = datetime.strftime(current_time.date(),'%Y%m%d')
                HHmmSS = datetime.strftime(current_time,'%H%M%S')
                uuu = datetime.strftime(current_time,'%f')
                message_log_detail = {}                     
                file_name = transfer_details.get('cFilenameformat').replace("{{YYYYMMDD}}",YYYYMMDD).replace("{{HHmmSS}}",HHmmSS).replace("{{uuu}}",uuu)
                file_format = transfer_details.get('cMessageformat')
                member_receiver = details.get('cCompanycode')
                member_program_id = message_detail.get("iProgramID")
                file_dest = transfer_details.get("cDestination")
                file_transfer_type = transfer_details.get('cTransfertype')
                # append member log details
                job.ss_member_log_details.append({"sender": "WorldWideAlliance", "receiver": member_receiver,
                                                    "file_name": file_name, "file_format": file_format,
                                                    "program_id": member_program_id, "file_dest": file_dest,
                                                    "customerAlias": org_data.get('CustomerAlias'),
                                                    "file_transfer_type": file_transfer_type, "file_type": "SS"})
                
                # checking for member-to-member booking
                is_send_to_submitter = False
                member_booking_response = booBooking.select(db, data_query={'WWAShipmentReference': org_data.get('WWAShipmentReference')})
                if len(member_booking_response) > 0:
                    member_id = member_booking_response[0].get('iMemberID')
                    company_code = member_booking_response[0].get('cCompanycode')
                    # check the member setting, it is configured to send file or not
                    mem_setting_data = seiMemberSetting.select(db, data_query={'memberID': member_id, 'programID': job.program_id})
                    for item in mem_setting_data:
                        if item.get('cCode') == 'send_to_submitter' and item.get('cValue') == 'Y':
                            is_send_to_submitter = True

                if file_format.lower()=='xml':
                    Envelope={}
                    Envelope['SenderID'] ='WorldWideAlliance'
                    Envelope['ReceiverID'] = re.sub('\s+','',details.get('cCompanycode'))
                    Envelope['Password'] = 'XXXXXXXXXXXXX'
                    Envelope['Type'] = 'Shipment_Status_XML_1.0.0'
                    Envelope['Version'] = '1.0.0'
                    Envelope['EnvelopeID'] = '1614669843168'
                    data_detail = {'Envelope':Envelope,'ShipmentStatusDetails':data}
                    message_log_detail['cFilename'] =file_name
                    message_log_detail['iMemberID'] = message_detail.get('iMemberID')
                    message_log_detail['iProgramID'] = message_detail.get('iProgramID')
                    message_log_detail['cStatuscode'] = status_code
                    message_log_detail['cExternalStatusCode'] = status_code
                    message_log_detail['iItemID'] = data.get('WWAShipmentReference')
                    XMLCreator.create(element={'data':data_detail, 'transfer':file_name,
                                               'message_log_detail': message_log_detail}, schema_type=schema_type)

                    # creating file for member-to-member booking
                    if is_send_to_submitter:
                        current_time = datetime.now()
                        YYYYMMDD = datetime.strftime(current_time.date(),'%Y%m%d')
                        HHmmSS = datetime.strftime(current_time,'%H%M%S')
                        uuu = datetime.strftime(current_time,'%f')
                        submitter_file_name = transfer_details.get('cFilenameformat').replace("{{YYYYMMDD}}",YYYYMMDD).replace("{{HHmmSS}}",HHmmSS).replace("{{uuu}}",uuu)
                        message_log_detail['cFilename'] = submitter_file_name
                        message_log_detail['iMemberID'] = member_id
                        
                        Envelope['ReceiverID'] = company_code
                        data_detail = {'Envelope':Envelope, 'ShipmentStatusDetails':data}

                        job.ss_member_log_details.append({"sender": "WorldWideAlliance", "receiver": company_code,
                                                          "file_name": submitter_file_name, "file_format": file_format,
                                                          "program_id": member_program_id, "file_dest": file_dest,
                                                          "customerAlias": org_data.get('CustomerAlias'),
                                                          "file_transfer_type": file_transfer_type, "file_type": "SS"})
                        XMLCreator.create(element={'data': data_detail, 'transfer': submitter_file_name,
                                                   'message_log_detail': message_log_detail}, schema_type=schema_type)
    

    @staticmethod
    def data_create(db, job:AppJob, data): 
        """ use case of this function to construct  data structure based on schema"""
        data = {re.sub('^[cti]','',key):value for key,value in data.items()}
        st_code = data.get('StatusCode')

        if st_code not in job.block_statuses:
            if st_code in ('51', '52', '53', '1051', '1052', '1053'):
                return_data = TransShipmentData.create(db, job, data)
                return return_data
            elif st_code in ('600', '601', '604'):
                return_data = LinkDelinkData.create(job, data)
                return return_data
            else:
                return_data = ShipmentStatusData.create(db, job, data)
                return return_data
            
        else:
            LogService.print(f"SSE: This status_code {st_code} was blocked to send the file") 


    @staticmethod
    def customer_data(db, job:AppJob, element):
        """use case of this function is to check the customer subscription based on status and construct the data based on customer structure"""
        for x in element:
            data = x.get('ShipmentStatusDetails')
            schema_type = x.get('SchemaType')
            bill_of_lading_number = x.get('BillOfLadingNumber')
            cust_alias =  data.get('CustomerAlias')
            stat_code = data.get('StatusCode')
            cust_detail = CustomerDetails.fetch(db, job, data_query={'CustomerAlias': cust_alias,'StatusCode': stat_code})
            if len(cust_detail) == 0 or 'message' in cust_detail.keys():
                LogService.print(f"SSE: customer {cust_alias} was not subscribed on this status_code {stat_code}")
                continue
            elif cust_detail:
                if cust_detail['cCompanycode'] != "edi_knmanifest_prod" and cust_detail['StatusCode'] in ['1068','1067','1069']:
                    continue

                # Check for blocked status
                if stat_code == '5':
                    fetched_block_status = seiMemberSetting.select(db, data_query={'memberID': cust_detail.get('iMemberID'),
                                                                                    'programID': cust_detail.get('iProgramID'),
                                                                                    'code': 'send_status_5'})
    
                    if len(fetched_block_status) > 0:
                        if fetched_block_status[0].get('cValue') in ('N', ''):
                            continue
                    else:
                        continue
                
                fetched_send_same_status = seiMemberSetting.select(db, data_query={'memberID': cust_detail.get('iMemberID'),
                                                                                    'programID': cust_detail.get('iProgramID'),
                                                                                    'code': 'send_same_status'})

                is_send_kn_status = False
                if len(fetched_send_same_status) > 0:
                    # for KN Manifest customer only
                    is_send_kn_status = True
                    extended_status = fetched_send_same_status[0].get('cExtendedcode')
                    same_status_data1 = Utility.send_same_status_file(db, data, {'LadingNumber': bill_of_lading_number})
                    same_status_data2 = Utility.send_same_status_file(db, data, {'LadingNumber': bill_of_lading_number})

                transfer_details = cust_detail.get('file_transfer_data')[0]
                current_time = datetime.now()
                message_log_detail={}
                YYYYMMDD = datetime.strftime(current_time.date(),'%Y%m%d')
                HHmmSS = datetime.strftime(current_time,'%H%M%S')
                uuu = datetime.strftime(current_time,'%f')
                file_name = transfer_details.get('cFilenameformat').replace("{{YYYYMMDD}}",YYYYMMDD).replace("{{HHmmSS}}",HHmmSS).replace("{{uuu}}",uuu)
                file_format = transfer_details.get('cMessageformat')
                customer_receiver = cust_detail.get('cCompanycode')
                # EXPEDITORS customer access the files from Shipco
                customer_receiver = "edi_shipco_prod" if customer_receiver == "edi_expeditors_prod" else customer_receiver
                customer_program_id = cust_detail.get("iProgramID")
                file_dest = transfer_details.get("cDestination")
                file_transfer_type = transfer_details.get('cTransfertype')
                # append customer log details
                job.ss_customer_log_details.append({"sender": "WorldWideAlliance", "receiver": customer_receiver,
                                                    "file_name": file_name, "file_format": file_format,
                                                    "program_id": customer_program_id, "file_dest": file_dest,
                                                    "customerAlias": cust_alias,
                                                    "file_transfer_type": file_transfer_type, "file_type": "SS"})
            
                if file_format.lower()=='xml':
                    data['StatusCode'] = cust_detail['StatusCode']
                    Envelope = {}
                    Envelope['SenderID'] ='WorldWideAlliance'
                    Envelope['ReceiverID'] = re.sub('\s+','',cust_detail.get('cCompanycode'))
                    Envelope['Password'] = 'XXXXXXXXXXXXX'
                    Envelope['Type'] = 'Shipment_Status_XML_1.0.0'
                    Envelope['Version'] = '1.0.0'
                    Envelope['EnvelopeID'] = '1614669843168'
                    data_detail = {'Envelope':Envelope,'ShipmentStatusDetails':data}
                    message_log_detail['cFilename'] =file_name
                    message_log_detail['iMemberID'] = cust_detail.get('iMemberID')
                    message_log_detail['iProgramID'] = cust_detail.get('iProgramID')
                    message_log_detail['cStatuscode'] = stat_code
                    message_log_detail['cExternalStatusCode'] = cust_detail.get('StatusCode')
                    message_log_detail['iItemID'] = data.get('WWAShipmentReference')
                    
                    if is_send_kn_status:
                        # for send_same_status feature
                        time.sleep(0.000001)  # apply sleep to make a difference of micro-second in time for filename
                        current_time = datetime.now()
                        YYYYMMDD = datetime.strftime(current_time.date(),'%Y%m%d')
                        HHmmSS = datetime.strftime(current_time,'%H%M%S')
                        uuu = datetime.strftime(current_time,'%f')
                        file_name1 = transfer_details.get('cFilenameformat').replace("{{YYYYMMDD}}",YYYYMMDD).replace("{{HHmmSS}}",HHmmSS).replace("{{uuu}}",uuu)
                        job.ss_customer_log_details.append({"sender": "WorldWideAlliance", "receiver": customer_receiver,
                                                            "file_name": file_name1, "file_format": file_format,
                                                            "program_id": customer_program_id, "file_dest": file_dest,
                                                            "customerAlias": cust_alias,
                                                            "file_transfer_type": file_transfer_type, "file_type": "SS"})
                        
                        schema_type = 'send_same_status'
                        envelope = {'recipientId': 'KN', 'senderId': 'wwalliance'}

                        data_detail1 = {"envelope": envelope, "cargos": same_status_data1.get('Cargo')}
                        data_detail2 = {"envelope": envelope, "cargos": same_status_data2.get('Cargo')}
                        container_number = same_status_data1.get('ContainerNumber')

                        XMLCreator.create(element={'data': data_detail1, 'transfer': file_name,
                                                   'message_log_detail': message_log_detail,
                                                   'attributes': {'Id': '1614669843168',
                                                                  'ContainerNumber': container_number,
                                                                  'StatusCode': cust_detail['StatusCode']}},
                                                   schema_type=schema_type)
                        XMLCreator.create(element={'data': data_detail2, 'transfer': file_name1,
                                                   'message_log_detail': message_log_detail,
                                                   'attributes': {'Id': '1614669843168',
                                                                  'ContainerNumber': container_number,
                                                                  'StatusCode': extended_status}},
                                                   schema_type=schema_type)
                    else:
                        XMLCreator.create(element={'data': data_detail, 'transfer': file_name,
                                                   'message_log_detail': message_log_detail}, schema_type=schema_type)
                
                elif file_format.lower() == 'x12':
                    # fetching the data from member settings for the memberID
                    fetched_setting_data = seiMemberSetting.select(db, data_query={'memberID': cust_detail.get('iMemberID'),
                                                                                    'programID': cust_detail.get('iProgramID')})

                    cucc_code, equip_no_check_digit, trim_segment, element_seperator = '', '', '', ''
                    receiver_id = cust_detail.get('cCompanycode').replace('edi_', '').replace('_prod', '').upper()
                    is_n9ca, is_carrier_scac_315 = False, False

                    for item in fetched_setting_data:
                        if item.get('cCode') == "ReceiverID":
                            receiver_id = item.get('cValue')
                        elif item.get('cCode') == "cucc_code":
                            cucc_code = item.get('cValue')
                        elif item.get('cCode') == "equipmentno_checkdigit":
                            equip_no_check_digit = item.get('cValue')
                        elif item.get('cCode') == "trim_segment":
                            trim_segment = item.get('cValue')
                        elif item.get('cCode') == "ElementSeparator":
                            element_seperator = item.get('cValue')
                        elif item.get('cCode') == "carrier_scac_315":
                            is_carrier_scac_315 = True
                        elif item.get('cCode') == "x12_N9CA" and item.get('cValue') == "Y":
                            is_n9ca = True

                    # fetching the City Name accordingly
                    routing_details = data.get('RoutingDetails')
                    place_of_receipt = routing_details.get('PlaceOfReceipt')
                    place_of_receipt = '' if place_of_receipt is None else place_of_receipt

                    port_of_loading = routing_details.get('PortOfLoading')
                    port_of_loading = '' if port_of_loading is None else port_of_loading

                    port_of_discharge = routing_details.get('PortOfDischarge')
                    port_of_discharge = '' if port_of_discharge is None else port_of_discharge

                    place_of_delivery = routing_details.get('PlaceOfDelivery')
                    place_of_delivery = '' if place_of_delivery is None else place_of_delivery

                    search_values = (place_of_receipt, port_of_loading, port_of_discharge, place_of_delivery)
                    fetched_city = genLocation.select(db, data_query={'values': search_values})

                    place_of_receipt_city, port_of_loading_city = '', ''
                    port_of_discharge_city, place_of_delivery_city = '', ''
                    for item in fetched_city:
                        if item.get('cCode') == place_of_receipt:
                            place_of_receipt_city = item.get('cCityname')
                        if item.get('cCode') == port_of_loading:
                            port_of_loading_city = item.get('cCityname')
                        if item.get('cCode') == port_of_discharge:
                            port_of_discharge_city = item.get('cCityname')
                        if item.get('cCode') == place_of_delivery:
                            place_of_delivery_city = item.get('cCityname')

                    Envelope = {}
                    Envelope['SenderID'] = 'WWA'
                    Envelope['ReceiverID'] = receiver_id
                    data_detail = {'Envelope': Envelope, 'ShipmentStatusDetails': data}
                    message_log_detail['cFilename'] = file_name
                    message_log_detail['iMemberID'] = cust_detail.get('iMemberID')
                    message_log_detail['iProgramID'] = cust_detail.get('iProgramID')
                    message_log_detail['cStatuscode'] = stat_code
                    message_log_detail['cExternalStatusCode'] = cust_detail.get('StatusCode')
                    message_log_detail['iItemID'] = data.get('WWAShipmentReference')
                    message_log_detail['CuccCode'] = cucc_code
                    message_log_detail['TrimSegment'] = trim_segment
                    message_log_detail['ElementSeperator'] = element_seperator
                    message_log_detail['CarrieSCAC315'] = is_carrier_scac_315
                    message_log_detail['N9CA'] = is_n9ca
                    message_log_detail['EquipmentNoCheckDigit'] = equip_no_check_digit
                    message_log_detail['PlaceOfReceiptCityName'] = place_of_receipt_city
                    message_log_detail['PortOfLoadingCityName'] = port_of_loading_city
                    message_log_detail['PortOfDischargeCityName'] = port_of_discharge_city
                    message_log_detail['PlaceOfDeliveryCityName'] = place_of_delivery_city
                    X12Creator.create({'data': data_detail, 'message_log_detail': message_log_detail})


    @staticmethod
    def send_same_status_file(db, data, data_dict):
        """ Send Same Status feature for KN Manifest customer """
        status_code = data.get('StatusCode')
        status_loc_code = data.get('StatusLocationCode')
        status_date_time_details = data.get('StatusDateTimeDetails')
        status_date = status_date_time_details.get('Date') + "T" + status_date_time_details.get('Time')
        bill_of_lading_number = data_dict.get('LadingNumber')

        status_name = genStatus.select(db, data_query={'StatusCode': status_code})
        status_name = status_name[0].get('cStatusname') if len(status_name) > 0 else ''

        tags_dict = {"container": '', "status": ''}
        master_track_no = fileBLDetail.select(db, data_query={"LadingNumber": bill_of_lading_number})
        master_track_no = master_track_no[0].get('cMasterTrackingNumber') if len(master_track_no) > 0 else ''

        tags_dict["container"] = {"billOfLading": bill_of_lading_number,
                                "masterTrackingNumber": master_track_no}
        tags_dict["status"] = {"name": status_name, "date": status_date, "unLocationCode": status_loc_code}

        return {"Cargo": {"Cargo": tags_dict}, "ContainerNumber": data.get('ContainerNumber')}


    @staticmethod
    def trans_member_data(db, job:AppJob, element):
        """
        creating the member data schema and get member origin and destination for Transhipment status
        """
        for place in element:
            data = place.get('trans_shipment_status_details')
            status_code = data.get('TSStatusCode')
            if int(status_code) in job.member_block_statuses:
                LogService.print(f"SSE: status {status_code} was blocked for member")
                continue

            if data.get('TSRoutingDetails') != "":
                origin = data.get('TSRoutingDetails').get('TSPortOfLoading')
                destination = data.get('TSRoutingDetails').get('TSPortOfDischarge')
            else:
                origin, destination = "", ""

            if origin == destination:
                LogService.print(f"SSE: origin{origin} and destination {destination} are same for trans shipment reference")
                continue

            details = MemberDetails.fetch(db, job, data_query={"origin": origin,"destination": destination,'StatusCode': status_code})

            if len(details) == 0:
                LogService.print(f"SSE: f{origin}")
            elif details:
                transfer_details = details.get("file_transfer_data")
                if len(transfer_details) == 0:
                    continue

                message_detail = details.get('message_detail')
                LogService.print(f"SSE: message {message_detail}")
                
                # Check for blocked status
                if status_code in ['1051', '1053']:
                    fetched_block_status = seiMemberSetting.select(db, data_query={'memberID': message_detail.get('iMemberID'),
                                                                                    'programID': message_detail.get('iProgramID'),
                                                                                    'code': 'block_status'})
                    if len(fetched_block_status) > 0:
                        if fetched_block_status[0].get('cValue') == "Y":
                            continue
                
                relevant_status_code = {'1051': '51', '1052': '52', '1053': '53'}
                # convert the status code
                data['TSStatusCode'] = relevant_status_code.get(status_code) if status_code in ('1051', '1052', '1053') else status_code

                details = details.get('data')[0]
                transfer_details = transfer_details[0]
                current_time = datetime.now()
                YYYYMMDD = datetime.strftime(current_time.date(),'%Y%m%d')
                HHmmSS = datetime.strftime(current_time,'%H%M%S')
                uuu = datetime.strftime(current_time,'%f')
                message_log_detail = {}                     
                file_name = transfer_details.get('cFilenameformat').replace("{{YYYYMMDD}}",YYYYMMDD).replace("{{HHmmSS}}",HHmmSS).replace("{{uuu}}",uuu)
                file_name = file_name if "trans_shipment" in file_name else file_name.replace("shipment", "trans_shipment")
                file_format = transfer_details.get('cMessageformat')
                member_receiver = details.get('cCompanycode')
                member_program_id = message_detail.get("iProgramID")
                file_dest = transfer_details.get("cDestination").replace("shipment", "trans_shipment")
                file_transfer_type = transfer_details.get('cTransfertype')
                # append member log details
                job.ts_member_log_details.append({"sender": "WorldWideAlliance", "receiver": member_receiver,
                                                    "file_name": file_name, "file_format": file_format,
                                                    "program_id": member_program_id, "file_dest": file_dest,
                                                    "customerAlias": place.get('CustomerAlias'),
                                                    "file_transfer_type": file_transfer_type, "file_type": "TS"})
                if file_format.lower() == 'xml':
                    Envelope={}
                    Envelope['SenderID'] ='WorldWideAlliance'
                    Envelope['ReceiverID'] = re.sub('\s+','',details.get('cCompanycode'))
                    Envelope['Password'] = 'XXXXXXXXXXXXX'
                    Envelope['Type'] = 'transshipment_shipment_status'
                    Envelope['Version'] = '1.0.0'
                    Envelope['EnvelopeID'] = '1554268802467'
                    data_detail = {'Envelope': Envelope,'TSStatusDetails': data}
                    message_log_detail['cFilename'] = file_name
                    message_log_detail['iMemberID'] = message_detail.get('iMemberID')
                    message_log_detail['iProgramID'] = message_detail.get('iProgramID')
                    message_log_detail['cStatuscode'] = data.get('TSStatusCode')
                    message_log_detail['cExternalStatusCode'] = data.get('TSStatusCode')
                    message_log_detail['iItemID'] = data.get('WWAShipmentReference')
                    XMLCreator.create(element={'data': data_detail, 'transfer': file_name,
                                               'message_log_detail': message_log_detail}, schema_type="TS")


    @staticmethod
    def trans_customer_data(db, job:AppJob, element):
        """use case of this function is to check the customer subscription based on status and construct the data based on customer structure for Transhipment status"""
        for place in element:
            data = place.get('trans_shipment_status_details')
            cust_alias =  place.get('CustomerAlias')
            stat_code = data.get('TSStatusCode')
            cust_detail = CustomerDetails.fetch(db, job, data_query={'CustomerAlias':cust_alias,'StatusCode':stat_code})
            if len(cust_detail) == 0 or 'message' in cust_detail.keys():
                LogService.print(f"SSE: customer {cust_alias} was not subscribed on this status_code {stat_code}")
                continue
            elif cust_detail:
                if cust_detail.get('cCompanycode')!="edi_knmanifest_prod" and int(cust_detail.get('StatusCode')) in [1068,1067,1069]:
                    continue
                transfer_details = cust_detail.get('file_transfer_data')[0]
                current_time = datetime.now()
                message_log_detail={}
                YYYYMMDD = datetime.strftime(current_time.date(),'%Y%m%d')
                HHmmSS = datetime.strftime(current_time,'%H%M%S')
                uuu = datetime.strftime(current_time,'%f')
                file_name = transfer_details.get('cFilenameformat').replace("{{YYYYMMDD}}",YYYYMMDD).replace("{{HHmmSS}}",HHmmSS).replace("{{uuu}}",uuu)
                file_name = file_name if "trans_shipment" in file_name else file_name.replace("shipment", "trans_shipment")
                file_format = transfer_details.get('cMessageformat')     
                customer_receiver = cust_detail.get('cCompanycode')
                customer_program_id = cust_detail.get("iProgramID")
                file_dest = transfer_details.get("cDestination")
                file_transfer_type = transfer_details.get('cTransfertype')
                # append customer log details
                job.ts_customer_log_details.append({"sender": "WorldWideAlliance", "receiver": customer_receiver,
                                                    "file_name": file_name, "file_format": file_format,
                                                    "program_id": customer_program_id, "file_dest": file_dest,
                                                    "customerAlias": cust_alias,
                                                    "file_transfer_type": file_transfer_type, "file_type": "TS"})       
                if file_format.lower()=='xml':
                    Envelope={}
                    Envelope['SenderID'] ='WorldWideAlliance'
                    Envelope['ReceiverID'] = re.sub('\s+','',cust_detail.get('cCompanycode'))
                    Envelope['Password'] = 'XXXXXXXXXXXXX'
                    Envelope['Type'] = 'transshipment_shipment_status'
                    Envelope['Version'] = '1.0.0'
                    Envelope['EnvelopeID'] = '1554268802467'
                    data_detail = {'Envelope': Envelope, 'TSStatusDetails': data}
                    message_log_detail['cFilename'] = file_name
                    message_log_detail['iMemberID'] = cust_detail.get('iMemberID')
                    message_log_detail['iProgramID'] = cust_detail.get('iProgramID')
                    message_log_detail['cStatuscode'] = stat_code
                    message_log_detail['cExternalStatusCode'] = cust_detail.get('StatusCode')
                    message_log_detail['iItemID'] = data.get('WWAShipmentReference')
                    XMLCreator.create(element={'data': data_detail, 'transfer': file_name,
                                               'message_log_detail': message_log_detail}, schema_type="TS")
