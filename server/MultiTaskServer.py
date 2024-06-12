import pyautogui
from threading import Thread, Event
import io
from crypto import *
import struct

BUFFERSIZE=1024
KEY = b""
NONCE = b"\0" * 16

def controlled(main_connect, screen_connect, key_connect, mouse_connect, password):

    global stop_event
    global KEY
    KEY = password.encode() + b"\0" * (16 - len(password.encode()))

    stop_event = Event()
    
    checkThread = Thread(target = CheckStop, args=(main_connect,))
    checkThread.start()
    
    screenThread = Thread(target = send_img, args=(screen_connect,))
    screenThread.start()
        
    #Tương tự dành cho bàn phím
    keyThread = Thread(target = KeyControlled, args=(key_connect,))
    keyThread.start()
        
    mouseThread = Thread(target = MouseControlled, args=(mouse_connect,))
    mouseThread.start()
    
    screenThread.join()
    keyThread.join()
    mouseThread.join()
    
    stop_event.clear()
    

def CheckStop(main_connect):
    while not stop_event.is_set():
        flag = main_connect.recv(BUFFERSIZE).decode()
        if "STOP" in flag:
            stop_event.set()

def send_img(screen_connect):
    while not stop_event.is_set():
        image = pyautogui.screenshot()
        image_byte_array = io.BytesIO()
        image.save(image_byte_array, format='JPEG')
        image_byte_array = image_byte_array.getvalue()

        screen_connect.sendall(len(image_byte_array).to_bytes(4))
        encrypted_image_byte_array = ascon_encrypt(key = KEY, nonce = NONCE, plaintext=image_byte_array)
        screen_connect.sendall(encrypted_image_byte_array)
         
        status = screen_connect.recv(BUFFERSIZE).decode()
        if "STOP" in status:
            break   

def KeyControlled(key_connect):
    while True:
        data1 = key_connect.recv(4)
        size_of_key = struct.unpack('!I', data1)[0]
        key = key_connect.recv(size_of_key).decode()

        data2 = key_connect.recv(4)
        size_of_key_event = struct.unpack('!I', data2)[0]
        key_event = key_connect.recv(size_of_key_event).decode()
        print(f"Da nhan phim {key} {key_event}")

        # Kiểm tra nếu phím Esc được nhấn thì thoát khỏi vòng lặp
        if key == "esc" and key_event == "down":
            return
        elif key_event == "down":
            pyautogui.keyDown(key)
        elif key_event == "up":
            pyautogui.keyUp(key)
       

def MouseControlled(mouse_connect):
    while not stop_event.is_set():
        #Nhận dữ liệu chuột
        buffer = mouse_connect.recv(BUFFERSIZE).decode()
        
        if "STOP" in buffer:
            break   
        
        if not buffer:
            break
        
        task, x, y = buffer.split(",")
        
        #Nếu lệnh là nhấp trái
        if task == "clickLeft":
            try:
                x, y = int(x), int(y)
                pyautogui.click(x, y, button='left')
            except ValueError:
                print("Invalid clickLeft task:", buffer)

        #Nếu lệnh là nhấp phải
        if task == "clickRight":
            try:
                x, y = int(x), int(y)
                pyautogui.click(x, y, button='right')
            except ValueError:
                print("Invalid clickRight task:", buffer)
        #Nếu lệnh là di chuyển
        if task == "move":
            try:
                x, y = int(x), int(y)
                pyautogui.moveTo(x, y)
            except ValueError:
                print("Invalid move task:", buffer)
        #Nếu lệnh là cuộn
        if task == "scroll":
            x, y = int(x), int(y)
            print("Scroll ",x,y)
            pyautogui.scroll(x)
        mouse_connect.sendall(buffer.encode())
        #Dọn buffer
        buffer=""