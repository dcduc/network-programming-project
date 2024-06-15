from customtkinter import *


class HomescreenUI(CTkFrame):
    def __init__(self, parent):
        self.parent = parent
        CTkFrame.__init__(self, self.parent)
        self.configure(height=500, width=1300)
        self.parent.geometry("480x230")
        self.grid(row=0, column=0, sticky="nsew")

        self.button_file_control = CTkButton(
            self,
            text="File Control",
            width=120,
            height=80,
            font=("Inria Sans", 16),
            corner_radius=15,
            fg_color="#B010FF",
        )
        self.button_file_control.place(x=20, y=25)

        self.button_start = CTkButton(
            self,
            text="Start",
            width=120,
            height=80,
            font=("Inria Sans", 16),
            corner_radius=15,
            fg_color="#10B0FF",
        )
        self.button_start.place(x=160, y=25)

        self.button_disconnect = CTkButton(
            self,
            text="Disconnect",
            width=120,
            height=80,
            font=("Inria Sans", 16),
            corner_radius=15,
            fg_color="#FF2E2E",
        )
        self.button_disconnect.place(x=300, y=25)

        self.button_screenshot = CTkButton(
            self,
            text="Screenshot",
            width=120,
            height=80,
            font=("Inria Sans", 16),
            corner_radius=15,
            fg_color="#FFD700",
        )
        self.button_screenshot.place(x=20, y=125)

        self.button_shutdown = CTkButton(
            self,
            text="Shutdown",
            width=120,
            height=80,
            font=("Inria Sans", 16),
            corner_radius=15,
            fg_color="#FF4500",
        )
        self.button_shutdown.place(x=160, y=125)
