from framework.SSE.core.AppDatabase import AppDatabase


class fileBLDetail:
    @staticmethod
    def select(db:AppDatabase, data_query=None):
        values = (data_query.get('LadingNumber'),)
        response_data = db.master().select_all_safe("""select cMasterTrackingNumber from file_BL_detail where
                                                       cBillOfLadingNumber=%s;""", values=values, rowDict=True)
        return response_data