from framework.SSE.core.AppDatabase import AppDatabase


class SSDetails:
    @staticmethod
    def fetch(db:AppDatabase, data_query=None):
        shipment_query = """select  sd.*,sh.* ,li.*,dd.* from track_StatusDetails as sd INNER JOIN
                            track_ShipmentDetails as sh ON sh.cWWAShipmentReference=sd.cWWAShipmentReference
                            INNER JOIN
                            track_LineItems as li ON li.cWWAShipmentReference= sd.cWWAShipmentReference
                            INNER JOIN
                            track_DocumentationDetails as dd ON dd.cWWAShipmentReference=sd.cWWAShipmentReference
                            where sd.iStatus>=0 and sd.tEntered >= date_sub(utc_timestamp(),INTERVAL 40 MINUTE) and
                            sd.cWWAShipmentReference is NOT NULL;"""
        data = db.master().select_all_safe(query=shipment_query, values=(), rowDict=True)
        return data
