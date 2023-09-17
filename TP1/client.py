import socket
from enum import Enum

UDP_IP = "127.0.0.1"
UDP_PORT = 6969
FILE_NAME = "archivo_test.txt"
UP = 0
DOWN = 1   

def define_message(file, request):
    # formato:
    #     byte 0: request (UPLOAD=0, DOWNLOAD=1)
    #     byte 1: largo del nombre del archivo
    #     bytes 2 a n: nombre del archivo
    #     byte n+1: longitud del archivo (por ahora no es necesaria)
    #     bytes n+1 a m: contenido del archivo (solo si request es UPLOAD)
    
    file_content = file.read()
    header = request.to_bytes(1, byteorder='big')
    header += len(FILE_NAME).to_bytes(1, byteorder='big')
    header += FILE_NAME.encode()
    
    if request == UP:
        message = len(file_content).to_bytes(1, byteorder='big')
        message += file_content.encode()
        return header + message
    
    #if request == DOWN:
    return header

def upload_file(file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("The client is ready to send")

    while True:
        message = define_message(file, UP)
        sock.sendto(message, (UDP_IP, UDP_PORT))
        message_response, server_addr = sock.recvfrom(1024)
        if message_response.decode() == "File uploaded successfully":
            print(f"{message_response.decode()}")
            break

    sock.close()

def main():
    file = open(FILE_NAME, "r")
    upload_file(file)
    file.close()

main()