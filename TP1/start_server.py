import socket
import os
import time
import random
from lib.transfer_file import *
from lib.errors import Error
from lib.message import Type, Message
from lib.channel import Channel
from lib.connection_edges import ConnectionStatus
from lib.command_options import Options

UDP_IP = "127.0.0.1"
UDP_PORT = 42069
UP = 0
DOWN = 1
TIMEOUT = 10

def handle_client(message_receiver: Channel, client_addr, server_options: Options, sock: socket, finished_channel: Channel):
    print(client_addr)
    status = ConnectionStatus.attempt_connection_with_client(message_receiver, sock, client_addr)
    if status != ConnectionStatus.Connected:
        print(f"Failed to connect to Client: {client_addr}")
        finished_channel.put(client_addr)
        return
    
    #segund el primer mensaje hace rcv o send
    first_msg = message_receiver.get(TIMEOUT)
    if Error.is_error(first_msg):
        #fin 
        print(f"HUBOOOOOOOO UN ERRRRRRRRRRRORRRR, {os.getpid()}")
        finished_channel.put(client_addr)
        return
    
    message_receiver.put(first_msg)
    file_handling_options = Options(server_options.verbosity, client_addr, server_options.src + first_msg.header.file_name, first_msg.header.file_name) #to-do
    if first_msg.header.type == Type.Send:
        status = receive_file(message_receiver, file_handling_options, sock, first_msg.header.file_size)
    elif first_msg.header.type == Type.Receive:
        print(f"Entre al send, le pase {file_handling_options}")
        status = send_file(message_receiver, file_handling_options, sock, 0)
    #hacer fin
    print(status)
    status.finish_connection(message_receiver, sock, client_addr)
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
        #print(clients)
        msg, addr = Message.recv_from(sock)
        while not finished_clients.empty():
            addr = finished_clients.get()
            if clients.pop(addr).try_join():
                print("JOINEEEEEEEEEE")

        if not Error.is_error(msg):
            if clients.get(addr, None) == None:
                clients[addr] = ConnectionManager(handle_client, (addr, server_options, sock ,finished_clients))
                        #guarda cuando se corre dos veces seguidas, si no termino lo anterior hay que dropear el handshake
            clients[addr].send_message(msg) #enviar paquete x pipe a thread correspondiente
        
        

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





