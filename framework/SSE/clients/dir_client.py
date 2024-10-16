import os


class DIRClient:
    @staticmethod
    def send(receiver_alias, filename):
        # go to the directory
        # os.walk('/home/demo/download/')
        filepath = "/home/"+ receiver_alias +"/download" + filename

        # copy a file
        with open(filename, 'r') as rf:
            with open(filepath, 'w') as wf:
                for line in rf:
                    wf.write(line)
