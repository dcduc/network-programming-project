from customtkinter import *
import socket
from Screenshot import *
from FileControlClient import *
from MultiTask import *
from HomescreenGUI import *
from Shutdown import *
from LoginRegister import *
from PIL import Image, ImageTk
import sys
import database

BUFSIZ = 1024 * 4


class ClientApp:
    def __init__(self):
        self.client_socket = None
        self.host_id = None
        self.host_pass = None
        self.port = None
        self.app = CTk()
        self.app.geometry("300x180")
        self.app.configure()
        self.app.title("Client")
        self.app.resizable(False, False)
        self.main = None
        self.id_entry = None
        self.pass_entry = None
        self.main_hp = None

    def generateMainUI(self):
        title_label = CTkLabel( self.app, text="Client", font=("Inria Sans Bold", 24), width=50, text_color="#FFFFFF", )
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        id_label = CTkLabel( self.app, text="ID:", anchor="e", font=("Inria Sans", 16), width=30, height=2, )
        id_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.id_entry = CTkEntry(self.app, width=200, font=("Inria Sans", 12), placeholder_text="Enter ID...")
        self.id_entry.grid(row=1, column=1, padx=10)

        password_label = CTkLabel( self.app, text="Password:", anchor="e", font=("Inria Sans", 16), width=30, height=2, )
        password_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.pass_entry = CTkEntry( self.app, show="*", width=200, font=("Inria Sans", 12), placeholder_text="Enter password...", )
        self.pass_entry.grid(row=2, column=1, padx=10)

        connect_button = CTkButton( self.app, text="Connect", width=30, font=("Inria Sans", 16), command=self.connect, corner_radius=15, fg_color="#8AFF6C", text_color="#123456", )
        connect_button.grid(row=3, column=0, columnspan=2, pady=20)

    def getInputValue(self):
        return (self.id_entry.get()).strip(), (self.pass_entry.get()).strip()

    def back(self, temp):
        temp.destroy()
        self.main_hp.tkraise()
        self.app.geometry("480x140")
        self.client_socket.sendall(bytes("QUIT", "utf8"))

    def fileControl(self):
        self.client_socket.sendall(bytes("FILE CONTROL", "utf8"))
        temp = FileControlUI(self.app, self.client_socket, self.host_pass)
        temp.button_back.configure(command=lambda: self.back(temp))

    def disconnect(self):
        self.client_socket.sendall(bytes("QUIT", "utf8"))
        self.main_hp.destroy()
        self.app.destroy()
        self.client_socket.close()
        exit()

    def screenshot(self):
        self.client_socket.sendall(bytes("SCREENSHOT", "utf8"))
    
    def shutdown(self):
        self.client_socket.sendall(bytes("SHUTDOWN", "utf8"))
        temp = shutdown_UI(self.client_socket, self.app)
    
    def login_register(self):
        LoginRegisterUI(self.client_socket, self.app)

    def multitask(self):
        try:
            self.client_socket.sendall(bytes("MULTI TASK", "utf8"))
            screen_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            screen_con.connect((self.ip, self.port))
            key_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            key_con.connect((self.ip, self.port))
            mouse_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mouse_con.connect((self.ip, self.port))
            temp = Control(self.app, self.client_socket, screen_con, key_con, mouse_con, self.host_pass)
            temp.info.configure(command=lambda: self.back(temp))
        except:
            messagebox.showerror(message="Kết nối thất bại!")
            if self.client_socket:
                self.client_socket.close()
            exit()

    def showMainUI(self):
        self.main_hp = HomescreenUI(self.app)
        self.main_hp.button_file_control.configure(command=self.fileControl)
        self.main_hp.button_disconnect.configure(command=self.disconnect)
        self.main_hp.button_start.configure(command=self.multitask)
        self.main_hp.button_screenshot.configure(command=self.screenshot)
        self.main_hp.button_shutdown.configure(command=self.shutdown)

    def connect(self):
        if len(sys.argv) > 1:
            try:
                if sys.argv[1] == "--remote":
                    self.host_id, self.host_pass = self.getInputValue()
                    f, socket_db = database.connect(
                        b"client",
                        b"client",
                        "dcduc.mysql.database.azure.com",
                        3306,
                        b"remote_desktop_app",
                    )
                    if f < 0:
                        print("Authentication failed!")
                    self.port = int(
                        database.execute_command(
                            f"select remote_desktop_app.get_port('{self.host_id}','{self.host_pass}')".encode(),
                            socket_db,
                        )
                    )
                    self.ip = "172.207.92.76"
            except ConnectionRefusedError:
                messagebox.showerror(message="Kết nối thất bại!")
                if self.client_socket:
                    self.client_socket.close()
                exit()
            except Exception as e:
                print(e)
                if self.client_socket:
                    self.client_socket.close()
                exit()
        else:
            self.ip, self.port = self.getInputValue()
            self.host_pass = "0" * 16
            self.port = int(self.port)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.ip, self.port)
        self.client_socket.connect(server_address)
        messagebox.showinfo(message="Kết nối thành công!")
        self.showMainUI()
        self.app.mainloop()


if __name__ == "__main__":
    try:
        client = ClientApp()
        client.login_register()
        client.generateMainUI()
        client.app.mainloop()
        client.connect()
    except:
        exit()
