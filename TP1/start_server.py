import socket
import os
import time
import random
import threading
from lib.transfer_file import *
from lib.errors import Error
from lib.message import Type, Message
from lib.channel import Channel
from lib.connection_edges import ConnectionStatus
from lib.command_options import Options
from lib.file_controller import FileController

TIMEOUT = 1

def handle_client(message_receiver: Channel, client_addr, server_options: Options, sock: socket, controller: FileController,finished_channel: Channel):
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
    file_handling_options = Options(server_options.verbosity, client_addr, server_options.src + first_msg.header.file_name, first_msg.header.file_name, server_options.window_size) #to-do
    if first_msg.header.type == Type.Send:
        file = controller.try_write_lock(file_handling_options.src)
        if not Error.is_error(file):
            status = receive_file(message_receiver, file_handling_options, sock, first_msg.header.file_size, file)
            controller.release_write_lock(file)
    
    elif first_msg.header.type == Type.Receive:
        file = controller.try_read_lock(file_handling_options.src)
        if not Error.is_error(file):
            status = send_file(message_receiver, file_handling_options, sock, 0,file)
            controller.release_read_lock(file)
    #hacer fin
    print(status)
    status.finish_connection(message_receiver, sock, client_addr)
    finished_channel.put(client_addr)

def server_init():
    args = sys.argv[1:]
    server_options = Options.server_from_args(args)
    print(server_options)
    if (server_options == None) or (Error.is_error(server_options)):
        return
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server_options.addr)
    sock.settimeout(TIMEOUT)

    clients = {}
    finished_clients = Channel()
    controller = FileController()

    return server_options, sock, clients, finished_clients, controller

def server(end_of_program: Channel):
    
    server_options, sock, clients, finished_clients, controller = server_init()
    print("Server is running")
    running = True
    while running:
        msg, addr = Message.recv_from(sock)
        #print(f"me llego mensaje de tipo {msg.header.type} de {addr}")
        while not finished_clients.empty():
            finished_addr = finished_clients.get()
            if clients.pop(finished_addr).try_join():
                print("JOINEEEEEEEEEE")

        if not Error.is_error(msg):
            if clients.get(addr, None) == None and end_of_program.empty():
                clients[addr] = ConnectionManager(handle_client, (addr, server_options, sock ,controller, finished_clients))
                        #guarda cuando se corre dos veces seguidas, si no termino lo anterior hay que dropear el handshake
            clients[addr].send_message(msg) #enviar paquete x pipe a thread correspondiente
        if not end_of_program.empty() and len(clients) == 0:
            running = False
        
    sock.close()



def main():
    #init_server()
    print("HOLA")
    finish = Channel()
    join_handle = threading.Thread(target=server, args=(finish,))
    print("COMO ANDAS")
    join_handle.start()
    print("2CHAU")
    end_of_program = False
    while not end_of_program:
        print("entro a l while")
        try:
            input("input:")
        except EOFError as e:
            finish.put(e)
            print("CTRL DDDDDDDDDDDDDDDDDDDDDDDDDD")
            end_of_program = True

    join_handle.join()


main()



