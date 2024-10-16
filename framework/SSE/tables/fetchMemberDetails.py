from framework.SSE.core.AppDatabase import AppDatabase
from framework.system.LogService import LogService
from framework.SSE.job.AppJob import AppJob


class MemberDetails:
    @staticmethod
    def fetch(db:AppDatabase, job:AppJob, data_query=None):
        values = (data_query['origin'],data_query['destination'])
        LogService.print(f"SSE: calling stored procedure for member origin and destination {'CALL getMemberID(%s,%s,@a,@b)', values}")
        sp_query = "CALL getMemberID(%s,%s,@a,@b)"
        db.master().batch_execute(query=sp_query, value=values)
        select_origin_procedure = """select @a,@b"""
        orig_dest = db.master().select_all_safe(query=select_origin_procedure, values=(), rowDict=True)[0]
        if int(data_query['StatusCode']) <= 50:
             member_data = """select * from sei_Member where iMemberID = %s;"""
             values = (str(orig_dest['@b']),)
             LogService.print(f"SSE: getting memeber detail query {member_data}")
             data = db.master().select_all_safe(query=member_data, values=values, rowDict=True)

             if len(data) != 0:
                 file_transfer_query = """SELECT b.cTransfertype,a.cMessageformat,a.cFilenameformat,
                                          a.cCompressiontype, a.cDestination, a.cAckfilenameformat,
                                          a.cAckdestination, b.cUsername, b.cPassword,b.cServer,b.cPort
                                          FROM sei_Member_transfer_program_link a, sei_Member_transfer b WHERE
                                          a.iMembertransferID =  b.iMembertransferID AND a.iStatus >= 0 AND
                                          b.iStatus >= 0 AND iProgramID = %s AND iMemberID = %s;"""
                 values = (str(job.program_id), str(orig_dest['@b']))
                 file_transfer_data = db.master().select_all_safe(query=file_transfer_query, values=values, rowDict=True)
                 LogService.print(f"SSE: file_transfer_query {file_transfer_query}")
                 message_detail = {"iMemberID": orig_dest['@b'], "iProgramID": job.program_id}
                 return {"data": data, "file_transfer_data": file_transfer_data, "message_detail": message_detail}
             return data
        elif int(data_query['StatusCode']) > 50:
            member_data = "select * from sei_Member where iMemberID = %s;"
            values = (str(orig_dest['@a']),)
            LogService.print(f"SSE: getting memeber detail query{member_data}")
            data = db.master().select_all_safe(query=member_data, values=values, rowDict=True)

            if len(data) != 0:
                 file_transfer_query ="""SELECT b.cTransfertype,a.cMessageformat,a.cFilenameformat,
                                         a.cCompressiontype, a.cDestination, a.cAckfilenameformat,
                                         a.cAckdestination, b.cUsername, b.cPassword,b.cServer,b.cPort
                                         FROM sei_Member_transfer_program_link a, sei_Member_transfer b WHERE
                                         a.iMembertransferID =  b.iMembertransferID AND a.iStatus >= 0 AND
                                         b.iStatus >= 0 AND iProgramID = %s AND iMemberID = %s;"""
                 values = (str(job.program_id), str(orig_dest['@a']))
                 file_transfer_data = db.master().select_all_safe(query=file_transfer_query, values=values, rowDict=True)
                 LogService.print(f"SSE: file_transfer_query {file_transfer_query}")
                 message_detail = {"iMemberID": orig_dest['@a'], "iProgramID": job.program_id}
                 LogService.print(f"SSE: {file_transfer_data}")
                 return {"data": data, "file_transfer_data": file_transfer_data, "message_detail": message_detail}
            return data