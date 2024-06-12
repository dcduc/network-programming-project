from customtkinter import *
import database


class LoginRegister(CTkFrame):
    def __init__(self, parent):
        self.parent = parent
        CTkFrame.__init__(self, self.parent)
        self.configure(height=300, width=700)
        self.parent.geometry("700x300")
        self.grid(row=0, column=0, sticky="nsew")

        # Database
        f, self.socket_db = database.connect(
            b"dcduc",
            b"CongDuc_1608",
            "dcduc.mysql.database.azure.com",
            3306,
            b"remote_desktop_app",
        )
        if f < 0:
            print("Authentication failed!")

        # Login UI
        self.login_label = CTkLabel(
            self,
            text="Login",
            font=("Inria Sans Bold", 24),
            width=50,
            text_color="#FFFFFF",
        )
        self.login_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

        self.id_label = CTkLabel(
            self,
            text="ID:",
            anchor="e",
            font=("Inria Sans", 16),
            width=30,
            height=2,
        )
        self.id_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.id_entry = CTkEntry(
            self, width=200, font=("Inria Sans", 12), placeholder_text="Enter ID..."
        )
        self.id_entry.grid(row=1, column=1, padx=10)

        self.password_label = CTkLabel(
            self,
            text="Password:",
            anchor="e",
            font=("Inria Sans", 16),
            width=30,
            height=2,
        )
        self.password_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.pass_entry = CTkEntry(
            self,
            show="*",
            width=200,
            font=("Inria Sans", 12),
            placeholder_text="Enter password...",
        )
        self.pass_entry.grid(row=2, column=1, padx=10)

        self.login_button = CTkButton(
            self,
            text="Login",
            width=30,
            font=("Inria Sans", 16),
            corner_radius=15,
            fg_color="#8AFF6C",
            text_color="#123456",
            command=self.login(),
        )
        self.login_button.grid(row=4, column=0, columnspan=2, pady=20)

        # Register UI
        self.register_label = CTkLabel(
            self,
            text="Register",
            font=("Inria Sans Bold", 24),
            width=50,
            text_color="#FFFFFF",
        )
        self.register_label.grid(row=0, column=2, columnspan=2, pady=10, padx=10)

        self.id_label2 = CTkLabel(
            self,
            text="ID:",
            anchor="e",
            font=("Inria Sans", 16),
            width=30,
            height=2,
        )
        self.id_label2.grid(row=1, column=2, sticky="w", padx=10, pady=10)

        self.id_entry2 = CTkEntry(
            self, width=200, font=("Inria Sans", 12), placeholder_text="Enter ID..."
        )
        self.id_entry2.grid(row=1, column=3, padx=10)

        self.password_label2 = CTkLabel(
            self,
            text="Password:",
            anchor="e",
            font=("Inria Sans", 16),
            width=30,
            height=2,
        )
        self.password_label2.grid(row=2, column=2, sticky="w", padx=10, pady=10)
        self.pass_entry2 = CTkEntry(
            self,
            show="*",
            width=200,
            font=("Inria Sans", 12),
            placeholder_text="Enter password...",
        )
        self.pass_entry2.grid(row=2, column=3, padx=10)

        self.confirm_password_label = CTkLabel(
            self,
            text="Confirm Password:",
            anchor="e",
            font=("Inria Sans", 16),
            width=30,
            height=2,
        )
        self.confirm_password_label.grid(row=3, column=2, sticky="w", padx=10, pady=10)
        self.confirm_pass_entry = CTkEntry(
            self,
            show="*",
            width=200,
            font=("Inria Sans", 12),
            placeholder_text="Enter password...",
        )
        self.confirm_pass_entry.grid(row=3, column=3, padx=10)

        self.register_button = CTkButton(
            self,
            text="Register",
            width=30,
            font=("Inria Sans", 16),
            corner_radius=15,
            fg_color="#8AFF6C",
            text_color="#123456",
            command=self.register(),
        )
        self.register_button.grid(row=4, column=2, columnspan=2, pady=20)
        

    def login(self):
        ID, passwd = self.id_entry.get(), self.pass_entry.get()
        # Truy vấn
        self.client_id = database.execute_command(
            f"SELECT id FROM remote_desktop_app.clients WHERE username = '{ID}' AND password = '{passwd}'".encode(),
            self.socket_db,
        )


    def register(self):
        ID, passwd = self.id_entry2.get(), self.pass_entry2.get()
        assert passwd == self.confirm_pass_entry.get(), "Password not match"
        # Truy vấn
        database.execute_command(
            f"INSERT INTO remote_desktop_app.clients (username, password) VALUES ('{ID}', '{passwd}')".encode(),
            self.socket_db,
        )


    # def get_client_id(self):
    #     return self.client_id
