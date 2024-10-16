from framework.SSE.core.AppDatabase import AppDatabase


class weiFileLogNew:
    @staticmethod
    def insert(db:AppDatabase, data_query=None, values=()):
        """ Insert data into File logs when the file is sent """
        columns = """(`cFileName`, `cFilePath`, `iProgramID`, `cErrorMessage`, `cSender`, `cReceiver`,
                      `cCustomeralias`, `tFileDateTime`, `tStartDateTime`, `tEndDateTime`, `tEntered`)"""
        last_row_id = db.master()._insert_id_safe(f"""INSERT INTO wei_File_Log_new {columns} VALUES
                                                      (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                                      tuple(values))
        return last_row_id