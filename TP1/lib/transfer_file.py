import sys
import os
from lib.message import *
from lib.command_options import Options

seq_num = 0

def send_file(options: Options):
    file_size = os.path.getsize(options.src)
    if file_size > MAX_FILE_SIZE:
        print("Invalid file size")
        return
    
    file = open(options.src, "rb")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.2", 42069))

    read = file.read(PAYLOAD_SIZE)
    #iterar sobre read para leer todo el archivo
    while read != b'':
        message = Message.new(options.request, options.name, file_size, len(read), seq_num, read)
        print(message)
        message.send_to(sock, (options.host, options.port))
        Message.recv_from(sock)

        # wait_for_ack() #si estamos en stop & wait
        
        read = file.read(PAYLOAD_SIZE)

# def handle_msg(msg: Message):
#     if msg.header.request == Request.Upload:
#         result = store_package_server(msg.header.file_name, msg.payload)
#         if result == -1:
#             print("Filed to store file")
    
#         # EN LUGAR DEL ACK SE MANDA ERROR PA CORTAR LA TRANSMICION
#         return # Y muere hilo de este cliente
#     print(msg)

def store_package(path, data: bytearray):
    print(f"Storing file in {path}")
    with open(path, 'ab') as file:
        file.write(data)

    return 0
