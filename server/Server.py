from customtkinter import *
import database
import socket
import threading
from FileControlServer import *
from MultiTaskServer import *
from Screenshot import *
from Shutdown import *
import sshtunnel
import psutil
from checkValidPort import get_listening_ports
from genIdPass import genIDPassword
from random import randint
from tkinter import messagebox

BUFSIZ = 1024 * 4
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 8887


def get_wifi_mac_address():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                if (
                    "Wi-Fi" in interface or "wlan" in interface
                ):  # Kiểm tra tên interface phù hợp
                    return addr.address


class ServerApp:
    def __init__(self):
        self.server_socket = None
        self.running = False
        self.key_path = "C:\\Users\\dcduc\\Downloads\\duynv.pem"
        self.localport = 4444
        self.localhost = "127.0.0.1"
        self.remoteport = 4444
        self.remotehost = "172.207.92.76"
        self.user = "nvm"
        self.app = CTk()
        self.app.geometry("300x180")
        self.app.configure()
        self.app.title("Server")
        self.app.resizable(False, False)
        self.id_server, self.passwd_server = genIDPassword()
        self.is_ready = False

        if len(sys.argv) > 1 and sys.argv[1] == "--remote":
            try:
                mac = get_wifi_mac_address()
                listening_ports = get_listening_ports()
                print(mac)
                print(self.id_server, self.passwd_server)
                print(self.localport)
                while True:
                    tmp_port = randint(1024, 65000)
                    if tmp_port not in listening_ports:
                        self.localport = tmp_port
                        self.remoteport = tmp_port
                        break
                f, socket_db = database.connect(
                    b"dcduc",
                    b"CongDuc_1608",
                    "dcduc.mysql.database.azure.com",
                    3306,
                    b"remote_desktop_app",
                )
                if f < 0:
                    print("Authentication failed!")
                mac_exists = database.execute_command(
                    f"select mac_address from remote_desktop_app.servers where mac_address='00:00:00:00:00:01'".encode(),
                    socket_db,
                )
                if not mac_exists:
                    print(mac)
                    print(self.id_server)
                    print(self.passwd_server)
                    print(self.localport)
                    if (
                        type(
                            database.execute_command(
                                f"insert into remote_desktop_app.servers values ('{mac}','{self.id_server}','{self.passwd_server}',{self.localport})".encode(),
                                socket_db,
                            )
                        )
                        == "int"
                    ):
                        self.is_ready = True
                else:
                    try:
                        self.id_server = database.execute_command(
                            f"update remote_desktop_app.servers set password='{self.passwd_server}', port={self.localport}) where mac_address='{mac}'".encode(),
                            socket_db,
                        )
                        self.is_ready = True
                    except Exception as e:
                        print(e)
                        exit()
            except Exception as e:
                print(e)
                exit()
        else:
            self.passwd_server = "0" * 16

        self.create_ui()

    def create_ui(self):
        title_label = CTkLabel(
            self.app,
            text="Server",
            text_color="#FFFFFF",
            font=("Inria Sans", 24),
            width=50,
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        id_label = CTkLabel(
            self.app,
            text=f"ID:",
            anchor="w",
            font=("Inria Sans", 16),
            width=30,
            height=2,
        )
        id_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.id_entry = CTkEntry(
            self.app,
            width=150,
            font=("Inria Sans", 12),
        )
        self.id_entry.grid(row=1, column=1, padx=10)
        self.id_entry.insert(0, self.id_server)

        passwd_label = CTkLabel(
            self.app,
            text=f"Password:",
            anchor="w",
            font=("Inria Sans", 16),
            width=30,
            height=2,
        )
        passwd_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        self.passwd_entry = CTkEntry(
            self.app,
            width=150,
            font=("Inria Sans", 12),
        )
        self.passwd_entry.grid(row=2, column=1, padx=10)
        self.passwd_entry.insert(0, self.passwd_server)

        CTkButton(
            self.app,
            text="Open",
            fg_color="#90FF90",
            height=30,
            width=100,
            font=("Inria Sans", 16),
            corner_radius=15,
            command=self.open_server,
        ).grid(row=3, column=0, padx=10, pady=10)
        CTkButton(
            self.app,
            text="Close",
            fg_color="#FF9090",
            height=30,
            width=100,
            font=("Inria Sans", 16),
            corner_radius=15,
            command=self.close_server,
        ).grid(row=3, column=1, padx=10, pady=10)

    def handle_client(self, client_socket):
        try:
            while True:
                msg = client_socket.recv(BUFSIZ).decode("utf8")
                if not msg:
                    break
                if "MULTI TASK" in msg:
                    self.multi_task(client_socket)
                elif "FILE CONTROL" in msg:
                    file_control(client_socket, self.passwd_server)
                elif "SCREENSHOT" in msg:
                    send_screenshot(client_socket)
                elif "SHUTDOWN" in msg:
                    shutdown(client_socket)
                elif "QUIT" in msg:
                    client_socket.close()
                    exit()
        except:
            client_socket.close()
            exit()

    def multi_task(self, client_socket):
        try:
            screen_con, _ = self.server_socket.accept()
            key_con, _ = self.server_socket.accept()
            mouse_con, _ = self.server_socket.accept()
            controlled(
                client_socket, screen_con, key_con, mouse_con, self.passwd_server
            )
        except:
            screen_con.close()
            key_con.close()
            mouse_con.close()
            client_socket.close()
            exit()

    def open_server(self):
        if len(sys.argv) > 1 and sys.argv[1] == "--remote":
            try:
                # mac = get_wifi_mac_address()
                # id_server, pass_server = genIDPassword()
                # print(id_server, pass_server)

                # self.id_entry.delete(0, END)
                # self.id_entry.insert(0, str(id_server))

                # self.passwd_entry.delete(0, END)
                # self.passwd_entry.insert(0, str(pass_server))

                # listening_ports = get_listening_ports()
                # is_ready = False
                # while True:
                #     tmp_port = randint(1024, 65000)
                #     if tmp_port not in listening_ports:
                #         self.localport = tmp_port
                #         self.remoteport = tmp_port
                #         break
                # f, socket_db = database.connect(b"server", b"server", "dcduc.mysql.database.azure.com", 3306, b"remote_desktop_app")
                # if f < 0:
                #     print("Authentication failed!")
                # mac_exists = database.execute_command(f"select remote_desktop_app.check_exist_mac({mac})".encode(), socket_db)
                # if not mac_exists:
                #     if database.execute_command(f"select remote_desktop_app.insert_server({mac},{self.id_server},{self.passwd_server},{self.localport})".encode(), socket_db):
                #         is_ready = True
                # else:
                #     try:
                #         self.id_server = database.execute_command(f"select remote_desktop_app.update_server({mac},{self.passwd_server},{self.localport})".encode(), socket_db)
                #         is_ready = True
                #     except Exception as e:
                #         print(e)
                #         exit()

                if self.is_ready == True:
                    a = sshtunnel.sshtunnel(
                        self.key_path,
                        self.localport,
                        self.localhost,
                        self.remoteport,
                        self.user,
                        self.remotehost,
                    )
                    b = threading.Thread(target=a.run)
                    b.start()
                    self.server_socket = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM
                    )
                    self.server_socket.bind((self.localhost, self.localport))
                    self.server_socket.listen(5)
                    self.running = True
                    print(
                        f"Server is listening on {self.localhost}:{self.localport}..."
                    )
                    self.accept_clients()
                    # b.join()
            except Exception as e:
                print(e)
                self.server_socket.close()
                self.running = False
                exit()
        else:
            print("Open server")
            try:
                self.passwd_server = "0" * 16
                self.localport = int(input("Enter port: "))
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # self.server_socket.bind((self.localhost, self.localport))
                self.server_socket.bind(("100.117.59.11", self.localport))
                self.server_socket.listen(5)
                self.running = True
                print(f"Server is listening on {self.localhost}:{self.localport}...")
                self.accept_clients()
            except Exception as e:
                print(e)
                self.server_socket.close()
                self.running = False
                exit()

    def accept_clients(self):
        try:
            print("Waiting for connection...")
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection from {client_address} has been established.")

            messagebox.showinfo(
                "Connection", f"Connection from {client_address} has been established."
            )
            self.handle_client(client_socket)
        except:
            self.server_socket.close()
            self.running = False
            exit()

    def close_server(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.app.quit()


if __name__ == "__main__":
    try:
        server = ServerApp()
        server.app.mainloop()
    except:
        exit()
