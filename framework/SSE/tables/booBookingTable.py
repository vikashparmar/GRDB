from framework.SSE.core.AppDatabase import AppDatabase


class booBooking:
    @staticmethod
    def select(db:AppDatabase, data_query=None):
        values = (data_query.get('WWAShipmentReference'), )
        booking_data = db.master().select_all_safe("""select iEnteredby from boo_Booking where iStatus=0 and
                                                      cWWAreference=%s and cBookingType='M';""",
                                                      values=values, rowDict=True)

        if len(booking_data) > 0:
            user_id = booking_data[0].get('iEnteredby')
            response_data = db.master().select_all_safe("""select iMemberID, cCompanycode from sei_Member
                                                           where iUserID=%s;""", values=(user_id,), rowDict=True)
            return response_data
        return []