from datetime import datetime
from framework.SSE.job.AppJob import AppJob


class LinkDelinkData:
    @staticmethod
    def create(job:AppJob, data):
        customer_alias = data.get('CustomerAlias')
        link_details = {key:data[key] if key in data.keys() else '' for key in job.link_delink_detail}
        link_details['PreviousBillOfLadingNumber'] = data.get('PrevHBL')
        schema_type = "link_delink"
        job.sse_shipment_id_list.add(data.get('ShipmentdetailID'))

        cutoff_receiving_wh = datetime.strftime(data.get('CutoffReceivingWarehouse'),'%Y-%m-%d') if data.get('CutoffReceivingWarehouse') is not None else ''
        place_of_receipt_date = datetime.strftime(data.get('ETSPlaceOfReceipt'),'%Y-%m-%d') if data.get('ETSPlaceOfReceipt') is not None else ''
        port_of_loading_date = datetime.strftime(data.get('ETSPortOfLoading'),'%Y-%m-%d') if data.get('ETSPortOfLoading') is not None else ''
        port_of_discharge_date = datetime.strftime(data.get('ETAPortOfDischarge'),'%Y-%m-%d') if data.get('ETAPortOfDischarge') is not None else ''
        place_of_delivery_date = datetime.strftime(data.get('ETAPlaceOfDelivery'),'%Y-%m-%d') if data.get('ETAPlaceOfDelivery') is not None else ''

        link_details['RoutingDetails'] = {'ReceivingWarehouse': data.get('ReceivingWarehouse'), 'CutoffReceivingWarehouse': cutoff_receiving_wh,
                                        'PlaceOfReceipt': data.get('PlaceOfReceipt'), 'ETSPlaceOfReceipt': place_of_receipt_date,
                                        'PortOfLoading': data.get('PortOfLoading'), 'ETSPortOfLoading': port_of_loading_date,
                                        'PortOfDischarge': data.get('PortOfDischarge'), 'ETAPortOfDischarge': port_of_discharge_date,
                                        'PlaceOfDelivery': data.get('PlaceOfDelivery'), 'ETAPlaceOfDelivery': place_of_delivery_date}
        
        StatusDateTimeDetails = {}

        StatusDateTimeDetails['Date'] = datetime.strftime(data.get('StatusDateTime').date(),'%Y-%m-%d')
        StatusDateTimeDetails['Time'] = str(data.get('StatusDateTime').time())
        StatusDateTimeDetails['TimeZone'] = 'GMT'

        link_details['StatusDateTimeDetails'] = StatusDateTimeDetails
        link_details['CargoDetails'] = {key:data[key] if key in data.keys() else ''  for key in job.cargo_details}

        if data.get('HazardousFlag') == "Y":
            link_details['CargoDetails']['HazardousDetails'] = {key:data[key] if key in data.keys() else ''  for key in job.hazardous_details}

        link_details['DocumentationDetails'] = {key:data[key] if key in data.keys() else ''  for key in job.documentation_details}

        return {'ShipmentStatusDetails': link_details, 'SchemaType': schema_type}