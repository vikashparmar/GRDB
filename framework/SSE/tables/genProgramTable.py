from framework.SSI.core.AppDatabase import AppDatabase
from framework.SSE.job.AppJob import AppJob


class genProgram:
    @staticmethod
    def select(db:AppDatabase, job:AppJob):
        job.program_id = db.master().select_all_safe(query="SELECT iProgramID FROM gen_Program WHERE cCode=%s", values=('SSE',), rowDict=True)[0]['iProgramID']