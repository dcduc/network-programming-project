import os
import tkinter as tk
import tkinter.ttk as ttk
import pickle
from tkinter import filedialog, messagebox
from customtkinter import *
import sys
from PIL import Image, ImageTk
from crypto import *

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 

def path(file_name):
    file_name = 'pic\\' + file_name
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, file_name)

def listDirs(client_socket, path):
    client_socket.sendall(path.encode())

    data_size = int(client_socket.recv(BUFFER_SIZE))
    if (data_size == -1):
        messagebox.showerror(message = "Nhấn vào nút SHOW một lần nữa để xem danh sách thư mục!")
        return []
    client_socket.sendall("received filesize".encode())
    data = b""
    while len(data) < data_size:
        packet = client_socket.recv(999999)
        data += packet
    if (data == "error"):
        messagebox.showerror(message = "Không thể mở được thư mục!")
        return []
    
    list_folder_file = pickle.loads(data)
    return list_folder_file

class FileControlUI(CTkFrame):
    def __init__(self, parent, client_socket, password):
        self.KEY = password.encode() + b"\0" * (16 - len(password.encode()))
        self.parent = parent
        CTkFrame.__init__(self, self.parent)

        self.configure(bg_color = "white", height = 720, width = 1280)
        self.parent.geometry("900x500")
        self.grid(row=0, column=0, sticky="nsew")
        
        self.client = client_socket
        self.currPath = " "
        self.nodes = dict()

        self.frame = CTkFrame(self, width=600, height=300)
        self.frame.place(x=100, y=70)

        self.tree = ttk.Treeview(self.frame)
        self.scroll_y = CTkScrollbar(self.frame, orientation='vertical', command=self.tree.yview)
        self.scroll_x = CTkScrollbar(self.frame, orientation='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=self.scroll_y.set, xscroll=self.scroll_x.set)
        self.tree.pack(fill = tk.BOTH, expand = True)

        self.tree.bind('<<TreeviewOpen>>', self.open_node)
        self.tree.bind("<<TreeviewSelect>>", self.select_node)

        self.path = CTkTextbox(self.frame, height = 2, width = 700, state = "disable", activate_scrollbars=True)
        self.path.pack(side = tk.BOTTOM, fill = tk.X)

        self.button_show = CTkButton(self, text = 'SHOW LIST', width = 100, height = 50, corner_radius=15, command=self.showTree, font=("Inria Sans", 16))
        self.button_show.place(x=100,y=350)
        
        self.button_send = CTkButton(self, text = 'SEND FILE', width = 100, height = 50, corner_radius=15, command=self.sendFileToServer, font=("Inria Sans", 16))
        self.button_send.place(x=250,y=350) # Enc
        
        self.button_get = CTkButton(self, text = 'GET FILE', width = 100, height = 50, corner_radius=15, command=self.getFileFromServer, font=("Inria Sans", 16))
        self.button_get.place(x=400,y=350) # Enc

        self.button_delete = CTkButton(self, text = 'DELETE FILE', width = 100, height = 50, corner_radius=15, command=self.deleteFile, font=("Inria Sans", 16))
        self.button_delete.place(x=550,y=350)

        self.button_back = CTkButton(self, text = 'BACK', width = 100, height = 50, corner_radius=15, command=lambda: self.back(), font=("Inria Sans", 16))
        self.button_back.place(x=700,y=350)

    def insert_node(self, parent, text, abspath, isFolder):
        node = self.tree.insert(parent, 'end', text=text, open=False)
        if abspath != "" and isFolder:
            self.nodes[node] = abspath
            self.tree.insert(node, 'end')

    def open_node(self, event):
        node = self.tree.focus()
        abspath = self.nodes.pop(node, None)
        if abspath:
            self.tree.delete(self.tree.get_children(node))
            try:
                dirs = listDirs(self.client, abspath)
                for p in dirs:
                    self.insert_node(node, p[0], os.path.join(abspath, p[0]), p[1])
            except:
                messagebox.showerror(message = "Không thể mở được thư mục này!")

    def select_node(self, event):
        item = self.tree.selection()[0]
        parent = self.tree.parent(item)
        self.currPath = self.tree.item(item,"text")
        while parent:
            self.currPath = os.path.join(self.tree.item(parent)['text'], self.currPath)
            item = parent
            parent = self.tree.parent(item)

        self.path.configure(state = "normal")
        self.path.delete("1.0", tk.END)
        self.path.insert(tk.END, self.currPath)
        self.path.configure(state = "disable")

    def deleteTree(self):
        self.currPath = " "
        self.path.configure(state = "normal")
        self.path.delete("1.0", tk.END)
        self.path.configure(state = "disable")
        for i in self.tree.get_children():
            self.tree.delete(i)

    def showTree(self):
        self.deleteTree()
        self.client.sendall("SHOW".encode())

        data_size = int(self.client.recv(BUFFER_SIZE))
        data = b""
        while len(data) < data_size:
            packet = self.client.recv(999999)
            data += packet
        loaded_list = pickle.loads(data)
        
        for path in loaded_list:
            try:
                abspath = os.path.abspath(path)
                self.insert_node('', abspath, abspath, True)
            except:
                continue

    def sendFileToServer(self):
        if not os.path.isdir(self.currPath):
            messagebox.showinfo(message = "Bạn hãy chọn thư mục bên server để nhận file!")
            return []
        self.client.sendall("SEND".encode())
        filename = filedialog.askopenfilename(title="Select File", filetypes=[("All Files", "*.*")])
        if filename == None or filename == "":
            self.client.sendall("-1".encode())
            temp = self.client.recv(BUFFER_SIZE)
            return 
        destPath = self.currPath + "\\"
        filesize = os.path.getsize(filename)
        self.client.send(f"{filename}{SEPARATOR}{filesize}{SEPARATOR}{destPath}".encode())
        isReceived = self.client.recv(BUFFER_SIZE).decode()
        if (isReceived == "server was received filename"):
            try:
                with open(filename, "rb") as fin:
                    data = fin.read()
                    enc_data = ascon_encrypt(key = self.KEY, nonce = b"\0"*16, plaintext=data, associateddata=b"")
                    self.client.sendall(enc_data)
            except:
                self.client.sendall("-1".encode())
            isReceivedContent = self.client.recv(BUFFER_SIZE).decode()
            if (isReceivedContent == "server was received content of file"):
                messagebox.showinfo(message = "Gửi tệp tin thành công!")
                return True

    def getFileFromServer(self):
        if os.path.isdir(self.currPath):
            messagebox.showinfo(message = "Bạn hãy chọn file muốn lấy của server!")
            return []
        self.client.sendall("GET".encode())
        try:
            destPath = filedialog.askdirectory()
            if destPath == None or destPath == "":
                self.client.sendall("-1".encode())
                temp = self.client.recv(BUFFER_SIZE)
                return 
            self.client.sendall(self.currPath.encode())
            filename = os.path.basename(self.currPath)
            filesize = int(self.client.recv(100))
            if (filesize == -1):
                messagebox.showerror(message = "Không thể lấy tệp tin!")  
                return
            self.client.sendall("received filesize".encode())
            enc_data = b""
            while len(enc_data) < filesize:
                enc_packet = self.client.recv(999999)
                enc_data += enc_packet
            with open(destPath + "\\" + filename, "wb") as f:
                data = ascon_decrypt(key = self.KEY, nonce = b"\0"*16, ciphertext=enc_data, associateddata=b"")
                f.write(data)
            messagebox.showinfo(message = "Lấy tệp tin thành công!")
        except:
            messagebox.showerror(message = "Không thể lấy tệp tin!")  

    def deleteFile(self):
        if os.path.isdir(self.currPath):
            messagebox.showinfo(message = "Bạn hãy chọn file muốn xóa của server!")
            return []
        self.client.sendall("DELETE".encode())
        self.client.sendall(self.currPath.encode())
        res = self.client.recv(BUFFER_SIZE).decode()
        if (res == "deleted"):
            messagebox.showinfo(message = "Xóa tệp tin thành công!")
        else:
            messagebox.showerror(message = "Không thể xóa được tệp tin!") 

    def back(self):
        self.parent.geometry("480x140")
