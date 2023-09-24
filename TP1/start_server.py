import socket
import os
import time
from lib.message import *
from lib.transfer_file import store_package
from lib.errors import Error

UDP_IP = "127.0.0.1"
UDP_PORT = 42069
UP = 0
DOWN = 1

class File:
    def __init__(self, name, content):
        self.name = name
        self.content = content
"""
def parse_upload_request(message):
    #p todo
    file_name_length = int(message[0])
    file_name = message[1:file_name_length+1].decode()
    file_content_length = int(message[file_name_length+1])
    file_content = message[file_name_length+2:].decode()


    print(f"File name: {file_name}\nFile content:\n{file_content}")
    return File(file_name, file_content)

def init_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP,UDP_PORT))    
    print("The server is ready to receive")
    #Crear un hilo x cada conexion entrante

    while True:
        data, addr = sock.recvfrom(1024)
        #p PARSEO
        request = int(data[0])

        if request == UP:
            file = parse_upload_request(data[1:])
            result = store_package(file.name, file.content)
            if result == -1:
                print("Filed to store file {}", file)
                # EN LUGAR DEL ACK SE MANDA ERROR PA CORTAR LA TRANSMICION
                return # Y muere hilo de este cliente
            sock.sendto("File uploaded successfully".encode(), addr) # envio mensaje de confirmacion              

        if request == DOWN:
            # enviar archivo al cliente
            print("Sending file to client")
"""

        #Envio de ack

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
    print("The server is ready to receive")
    while True:
        msg, addr = Message.recv_from(sock)
        result = handle_message(msg, addr, sock)
        if Error.is_error(result):
            print(f"Error: {result}")
            break
        print(msg)
        
def handle_upload(msg: Message, addr, sock: socket):
    result = store_package_server(msg.header.file_name, msg.payload)
    if Error.is_error(result): 
        return result
    #msg.acknowledge(sock, addr)

def handle_message(msg: Message, addr, sock: socket):
    if msg.header.request == Request.Upload.value:
        return handle_upload(msg, addr, sock)

    #if msg.header.request == Request.Download:


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





