from framework.SSE.core.AppDatabase import AppDatabase


class genLocation:
    @staticmethod
    def select(db:AppDatabase, data_query=None):
        get_city_query = f"""SELECT cCode, cCityname FROM gen_Location WHERE cCode in {data_query.get('values')} AND
                             cActive = 'Y' AND cOceanlocation = 'Y' AND iStatus >= 0;"""
        response_data = db.master().select_all_safe(query=get_city_query, values=(), rowDict=True)
        return response_data