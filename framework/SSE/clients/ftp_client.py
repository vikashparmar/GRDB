import ftplib


class FTPClient:
    @staticmethod
    def send(receiver_alias, filename):
        FTP_HOST = "ftp.dlptest.com"
        FTP_USER = "dlpuser@dlptest.com"
        FTP_PASS = "SzMf7rTE4pCrf9dV286GuNe4N"

        # connect to the FTP server
        ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
        # force UTF-8 encoding
        ftp.encoding = "utf-8"

        source_dir = "/home/" + receiver_alias + "/download/"

        # change the directory
        ftp.cwd(source_dir)

        # local file name you want to upload
        with open(filename, "rb") as file:
            # use FTP's STOR command to upload the file
            ftp.storbinary(f"STOR {filename}", file)

        # quit and close the connection
        ftp.quit()
