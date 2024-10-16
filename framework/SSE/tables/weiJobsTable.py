from framework.SSE.core.AppDatabase import AppDatabase
from framework.SSE.job.AppJob import AppJob


class weiJobs:
    @staticmethod
    def insert(db:AppDatabase, data_query=None, values=()):
        """ Insert data into Jobs logs when the file is sent """
        columns = """(`cFileName`, `cFilePath`, `iProgramID`, `cFileFormat`, `cFileType`, `cCurrentStatus`,
                      `cErrorMessage`, `cSender`, `cReceiver`, `tStartTime`, `tEndTime`, `iStatus`)"""
        last_row_id = db.master()._insert_id_safe(f"""INSERT INTO wei_Jobs {columns} VALUES
                                                      (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                                      tuple(values))
        return last_row_id
    
    @staticmethod
    def update(db:AppDatabase, job:AppJob, data_query=None):
        """ Update data into Jobs logs """
        job.iJobID = data_query.get("logID")
        current_status = data_query.get("currentStatus")
        log_sent_time = data_query.get("sentTime")

        db.master().update_record("wei_Jobs", "iJobID", job.iJobID, {
            'cCurrentStatus': current_status,
            'cErrorMessage': '',
            'tFileDate': log_sent_time,
            'iStatus': 1
        })