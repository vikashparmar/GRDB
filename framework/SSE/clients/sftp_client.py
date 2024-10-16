import paramiko


class SFTPClient:
    @staticmethod
    def send(receiver_alias, filename):
        # Open a transport
        host, port = "xyz.com", 00
        transport = paramiko.Transport((host,port))

        # User authorization    
        username, password = "user", "pass"
        transport.connect(None, username, password)

        # Open a sftp
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Send the file
        filepath = "/home/"+ receiver_alias +"/download/" + filename
        localpath = filename
        sftp.put(localpath, filepath)

        # Close the sftp
        if sftp:
            sftp.close()

        # Close the transport
        if transport:
            transport.close()
