import os, time
from datetime import datetime

class X12Creator:
    @staticmethod
    def create(param_data):
        data = param_data.get('data')
        shipment_details = data.get('ShipmentStatusDetails')
        message_log_details = param_data.get('message_log_detail')
        
        # ISA
        sender_id = data.get('Envelope').get('SenderID')
        receiver_id = data.get('Envelope').get('ReceiverID')

        current_datetime = datetime.now()
        current_date = datetime.strftime(current_datetime, "%y%m%d")
        full_date = datetime.strftime(current_datetime, "%Y%m%d")
        current_time = datetime.strftime(current_datetime, "%H%M")

        interchange_control_number = str(int(time.time()))[-9:]  # It's number of seconds since the epoch (since 1 Jan, 1970)
        indicator = 'T' if os.environ.get('ENV') == "dev" else 'P'
        transaction_set_control_no = '0001'

        # B4
        status_code = message_log_details.get('cExternalStatusCode')  # External status code
        status_location_code = shipment_details.get('StatusLocationCode')
        status_location_code = '' if status_location_code is None else status_location_code
        container_number = shipment_details.get('ContainerNumber')
        equipment_initials = container_number[0:4] if len(container_number) >= 4 else ''

        if message_log_details.get('EquipmentNoCheckDigit') == "Y":
            equipment_no = container_number[4:6] if len(container_number) > 4 else ''
            equipment_no_check_digit = container_number[-1] if len(container_number) >= 10 else ''
        else:
            equipment_no = container_number[4] if len(container_number) > 4 else ''
            equipment_no_check_digit = ''

        container_code = '' if shipment_details.get('ContainerCode') is None else shipment_details.get('ContainerCode')
        status_location_code_alias = 'UN' if status_location_code != "" else ''

        # N9BN
        booking_number = shipment_details.get('BookingNumber')
        booking_number = '' if booking_number is None else booking_number

        # N9SI
        shipper_reference = shipment_details.get('ShipperReference')
        shipper_reference = '' if shipper_reference is None else shipper_reference

        # N94F
        cucc_code = message_log_details.get('CuccCode')

        # N9FN
        forwarder_reference = shipment_details.get('ForwarderReference')
        forwarder_reference = '' if forwarder_reference is None else forwarder_reference

        # Q2
        country_code = status_location_code[0:2] if status_location_code != '' else ''
        routing_details = shipment_details.get('RoutingDetails')
        loading_date = routing_details.get('ETSPortOfLoading').replace('-', '')
        ets_port_of_loading = loading_date if loading_date != "00000000" else ''

        discharge_date = routing_details.get('ETAPortOfDischarge').replace('-', '')
        eta_port_of_discharge = discharge_date if discharge_date != "00000000" else ''

        carrier_scac = '' if shipment_details.get('CarrierSCAC') is None else shipment_details.get('CarrierSCAC')
        carrier_scac = '' if message_log_details.get('CarrieSCAC315') else carrier_scac
        carrier_scac_alias = "SCA" if carrier_scac != "" else ''

        ocean_vessel = '' if shipment_details.get('OceanVessel') is None else shipment_details.get('OceanVessel')
        if message_log_details.get('TrimSegment') == "Y":
            ocean_vessel = ocean_vessel[0:28] if len(ocean_vessel) > 28 else ocean_vessel

        # R4R
        place_of_receipt_code = routing_details.get('PlaceOfReceipt')
        place_of_receipt_code = '' if place_of_receipt_code is None else place_of_receipt_code
        place_of_receipt_city_name = message_log_details.get('PlaceOfReceiptCityName')
        place_of_receipt_code_alias = place_of_receipt_code[0:2] if place_of_receipt_code != "" else ''

        # R4L
        port_of_loading_code = routing_details.get('PortOfLoading')
        port_of_loading_code = '' if port_of_loading_code is None else port_of_loading_code
        port_of_loading_city_name = message_log_details.get('PortOfLoadingCityName')
        port_of_loading_code_alias = port_of_loading_code[0:2] if port_of_loading_code != "" else ''

        # R4D
        port_of_discharge_code = routing_details.get('PortOfDischarge')
        port_of_discharge_code = '' if port_of_discharge_code is None else port_of_discharge_code
        port_of_discharge_city_name = message_log_details.get('PortOfDischargeCityName')
        port_of_discharge_code_alias = port_of_discharge_code[0:2] if port_of_discharge_code != "" else ''

        # R4E
        place_of_delivery_code = routing_details.get('PlaceOfDelivery')
        place_of_delivery_code = '' if place_of_delivery_code is None else place_of_delivery_code
        place_of_delivery_city_name = message_log_details.get('PlaceOfDeliveryCityName')
        place_of_delivery_code_alias = place_of_delivery_code[0:2] if place_of_delivery_code != "" else ''

        element_seperator = message_log_details.get('ElementSeperator')
        element_seperator = "*" if element_seperator == "" else element_seperator
        file_content = []
        elements_list = []

        # ISA
        elem_of_line = ['ISA', '00', ' ' * 10, '00', ' ' * 10, 'ZZ', sender_id + ' ' * 12, 'ZZ', receiver_id + ' ' * 11,
                        current_date, current_time, 'U', '00401', interchange_control_number, '0', indicator, '>']
        elements_list.append(elem_of_line)

        # GS
        elem_of_line = ['GS', 'QO', sender_id, receiver_id, full_date, current_time, '1', 'X', '004010']
        elements_list.append(elem_of_line)

        # ST
        elem_of_line = ['ST', '315', transaction_set_control_no]
        elements_list.append(elem_of_line)

        # B4
        elem_of_line = ['B4', '', '', status_code, full_date, current_time, status_location_code, equipment_initials,
                        equipment_no, 'L', container_code, status_location_code, status_location_code_alias,
                        equipment_no_check_digit]
        elements_list.append(elem_of_line)

        # N9CA
        if message_log_details.get('N9CA'):
            elem_of_line = ['N9', 'CA', carrier_scac, '']
            elements_list.append(elem_of_line)

        # N9BN
        elem_of_line = ['N9', 'BN', booking_number, '']
        elements_list.append(elem_of_line)

        # N9SI
        elem_of_line = ['N9', 'SI', shipper_reference, '']
        elements_list.append(elem_of_line)

        # N94F
        elem_of_line = ['N9', '4F', cucc_code, '']
        elements_list.append(elem_of_line)

        # N9FN
        elem_of_line = ['N9', 'FN', forwarder_reference, '']
        elements_list.append(elem_of_line)

        # Q2
        elem_of_line = ['Q2', '', country_code, '', ets_port_of_loading, eta_port_of_discharge, '', '', '', '',
                        carrier_scac_alias, carrier_scac, 'L', ocean_vessel, '', '', '']
        elements_list.append(elem_of_line)

        # R4R
        elem_of_line = ['R4', 'R', 'UN', place_of_receipt_code, place_of_receipt_city_name,
                        place_of_receipt_code_alias, '', '', '']
        elements_list.append(elem_of_line)

        # DTM
        elem_of_line = ['DTM', '140', '', '0000', 'LT']
        elements_list.append(elem_of_line)

        # R4L
        elem_of_line = ['R4', 'L', 'UN', port_of_loading_code, port_of_loading_city_name,
                        port_of_loading_code_alias, '', '', '']
        elements_list.append(elem_of_line)

        # DTM
        elem_of_line = ['DTM', '140', '', '0000', 'LT']
        elements_list.append(elem_of_line)

        # R4D
        elem_of_line = ['R4', 'D', 'UN', port_of_discharge_code, port_of_discharge_city_name,
                        port_of_discharge_code_alias, '', '', '']
        elements_list.append(elem_of_line)

        # DTM
        elem_of_line = ['DTM', '140', '', '0000', 'LT']
        elements_list.append(elem_of_line)

        # R4E
        elem_of_line = ['R4', 'E', 'UN', place_of_delivery_code, place_of_delivery_city_name,
                        place_of_delivery_code_alias, '', '', '']
        elements_list.append(elem_of_line)

        # DTM
        elem_of_line = ['DTM', '140', '', '0000', 'LT']
        elements_list.append(elem_of_line)

        # SE
        elem_of_line = ['SE', '16', transaction_set_control_no]
        elements_list.append(elem_of_line)

        # GE
        elem_of_line = ['GE', '1', '1']
        elements_list.append(elem_of_line)

        # IEA
        elem_of_line = ['IEA', '1', interchange_control_number]
        elements_list.append(elem_of_line)

        # joining the line elements with the element seperator
        for item in elements_list:
            line = element_seperator.join(item)
            file_content.append(line)

        file_name = param_data.get('message_log_detail').get('cFilename')

        # creating the X12 file
        with open("framework/SSE/files_generated/" + file_name, 'w') as wf:
            for item in file_content:
                wf.write(item + "\n")