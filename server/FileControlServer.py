import pickle
import os
import time
from crypto import *

BUFSIZ = 1024 * 4
SEPARATOR = "<SEPARATOR>"

def showTree(server_socket):
    ListDirectoryTree = []
    for c in range(ord('A'), ord('Z') + 1):
        path = chr(c) + ":\\"
        if os.path.isdir(path):
            ListDirectoryTree.append(path)
    data = pickle.dumps(ListDirectoryTree)
    print(str(len(data)))
    server_socket.sendall(str(len(data)).encode())
    time.sleep(0.2)
    server_socket.sendall(data)

def sendListDirs(server_socket):
    path = server_socket.recv(BUFSIZ).decode()
    if not os.path.isdir(path):
        return [False, path]
    try:
        listTree = []
        ListDirectoryTree = os.listdir(path)
        for d in ListDirectoryTree:
            listTree.append((d, os.path.isdir(path + "\\" + d)))
        data = pickle.dumps(listTree)
        server_socket.sendall(str(len(data)).encode())
        temp = server_socket.recv(BUFSIZ)
        server_socket.sendall(data)
        return [True, path]
    except:
        server_socket.sendall("error".encode())
        return [False, "error"]    

def deleteFile(server_socket):
    file_name = server_socket.recv(BUFSIZ).decode()
    if os.path.exists(file_name):
        try:
            os.remove(file_name)
            server_socket.sendall("deleted".encode())
        except:
            server_socket.sendall("error".encode())
            return
    else:
        server_socket.sendall("error".encode())
        return

def getFileFromClient(server_socket, KEY):
    received = server_socket.recv(BUFSIZ).decode()
    if (received == "-1"):
        server_socket.sendall("-1".encode())
        return
    filename, filesize, path = received.split(SEPARATOR)
    filename = os.path.basename(filename)
    filesize = int(filesize)
    server_socket.sendall("server was received filename".encode())
    enc_data = b""
    while len(enc_data) < filesize:
        enc_packet = server_socket.recv(999999)
        enc_data += enc_packet
    if (enc_data == "-1"):
        server_socket.sendall("-1".encode())
        return
    try:
        with open(path + filename, "wb") as file:
            data = ascon_decrypt(key = KEY, nonce = b"\0"*16, ciphertext=enc_data, associateddata=b"")
            file.write(data)
        server_socket.sendall("server was received content of file".encode())
    except:
        server_socket.sendall("-1".encode())
    
def sendFileToClient(server_socket, KEY):
    filename = server_socket.recv(BUFSIZ).decode()
    if filename == "-1" or not os.path.isfile(filename):
        server_socket.sendall("-1".encode())
        return
    filesize = os.path.getsize(filename)
    server_socket.sendall(str(filesize).encode())
    temp = server_socket.recv(BUFSIZ)
    with open(filename, "rb") as f:
        data = f.read()
        enc_data = ascon_encrypt(key = KEY, nonce = b"\0"*16, plaintext=data, associateddata=b"")
        server_socket.sendall(enc_data)

def file_control(client_socket, password):
    isMod = False
    KEY = password.encode() + b"\0" * (16 - len(password.encode()))
    while True:
        if not isMod:
            mod = client_socket.recv(BUFSIZ).decode()

        if (mod == "SHOW"):
            showTree(client_socket)
            while True:
                check = sendListDirs(client_socket)
                if not check[0]:    
                    mod = check[1]
                    if (mod != "error"):
                        isMod = True
                        break
        
        elif (mod == "SEND"):
            #client.sendall("OK".encode())
            getFileFromClient(client_socket, KEY)
            isMod = False

        # copy file from server to client
        elif (mod == "GET"):
            #client.sendall("OK".encode())
            sendFileToClient(client_socket, KEY)
            isMod = False

        elif (mod == "DELETE"):
            #client.sendall("OK".encode())
            deleteFile(client_socket)
            isMod = False

        elif (mod == "QUIT"):
            return
        
        else:
            client_socket.sendall("-1".encode())
