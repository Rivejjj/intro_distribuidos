import sys
import os
import time
import hashlib
import random
from lib.message import *
from lib.command_options import Options

TIMEOUT = 0.2 # A definir
PACKAGE_TIMEOUT = 1 # A definir
MAX_ATTEMPTS = 10

def send_file(options: Options, seq_num, addr):
    file_size = os.path.getsize(options.src)
    if file_size > MAX_FILE_SIZE:
        print("Invalid file size")
        return
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    file = open(options.src, "rb")
    sock.bind(addr)

    read = file.read(PAYLOAD_SIZE)
    sock.settimeout(TIMEOUT) #p ver este valor
    send_attempts = 0
    #iterar sobre read para leer todo el archivo
    while (read != b'') and (send_attempts < MAX_ATTEMPTS):
        message = Message.make(options.type, options.name, file_size, len(read), seq_num, read)
        print(message)
        
        if random.random() > 0.8:
            message.header.seq_num = 1000
            print(" corrompiendo un paquete")

        message.send_to(sock, (options.host, options.port))
        send_attempts +=1
        sent = time.time()
        while time.time() - sent < PACKAGE_TIMEOUT:
            msg, addr = Message.recv_from(sock)
            if Error.is_error(msg):
                continue
            
            if (msg.header.type == Type.Ack) and (msg.header.seq_num == seq_num):
                send_attempts = 0
                seq_num += 1
                read = file.read(PAYLOAD_SIZE)
                print("received_ack")
                break

    sock.close()
        # wait_for_ack() #si estamos en stop & wait
        
def receive_file(options: Options):
    print("hola")


# def handle_msg( : Message):
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