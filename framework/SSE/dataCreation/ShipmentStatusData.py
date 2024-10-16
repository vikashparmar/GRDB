from datetime import datetime
from framework.SSE.job.AppJob import AppJob
from framework.SSE.tables.genCustomerAliasTable import genCustomerAlias


class ShipmentStatusData:
    @staticmethod
    def create(db, job:AppJob, data):
        customer_alias = data.get('CustomerAlias')
        # fetch the 'sequence_schema' is required or not
        get_data = genCustomerAlias.fetch(db, data_query={'cCode': 'sequence_schema', 'CustomerAlias': customer_alias})
        schema_tags_details = job.shipment_status_detail
        schema_type = "default"
        if len(get_data) > 0:
            if get_data[0].get('cValue').lower() == "y":
                schema_tags_details = job.sequence_schema_detail
                schema_type = "sequence_schema"
            else:
                pass
        else:
            pass

        job.sse_shipment_id_list.add(data.get('ShipmentdetailID'))
        ShipmentStatusDetails = {key:data[key] if key in data.keys() else '' for key in schema_tags_details}
        ShipmentStatusDetails['OfficeCode'] = data.get('BkngOfficeCode')

        try:
            cutoff_receiving_wh = datetime.strftime(data.get('CutoffReceivingWarehouse'),'%Y-%m-%d') if data.get('CutoffReceivingWarehouse') is not None else ''
            place_of_receipt_date = datetime.strftime(data.get('ETSPlaceOfReceipt'),'%Y-%m-%d') if data.get('ETSPlaceOfReceipt') is not None else ''
            port_of_loading_date = datetime.strftime(data.get('ETSPortOfLoading'),'%Y-%m-%d') if data.get('ETSPortOfLoading') is not None else ''
            port_of_discharge_date = datetime.strftime(data.get('ETAPortOfDischarge'),'%Y-%m-%d') if data.get('ETAPortOfDischarge') is not None else ''
            place_of_delivery_date = datetime.strftime(data.get('ETAPlaceOfDelivery'),'%Y-%m-%d') if data.get('ETAPlaceOfDelivery') is not None else ''

            ShipmentStatusDetails['RoutingDetails'] = {'ReceivingWarehouse': data.get('ReceivingWarehouse'), 'CutoffReceivingWarehouse': cutoff_receiving_wh,
                                                        'PlaceOfReceipt': data.get('PlaceOfReceipt'), 'ETSPlaceOfReceipt': place_of_receipt_date,
                                                        'PortOfLoading': data.get('PortOfLoading'), 'ETSPortOfLoading': port_of_loading_date,
                                                        'PortOfDischarge': data.get('PortOfDischarge'), 'ETAPortOfDischarge': port_of_discharge_date,
                                                        'PlaceOfDelivery': data.get('PlaceOfDelivery'), 'ETAPlaceOfDelivery': place_of_delivery_date}
        except:
            cutoff_receiving_wh = data.get('CutoffReceivingWarehouse')[0:10] if isinstance(data.get('CutoffReceivingWarehouse'), str) else ''
            place_of_receipt_date = data.get('ETSPlaceOfReceipt')[0:10] if isinstance(data.get('ETSPlaceOfReceipt'), str) else ''
            port_of_loading_date = data.get('ETSPortOfLoading')[0:10] if isinstance(data.get('ETSPortOfLoading'), str) else ''
            port_of_discharge_date = data.get('ETAPortOfDischarge')[0:10] if isinstance(data.get('ETAPortOfDischarge'), str) else ''
            place_of_delivery_date = data.get('ETAPlaceOfDelivery')[0:10] if isinstance(data.get('ETAPlaceOfDelivery'), str) else ''

            ShipmentStatusDetails['RoutingDetails'] = {'ReceivingWarehouse': data.get('ReceivingWarehouse'), 'CutoffReceivingWarehouse': cutoff_receiving_wh,
                                                        'PlaceOfReceipt': data.get('PlaceOfReceipt'), 'ETSPlaceOfReceipt': place_of_receipt_date,
                                                        'PortOfLoading': data.get('PortOfLoading'), 'ETSPortOfLoading': port_of_loading_date,
                                                        'PortOfDischarge': data.get('PortOfDischarge'), 'ETAPortOfDischarge': port_of_discharge_date,
                                                        'PlaceOfDelivery': data.get('PlaceOfDelivery'), 'ETAPlaceOfDelivery': place_of_delivery_date}

        
        StatusDateTimeDetails = {}

        StatusDateTimeDetails['Date'] = datetime.strftime(data.get('StatusDateTime').date(),'%Y-%m-%d')
        StatusDateTimeDetails['Time'] = str(data.get('StatusDateTime').time())
        StatusDateTimeDetails['TimeZone'] = 'GMT'

        ShipmentStatusDetails['StatusDateTimeDetails'] = StatusDateTimeDetails
        ShipmentStatusDetails['CargoDetails'] = {key:data[key] if key in data.keys() else ''  for key in job.cargo_details}

        if data.get('HazardousFlag') == "Y":
            ShipmentStatusDetails['CargoDetails']['HazardousDetails'] = {key:data[key] if key in data.keys() else ''  for key in job.hazardous_details}

        ShipmentStatusDetails['DocumentationDetails'] = {key:data[key] if key in data.keys() else ''  for key in job.documentation_details}
        return {'ShipmentStatusDetails':ShipmentStatusDetails, 'SchemaType': schema_type, 'BillOfLadingNumber': data.get('HouseBillOfLadingNumber')}
