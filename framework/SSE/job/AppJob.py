class AppJob:
    def __init__(self):
        self.iJobID = None
        self.program_id = None
        self.log_level = None
        self.log_filename = None
        self.log_format = None
        self.trans_ship_statuses = [51, 52, 53]
        self.export_statuses = [10, 11, 12, 20, 30, 40, 50]
        self.import_statuses = [60, 70, 80]
        self.shipment_status_detail = ['ApplicationType', 'TypeOfMove', 'ShipperReference', 'ForwarderReference',
                                       'CustomerReference', 'ConsigneeReference', 'CommunicationReference',
                                       'PickupReference', 'BookingNumber', 'WWAShipmentReference',
                                       'CarrierBookingNumber', 'CarrierBillofLadingNumber', 'FileNumber',
                                       'ContainerNumber', 'ContainerSize', 'ContainerType', 'ContainerCode',
                                       'SealNumber','CarrierSCAC', 'OceanVessel', 'Voyage', 'IMONumber',
                                       'CustomerAlias', 'StatusCode', 'StatusLocationCode', 'StatusLocationName',
                                       'OfficeCode', 'ReleaseType', 'RoutingDetails', 'StatusDateTimeDetails',
                                       'CargoDetails', 'DocumentationDetails']
        self.sequence_schema_detail = ['ApplicationType', 'TypeOfMove', 'ShipperReference', 'ForwarderReference',
                                       'CustomerReference', 'ConsigneeReference', 'CommunicationReference',
                                       'PickupReference', 'BookingNumber', 'WWAShipmentReference',
                                       'CarrierBookingNumber', 'CarrierBillofLadingNumber', 'FileNumber',
                                       'CarrierSCAC', 'ArrivalNoticeNumber', 'ContainerNumber', 'ContainerSize',
                                       'ContainerType', 'ContainerCode', 'SealNumber', 'OceanVessel', 'Voyage',
                                       'IMONumber','CustomerAlias', 'StatusCode', 'StatusLocationCode',
                                       'StatusLocationName', 'OfficeCode', 'ReleaseType', 'RoutingDetails',
                                       'StatusDateTimeDetails', 'CargoDetails', 'DocumentationDetails']
        self.link_delink_detail = ['ApplicationType', 'TypeOfMove', 'ShipperReference', 'ForwarderReference',
                                   'ConsigneeReference', 'CommunicationReference', 'PickupReference', 'BookingNumber',
                                   'WWAShipmentReference', 'CarrierBookingNumber', 'FileNumber', 'LotNumber',
                                   'PreviousBillOfLadingNumber', 'HouseBillOfLadingNumber', 'ReleaseType',
                                   'ContainerNumber', 'ContainerSize', 'ContainerType', 'ContainerCode',
                                   'SealNumber', 'OceanVessel', 'Voyage', 'CustomerAlias', 'InTransitNumber',
                                   'InTransitDate', 'StatusCode', 'StatusLocationCode', 'StatusLocationName',
                                   'RoutingDetails', 'StatusDateTimeDetails', 'CargoDetails', 'DocumentationDetails']
        self.cargo_details = ['Pieces', 'WeightLBS', 'VolumeCBF', 'WeightKG', 'VolumeCBM', 'HazardousFlag']
        self.status_date_time_details = ['Date', 'Time', 'TimeZone']
        self.documentation_details = ['ImageLink', 'Image', 'ContentType']
        self.hazardous_details = ['Pieces','HazWeightLBS','HazVolumeCBF','HazWeightKG','HazVolumeCBM']
        self.block_statuses = [32, 33, 2, 27, 1012, 450]
        self.member_block_statuses = [32, 33, 2, 27, 1012, 450, 1067, 1068, 1069]
        self.ss_member_log_details = []
        self.ss_customer_log_details = []
        self.sse_shipment_id_list = {''}
        self.ts_member_log_details = []
        self.ts_customer_log_details = []
        self.ts_shipment_id_list = {''}
