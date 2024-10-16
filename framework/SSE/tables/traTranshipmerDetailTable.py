from framework.SSE.core.AppDatabase import AppDatabase


class traTranshipmentDetail:
    @staticmethod
    def select(db:AppDatabase, data_query=None):
        """ Fetching the Trans Shipment Status Routing Details """
        shipment_id = data_query.get('shipmentId')
        fetch_files_query = """select iShipmentID, cPortofloadingcode, cPortofarrivalcode, cPortofdischargecode,
                               tPortofarrival, tPortofloading, tPortofdischarge from tra_Transshipment_detail
                               where iShipmentID = %s;"""
        data = db.master().select_all_safe(query=fetch_files_query, values=(shipment_id,), rowDict=True)
        return data