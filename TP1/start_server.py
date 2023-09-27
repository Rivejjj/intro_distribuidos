import socket
import os
import time
import random
from lib.message import *
from lib.transfer_file import *
from lib.errors import Error
from lib.message import *

UDP_IP = "127.0.0.1"
UDP_PORT = 42069
UP = 0
DOWN = 1
TIMEOUT = 10

def handle_client(message_receiver: Channel, client_addr, server_options: Options, sock: socket, finished_channel: Channel):
    print(client_addr)
    #handshake
    #segund el primer mensaje hace rcv o send
    first_msg = message_receiver.get(TIMEOUT)
    if Error.is_error(first_msg):
        #fin 
        print(f"HUBOOOOOOOO UN ERRRRRRRRRRRORRRR, {os.getpid()}")
        finished_channel.put(client_addr)
        return
    
    message_receiver.put(first_msg)
    
    file_handling_options = Options(server_options.verbosity, client_addr, server_options.src + first_msg.header.file_name, first_msg.header.file_name)
    if first_msg.header.type == Type.Send:
        receive_file(message_receiver, file_handling_options, sock)
    elif first_msg == Type.Receive:
        send_file()
    #hacer fin
    finished_channel.put(client_addr)

def server_init(path):
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except OSError: 
            print("fue el OS")
            return Error.ErrorStoringData

def server():
    server_options = Options(True, (UDP_IP,UDP_PORT), './server_files/', None)
    server_init(server_options.src)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server_options.addr)
    sock.settimeout(TIMEOUT)
    clients = {}
    finished_clients = Channel()

    while True:
        print(clients)

        msg, addr = Message.recv_from(sock)
        i = 1
        while not finished_clients.empty():
            i+=1
            addr = finished_clients.get()
            if clients.pop(addr).try_join():
                print("JOINEEEEEEEEEE")

        if not Error.is_error(msg):
            if clients.get(addr, None) == None:
                clients[addr] = ConnectionManager(handle_client, (addr, server_options, sock ,finished_clients))
                        #guarda cuando se corre dos veces seguidas, si no termino lo anterior hay que dropear el handshake
            clients[addr].send_message(msg) #enviar paquete x pipe a thread correspondiente
            print(f"-------------LONGITUD DEL DICCIONARIO CLIENT: {len(clients)} --------------")
        
        

    #sock.close()


def main():
    #init_server()
    server()

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





