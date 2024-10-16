from datetime import datetime
from framework.SSE.dataCreation.ShipmentStatusData import ShipmentStatusData
from framework.SSE.job.AppJob import AppJob
from framework.SSE.tables.genCustomerAliasTable import genCustomerAlias
from framework.SSE.tables.traTranshipmerDetailTable import traTranshipmentDetail
from framework.system.LogService import LogService


class TransShipmentData:
    @staticmethod
    def create(db, job:AppJob, trans_dict):
        """ Here we create data according to Trans shipment schema """
        customer_alias = trans_dict.get('CustomerAlias')
        get_data = genCustomerAlias.fetch(db, data_query={'cCode': 'TS_export_format', 'CustomerAlias': customer_alias})

        if len(get_data) > 0:
            if get_data[0].get('cValue').lower() == "y":
                job.ts_shipment_id_list.add(trans_dict.get('ShipmentdetailID'))
                # fetching routing details
                routing_details = traTranshipmentDetail.select(db, data_query={'shipmentId': trans_dict.get('ShipmentdetailID')})

                # for TS(Transshipment Status) format
                trans_shipment_status_details = {'TSReference': '', 'TSContainerNumber': trans_dict.get('ContainerNumber'),
                                                'TSSealNumber': trans_dict.get('SealNumber'), 'TSOceanVessel': trans_dict.get('OceanVessel'),
                                                'TSVoyage': trans_dict.get('Voyage'), 'TSStatusCode': trans_dict.get('StatusCode'),
                                                'TSStatusLocationCode': trans_dict.get('StatusLocationCode'), 'TSStatusLocationName': trans_dict.get('StatusLocationName'),
                                                'TSRoutingDetails': '', 'StatusDateTimeDetails': '', 'CargoDetails': ''}

                lading_number = trans_dict.get('HouseBillOfLadingNumber')
                if lading_number is None:
                    trans_shipment_status_details['TSReference'] = {'TSReferenceTypeDetails': 2, 'TSReferenceNumber': trans_dict.get('BookingNumber')}
                else:
                    trans_shipment_status_details['TSReference'] = {'TSReferenceTypeDetails': 1, 'TSReferenceNumber': lading_number}

                if len(routing_details) > 0:
                    routing_details = routing_details[0]
                    port_of_arrival_time = datetime.strftime(routing_details.get('tPortofarrival'), '%Y-%m-%d') if routing_details.get('tPortofarrival') is not None else ''
                    port_of_loading_time = datetime.strftime(routing_details.get('tPortofloading'), '%Y-%m-%d') if routing_details.get('tPortofloading') is not None else ''
                    port_of_discharge_time = datetime.strftime(routing_details.get('tPortofdischarge'), '%Y-%m-%d') if routing_details.get('tPortofdischarge') is not None else ''

                    trans_shipment_status_details['TSRoutingDetails'] = {'TSCFS': routing_details.get('cPortofarrivalcode'), 'ETATSPortOfArrival': port_of_arrival_time,
                                                                        'TSPortOfLoading': routing_details.get('cPortofloadingcode'), 'ETSTSPortOfLoading': port_of_loading_time,
                                                                        'TSPortOfDischarge': routing_details.get('cPortofdischargecode'), 'ETATSPortOfDischarge': port_of_discharge_time}

                status_date = trans_dict.get('StatusDateTime')
                trans_shipment_status_details['StatusDateTimeDetails'] = {'Date': datetime.strftime(status_date.date(), '%Y-%m-%d'), 'Time': str(status_date.time()), 'TimeZone': 'GMT'}

                trans_shipment_status_details['CargoDetails'] = {key:trans_dict[key] if key in trans_dict.keys() else ''  for key in job.cargo_details}

                if trans_dict.get('HazardousFlag') == "Y":
                    trans_shipment_status_details['CargoDetails']['HazardousDetails'] = {key:trans_dict[key] if key in trans_dict.keys() else ''  for key in job.hazardous_details}

                ts_details = {'trans_shipment_status_details': trans_shipment_status_details, 'CustomerAlias': customer_alias}

                return ts_details
            else:
                job.ts_shipment_id_list.add(trans_dict.get('ShipmentdetailID'))
                # for SS(Shipment Status) format
                schema_data = ShipmentStatusData.ship_status_data_create(db, trans_dict)
                return schema_data
        else:
            LogService.print(f"SSE: No request for specific filetype by Customer {customer_alias}")