import struct
from PIL import Image


def recv_screenshot(client_socket):
    size_data = client_socket.recv(4)
    with open('screenshot.png', 'wb') as image:
        image.write(size_data)
    size = struct.unpack('!I', size_data)[0]
    image_data = b''
    chunk_size = 1024

    # Chia nhỏ data để gửi
    while len(image_data) < size:
        chunk = client_socket.recv(min(chunk_size,size-len(image_data)))
        if not chunk:
            break
        image_data += chunk
    
    with open('screenshot.png', 'wb') as image:
        image.write(image_data)
    image = Image.open('screenshot.png')
    image.show()