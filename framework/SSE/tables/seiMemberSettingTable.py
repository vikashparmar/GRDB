from framework.SSE.core.AppDatabase import AppDatabase


class seiMemberSetting:    
    @staticmethod
    def select(db:AppDatabase, data_query=None):
        if data_query and data_query.get('code'):
            query = """select cValue, cExtendedcode from sei_Member_setting where iMemberID=%s and iProgramID=%s
                        and cCode=%s"""
            values = (data_query.get('memberID'), data_query.get('programID'), data_query.get('code'))
            response_data = db.master().select_all_safe(query=query, values=values, rowDict=True)
            return response_data
        else:
            query = """select cCode, cValue from sei_Member_setting where iMemberID=%s and iProgramID=%s;"""
            values = (data_query.get('memberID'), data_query.get('programID'))
            response_data = db.master().select_all_safe(query=query, values=values, rowDict=True)
            return response_data