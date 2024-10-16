from framework.SSE.core.AppDatabase import AppDatabase


class genStatus:
    @staticmethod
    def select(db:AppDatabase, data_query=None):
        values = (data_query.get('StatusCode'),)
        response_data = db.master().select_all_safe(query="""SELECT cStatusname FROM gen_Status WHERE
                                                             cStatuscode = %s""", values=values, rowDict=True)
        return response_data