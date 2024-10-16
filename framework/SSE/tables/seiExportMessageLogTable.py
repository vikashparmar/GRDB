from datetime import datetime
from framework.SSI.core.AppDatabase import AppDatabase
from framework.system.LogService import LogService


class seiExportMessageLogTable:
    @staticmethod
    # def message_log(db:AppDatabase, self, data_query=None):
    def insert_or_select(db:AppDatabase, self, data_query=None):
        if data_query['insert'] == True:
            times = datetime.strftime((datetime.now()),"%Y-%m-%d %H:%M:%S")
            columns = """(`iMemberID`, `iItemID`, `cReference`, `iProgramID`, `cStatuscode`, `cExternalStatusCode`,
                          `tSent`, `cFilename`, `iEnteredby`, `tEntered`, `tUpdated`, `iUpdatedby`, `iStatus`)"""
            values = (data_query['iMemberID'], int(data_query['iItemID']), '', data_query['iProgramID'],
                      int(data_query['cStatuscode']), data_query['cExternalStatusCode'], times,
                      data_query['cFilename'], 0, times, '0000-00-00 00:00:00', 0, 0)

            db.master()._insert_id_safe(f"""INSERT INTO sei_Export_message_log {columns} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", values)
            LogService.print(f"SSE: Record inserted successfully in sei_Export_message_log")
        else:
            query = """SELECT count(1) as count from sei_Export_message_log where iItemID = %s AND
                       iMemberID = %s AND cStatuscode = %s;"""
            values = (str(data_query['iItemID']), str(data_query['iMemberID']), str(data_query['cStatuscode']))
            data = db.master().select_all_safe(query=query, values=values, rowDict=True)
            if len(data) != 0:
                return data[0]