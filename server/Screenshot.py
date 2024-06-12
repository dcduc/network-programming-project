import pyautogui
import struct

def send_screenshot(client_socket):
    screenshot = pyautogui.screenshot()
    screenshot.save("myscreenshot.png")
    with open('myscreenshot.png', 'rb') as image:
        data = image.read()
    # Send the length of the data first
    client_socket.sendall(struct.pack('!I', len(data)))
    # Send data 
    chunk_size = 1024
    for i in range(0, len(data), chunk_size):
        client_socket.send(data[i:i + min(chunk_size,len(data)-i)])