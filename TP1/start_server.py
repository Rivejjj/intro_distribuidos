import socket
import os
import time
import random
import heapq
from lib.message import *
from lib.transfer_file import store_package
from lib.errors import Error
from lib.message import Message

UDP_IP = "127.0.0.1"
UDP_PORT = 42069
UP = 0
DOWN = 1
TIMEOUT = 0.2

def store_package_server(file_name, payload):
    print("entra a store package")
    if not os.path.exists('./server_files/'):
        try:
            os.mkdir('./server_files/')
        except OSError: 
            print("fue el OS")
            return -Error.ErrorStoringData
    
    path = './server_files/' + file_name
    return store_package(path, payload)

def serversito():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP,UDP_PORT))
    sock.settimeout(TIMEOUT) #p ver este valor
    print("The server is ready to receive")

    next_message = [0]
    messages = []
    while True:
        msg, addr = Message.recv_from(sock)
        print(msg)
            
        if Error.is_error(msg):
            if msg != Error.RcvTimeout:
                continue
        else:
            if random.random() > 0.5:
                print(f"\n Dropeamos el paquete {msg.header.seq_num}\n")
                msg = Error.RcvTimeout
                continue
            heapq.heappush(messages, msg)
        result = handle_messages(messages, next_message, addr, sock)
        
        if Error.is_error(result):
            print(result)
            break
    sock.close()

def handle_upload(msg: Message, addr, sock: socket):
    result = store_package_server(msg.header.file_name, msg.payload)
    if Error.is_error(result): 
        return result
    #msg.acknowledge(sock, addr)

def handle_message(msg: Message, next_message, addr, sock: socket):
    print(f"next_message[0]: {next_message[0]} > msg.header.seq_num: {msg.header.seq_num}")
    if next_message[0] > msg.header.seq_num:
        return Error.DupMessage
    if msg.header.request == Request.Upload:
        print("entro al upload")
        return handle_upload(msg, addr, sock)

    #if msg.header.request == Request.Download:

def handle_messages(messages: list, next_message, addr, sock: socket):
    print(messages)
    last_handled_msg = None
    result = None
    while (len(messages) != 0) and (messages[0].header.seq_num <= next_message[0]):
        print(next_message[0])
        msg = heapq.heappop(messages)
        result = handle_message(msg, next_message, addr, sock)
        if Error.is_error(result):
            if result == Error.DupMessage:
                continue
            break
        next_message[0] += 1
        last_handled_msg = msg
    if last_handled_msg!= None:
        last_handled_msg.acknowledge(sock, addr)
    return result
    



def main():
    #init_server()
    serversito()

main()



# import socket

# # Crea un socket UDP
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# # Establece un tiempo de espera en segundos
# timeout = 5

# try:
#     # Espera la respuesta durante el tiempo especificado
#     sock.settimeout(timeout)
#     data, addr = sock.recvfrom(1024)
#     print("Respuesta recibida:", data.decode())
# except socket.timeout:
#     print("Tiempo de espera agotado. No se recibió ninguna respuesta.")
# finally:
#     sock.close()





