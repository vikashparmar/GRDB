from framework.SSE.core.AppDatabase import AppDatabase
from framework.SSE.job.AppJob import AppJob
from framework.system.LogService import LogService


class CustomerDetails:
    @staticmethod
    def fetch(db:AppDatabase, job:AppJob, data_query=None):
        try:
            gen_cust_query = """select * from gen_Customer_alias where cAliascode = %s;"""
            values = (str(data_query.get('CustomerAlias')),)
            LogService.print(f"SSE: {gen_cust_query}")
            gen_cust_data = db.master().select_all_safe(query=gen_cust_query, values=values, rowDict=True)
            if len(gen_cust_data) > 0:
                member_id = gen_cust_data[0]['iMemberID']
            else:
                LogService.print(f"SSE: customer {data_query.get('CustomerAlias')} not registered to wwa member ")
            
            member_query = """select * from sei_Member where iMemberID = %s;"""
            values = (str(member_id),)
            LogService.print(f"SSE: member query {member_query}")
            gen_mem_data = db.master().select_all_safe(query=member_query, values=values, rowDict=True)
            LogService.print(f"SSE: {gen_mem_data}")
            if len(gen_mem_data) > 0:
                member_name = gen_mem_data[0]['cCompanycode']
            else:
                LogService.print(f"SSE: customer {data_query.get('CustomerAlias')} not registered to wwa member ")
                return gen_mem_data
            
            customer_query = """select * from sei_Status_map where iMemberID = %s and iInternalstatuscode = %s and
                                iProgramID = %s;"""
            values = (str(member_id), str(data_query['StatusCode']), str(job.program_id))
            LogService.print(f"SSE: customer_query{customer_query}")
            data = db.master().select_all_safe(query=customer_query, values=values, rowDict=True)
            LogService.print(f"SSE: {data} cust data")
            if len(data) == 0:
                LogService.print(f"SSE: customer {data_query.get('CustomerAlias')} was not subscribed with status {data_query.get('Status')}")
                return data
            else:
                external_code = data[0]['cExternalstatuscode']
                file_transfer_query = """SELECT b.cTransfertype, a.cMessageformat, a.cFilenameformat,
                                         a.cCompressiontype, a.cDestination, a.cAckfilenameformat,
                                         a.cAckdestination, b.cUsername, b.cPassword,b.cServer,b.cPort
                                         FROM sei_Member_transfer_program_link a, sei_Member_transfer b WHERE
                                         a.iMembertransferID = b.iMembertransferID AND a.iStatus >= 0 AND
                                         b.iStatus >= 0 AND iProgramID = %s AND iMemberID = %s;"""
                values = (str(job.program_id), str(member_id))
                file_transfer_data = db.master().select_all_safe(query=file_transfer_query, values=values, rowDict=True)
                if len(file_transfer_data) == 0:
                    LogService.print(f"SSE: customer {data_query.get('CustomerAlias')} was not subscribed with status {data_query.get('Status')} not having filename")
                    return ({"message": "e.args"})
                
                return {"cCompanycode": member_name, "StatusCode": external_code,
                        "file_transfer_data": file_transfer_data, "iProgramID": job.program_id,
                        "iMemberID": member_id}
        except Exception as e:
            LogService.print(f"SSE: exception raised {e.args}")
            return ({"message": e.args})