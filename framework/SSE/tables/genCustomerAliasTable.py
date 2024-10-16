from framework.SSE.core.AppDatabase import AppDatabase


class genCustomerAlias:
    @staticmethod
    def fetch(db:AppDatabase, data_query=None):
        # fetching the records for TS export format or sequnce_schema
        get_export_format = """select sms.cValue from gen_Customer_alias as gca inner join
                               sei_Member_setting as sms on sms.iMemberID=gca.iMemberID and sms.cCode=%s where
                               gca.cAliascode=%s;"""
        values = (data_query.get('cCode'), data_query.get('CustomerAlias'))
        response = db.master().select_all_safe(query=get_export_format, values=values, rowDict=True)
        return response