from framework.SSE.core.AppDatabase import AppDatabase


class weiExportMessageLog:
    @staticmethod
    def select(db:AppDatabase, data_query=None, shipment_ids=None):
        """ Check the entry, does file exists or not (for Shipment Status Module or Trans Shipment Status Module) """
        if data_query and data_query.get('queryType') == "SS":
            query = f"""select iShipmentdetailID from wei_Export_message_log where
                        iShipmentdetailID in {tuple(shipment_ids)};"""
        else:
            query = f"""select iShipmentdetailID from wei_Export_message_log where
                        iShipmentdetailID in {tuple(shipment_ids)} and cStatusCode in ('51', '52', '53');"""
        
        data = db.master().select_all_safe(query=query, values=(), rowDict=True)
        return data
    
    @staticmethod
    def insert(db:AppDatabase, data_query=None, values=()):
        """ Insert data when the file is sent """
        columns = """(`iShipmentdetailID`, `iProgramID`, `cStatuscode`, `cCarrierSCAC`, `cFilename`, `tSent`)"""
        db.master()._insert_id_safe(f"""INSERT INTO wei_Export_message_log {columns} VALUES
                                        (%s, %s, %s, %s, %s, %s);""", tuple(values))