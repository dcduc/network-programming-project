from customtkinter import *

def login():
    print("Login")

def register():
    print("Register")

def LoginRegisterUI(client_socket, root):
    window = CTkToplevel(root)
    window.geometry("700x300")
    window.configure()
    window.title("Login/Register")

    # Login UI
    login_label = CTkLabel(window, text="Login", font=("Inria Sans Bold", 24), width=50, text_color="#FFFFFF", )
    login_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

    id_label = CTkLabel(window, text="ID:", anchor="e", font=("Inria Sans", 16), width=30, height=2, )
    id_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)
    id_entry = CTkEntry(window, width=200, font=("Inria Sans", 12), placeholder_text="Enter ID...")
    id_entry.grid(row=1, column=1, padx=10)

    password_label = CTkLabel(window, text="Password:", anchor="e", font=("Inria Sans", 16), width=30, height=2, )
    password_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
    pass_entry = CTkEntry(window, show="*", width=200, font=("Inria Sans", 12), placeholder_text="Enter password...", )
    pass_entry.grid(row=2, column=1, padx=10)

    login_button = CTkButton(window, text="Login", width=30, font=("Inria Sans", 16), corner_radius=15, fg_color="#8AFF6C", text_color="#123456", )
    login_button.grid(row=4, column=0, columnspan=2, pady=20)

    # Register UI
    register_label = CTkLabel(window, text="Register", font=("Inria Sans Bold", 24), width=50, text_color="#FFFFFF", )
    register_label.grid(row=0, column=2, columnspan=2, pady=10, padx=10)

    id_label = CTkLabel(window, text="ID:", anchor="e", font=("Inria Sans", 16), width=30, height=2, )
    id_label.grid(row=1, column=2, sticky="w", padx=10, pady=10)
    id_entry = CTkEntry(window, width=200, font=("Inria Sans", 12), placeholder_text="Enter ID...")
    id_entry.grid(row=1, column=3, padx=10)

    password_label = CTkLabel(window, text="Password:", anchor="e", font=("Inria Sans", 16), width=30, height=2, )
    password_label.grid(row=2, column=2, sticky="w", padx=10, pady=10)
    pass_entry = CTkEntry(window, show="*", width=200, font=("Inria Sans", 12), placeholder_text="Enter password...", )
    pass_entry.grid(row=2, column=3, padx=10)

    confirm_password_label = CTkLabel(window, text="Confirm Password:", anchor="e", font=("Inria Sans", 16), width=30, height=2, )
    confirm_password_label.grid(row=3, column=2, sticky="w", padx=10, pady=10)
    confirm_pass_entry = CTkEntry(window, show="*", width=200, font=("Inria Sans", 12), placeholder_text="Enter password...", )
    confirm_pass_entry.grid(row=3, column=3, padx=10)

    register_button = CTkButton(window, text="Register", width=30, font=("Inria Sans", 16), corner_radius=15, fg_color="#8AFF6C", text_color="#123456", )
    register_button.grid(row=4, column=2, columnspan=2, pady=20)

    window.mainloop()
