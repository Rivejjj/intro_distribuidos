import socket
import os
from enum import Enum
from lib.transfer_file import *
from lib.command_options import *


UDP_IP = "127.0.0.1"
UDP_PORT = 42069
FILE_NAME = "archivo_test.txt"
UP = 0
DOWN = 1   

"""
def define_message(file, request):
    # formato:
    #     2 bits 0: request (UPLOAD=0, DOWNLOAD=1, ack= 2, solicitud de files disponibles = 3)
    #     32 u 64 bytes para el nombre del archivo
    #     x bytes para 2gs: longitud del archivo (por ahora no es necesaria) //cantidad de paquetes (dividido el tam max)
    #     2 bytes longitud [0-65535] del payload variable con tope superior
    #     sequence number
    #     Hash

    # a decidir: se manda un ack y despues el archivo o directamente el archivo?

    #     payload bytes n+1 a m: contenido del archivo (solo si request es UPLOAD)
    
    
    file_content = file.read()
    header = request.to_bytes(1, byteorder='big')
    header += len(FILE_NAME).to_bytes(1, byteorder='big')
    
    header += FILE_NAME.encode() # + lo que falte hasta 32/64 bytes
    
    
    if request == UP:
        message = len(file_content).to_bytes(1, byteorder='big')
        message += file_content.encode()
        return header + message
    
    #if request == DOWN:
    return header

def download_file(file_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    request = define_message(file_name, DOWN)
    sock.sendto(request, (UDP_IP, UDP_PORT))

    file_content, server_addr = sock.recvfrom(1024)
    if file_content.decode() == "File not found":
        print(f"{file_content.decode()}")
        sock.close()
        return
    
    received = open(FILE_NAME, "a")
    while file_content != b'':
        content = file_content.decode()
        print(content)
        received.write(content)
        file_content, server_addr = sock.recvfrom(1024)
"""

def main():
    args = sys.argv[1:] # [1:] para omitir el nombre del script

    command = Options.from_args(args, Request.Upload)
    if (command == None):
        return
    send_file(command)

main()