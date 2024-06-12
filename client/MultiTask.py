from threading import Thread
from tkinter import Frame, Label, Button
import io
import tkinter as tk
from threading import Thread, Event
from PIL import Image, ImageTk
import keyboard
import struct
global key
from crypto import *

BUFSIZ = 1024
w = 1280
h = 720
KEY = b""
NONCE = b"\0" * 16

class Control(Frame):
    def __init__(self, parent, client_socket, screen_connect, key_connect, mouse_connect, password):
        global KEY
        KEY = password.encode() + b"\0" * (16 - len(password.encode()))
        self.parent = parent
        Frame.__init__(self, self.parent)
        self.configure(
            bg='black',
            height=720,
            width=1280,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )
        self.parent.geometry("1280x720")
        self.grid(row=0, column=0, sticky="nsew")

        
        self.stop_event = Event()
        self.disconnect_event = Event()
        self.window = parent

        self.status = True
        self.mouse_status = True
        self.screen_status = True
        self.key_status = True

        self.mainConnect = client_socket
        self.screenConnect = screen_connect
        self.keyConnect = key_connect
        self.mouseConnect = mouse_connect

        self.label = Label(self, bg='black')
        self.label.place(x=0, y=0)

        self.checkThread = Thread(target=self.CheckStop)
        self.screenThread = Thread(target=self.LiveScreen)
        self.keyThread = Thread(target=self.KeyControl)
        self.mouseThread = Thread(target=self.MouseControl)

        self.checkThread.start()
        self.screenThread.start()
        self.keyThread.start()
        self.mouseThread.start()

        self.info = Button(self, text = 'PRESS ESC TO BACK', width = 20, height = 5,
            borderwidth=0,
            highlightthickness=0,
            fg = 'dodgerblue', bg = '#363636', font=("Inria Sans", 16),
            relief="flat"
            )
        self.info.place(
            x=500,
            y=680,
            width=300,
            height=20
        )

    def CheckStop(self):
        while True:
            try:
                event=keyboard.read_event().name

                if event != 'esc':
                    self.mainConnect.sendall("CONTINUE".encode())
                else:
                    self.mainConnect.sendall("STOP".encode())
                    self.disconnect_event.set()
                    self.parent.geometry("480x140")

                    self.status = False
                    self.screen_status = False
                    self.key_status = False
                    self.mouse_status = False

                    self.screenThread.join()
                    self.keyThread.join()
                    self.mouseThread.join()

                    self.screenConnect.close()
                    self.keyConnect.close()
                    self.mouseConnect.close()

                    self.destroy()
            except:
                exit()

        
    def LiveScreen(self):
        while self.screen_status:
            length_bytes = self.screenConnect.recv(4)
            length_ints = int.from_bytes(length_bytes, "big")

            enc_image_byte_array = b""
            while len(enc_image_byte_array) < length_ints:
                enc_buffer = self.screenConnect.recv(BUFSIZ) # Enc
                if not enc_buffer:
                    break
                enc_image_byte_array += enc_buffer

            image_byte_array = ascon_decrypt(key = KEY, nonce = NONCE, ciphertext=enc_image_byte_array, associateddata=b"")
            image_byte_io = io.BytesIO(image_byte_array)
            image = Image.open(image_byte_io).resize((w - 60, h - 60))
            photo = ImageTk.PhotoImage(image)

            self.label.configure(image=photo)
            self.label.image = photo

            if self.screen_status:
                self.screenConnect.sendall("CONTINUE".encode())
            else:
                self.screenConnect.sendall("STOP".encode())
                break

    def KeyControl(self):
        while self.key_status:
            event = keyboard.read_event()
            key = event.name
            key_event = event.event_type
            if key == "esc" and key_event == "down":

                self.keyConnect.sendall(struct.pack('!I', len(key)))
                self.keyConnect.send(key.encode())

                self.keyConnect.sendall(struct.pack('!I', len(key_event)))
                self.keyConnect.send(key_event.encode())

                print(f"Pressed {key} {key_event}")
                return
            else:
            
                self.keyConnect.sendall(struct.pack('!I', len(key)))
                self.keyConnect.send(key.encode())

                self.keyConnect.sendall(struct.pack('!I', len(key_event)))
                self.keyConnect.send(key_event.encode())
        
        
    def MouseControl(self):
        #Lắng nghe chuột
        if self.mouse_status:
            self.window.bind("<Motion>", self.move)
            self.window.bind("<Button-1>", self.clickLeft)
            self.window.bind("<Button-3>", self.clickRight)
            self.window.bind("<MouseWheel>", self.scroll)
        else:
            self.window.unbind("<Motion>")
            self.window.unbind("<Button-1>")
            self.window.unbind("<Button-3>")
            self.window.unbind("<MouseWheel>")
            self.mouseConnect.sendall("STOP".encode())
            
        #self.mouse_status = False
        
    def clickLeft(self, event):
        #Nhấn bên trái
        if(event.x>=0&event.x<=w-60&event.y>=0&event.y<=h-60 and self.mouse_status):
            x = int(event.x*1920/(w-60))
            y = int(event.y*1080/(h-60))
            buffer = f"clickLeft,{x},{y}"
            self.mouseConnect.sendall(buffer.encode())
            buffer = self.mouseConnect.recv(BUFSIZ).decode()
            buffer =""
    def clickRight(self, event):
        #Nhấn bên phải
        if(event.x>=0 and event.x<=w-60 and event.y>=0 and event.y<=h-60 and self.mouse_status):
            x = int(event.x*1920/(w-60))
            y = int(event.y*1080/(h-60))
            buffer = f"clickRight,{x},{y}"
            self.mouseConnect.sendall(buffer.encode())
            buffer = self.mouseConnect.recv(BUFSIZ).decode()
            buffer =""
    def move(self, event):
        #Di chuyển chuột
        if(event.x>=0 and event.x<=w-60 and event.y>=0 and event.y<=h-60 and self.mouse_status):
            x = int(event.x*1920/(w-60))
            y = int(event.y*1080/(h-60))
            buffer = f"move,{x},{y}"
            self.mouseConnect.sendall(buffer.encode())
            buffer = self.mouseConnect.recv(BUFSIZ).decode()
            buffer =""
    def scroll(self, event):
        #Cuộn chuột
        if(event.x>=0 and event.x<=w-60 and event.y>=0 and event.y<=h-60 and self.mouse_status):
            x = event.delta
            y = 0
            buffer = f"scroll,{x},{y}"
            self.mouseConnect.sendall(buffer.encode())
            buffer = self.mouseConnect.recv(BUFSIZ).decode()
            buffer =""