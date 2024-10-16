from framework.SSE.core.AppDatabase import AppDatabase


class weiFileMetaDataLog:
    @staticmethod
    def insert(db:AppDatabase, data_query=None, values=()):
        """ Insert data into File Meta Data logs when the file is sent """
        columns = """(`iFileLogID`, `cReferencetype`, `cReference`, `iStatus`, `tEntered`)"""
        db.master()._insert_id_safe(f"""INSERT INTO wei_File_Meta_Data_Log {columns} VALUES
                                        (%s, %s, %s, %s, %s)""", tuple(values))