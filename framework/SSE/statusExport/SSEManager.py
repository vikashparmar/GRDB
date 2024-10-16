from datetime import datetime
from framework.SSE.core.AppDatabase import AppDatabase
from framework.SSE.job.AppJob import AppJob
from framework.system.LogService import LogService
from framework.SSE.fileTransfer.SendFile import SendFile
from framework.SSE.statusExport.SSEUtility import Utility
from framework.SSE.tables.fetchShipmentStatusDetails import SSDetails
from framework.SSE.tables.genProgramTable import genProgram


class SSEManager:
    @staticmethod
    def export():
        try:
            LogService.print("SSE: creating db instance")
            db = AppDatabase()
            job = AppJob()
            LogService.print("SSE: db connection established")

            # Shipment Status
            START_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # this is to maintain the start time for Job started
            genProgram.select(db, job)
            shp_details = SSDetails.fetch(db)
            if len(shp_details) == 0:
                LogService.print(f"SSE: don't have any records from last 20 minutes")
                return False
            LogService.print("SSE: fetched the details from db from status_details table")
            data = [Utility.data_create(db, job, element) for element in shp_details]
            LogService.print("SSE: created the schema structure ")

            # Here seperate the data list for Shipment status & Transshipment status
            ts_data = []  # transshipment status data
            ss_data = []  # shipment status data
            for item in data:
                if item.get('ShipmentStatusDetails'):
                    ss_data.append(item)
                else:
                    ts_data.append(item)

            # create the shipment status file
            if len(ss_data) > 0:
                Utility.member_data(db, job, ss_data)
                Utility.customer_data(db, job, ss_data)
                SendFile.send(db, job, shp_details, module_type="SS", start_time=START_TIME)

            # create the trans shipment status file
            if len(ts_data) > 0:
                Utility.trans_member_data(db, job, ts_data)
                Utility.trans_customer_data(db, job, ts_data)
                SendFile.send(db, job, shp_details, module_type="TS", start_time=START_TIME)

            # del db
        except Exception as e:
            LogService.print(f"SSE: exception  occured{str(e)}")


if __name__ == '__main__':
    SSEManager.export()
