import os

BUFFSIZE = 1024 * 4
def shutdown(server_socket):
    while(True):
        message = server_socket.recv(BUFFSIZE).decode("utf8")
        if "SHUTDOWN" in message:
            os.system('shutdown -s -t 15')
        else:
            return