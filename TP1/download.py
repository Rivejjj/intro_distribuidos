import socket
import os
from enum import Enum
from lib.transfer_file import *
from lib.command_options import *
from lib.connection_edges import ConnectionStatus
from lib.channel import Channel


UDP_IP = "127.0.0.1"
UDP_PORT = 42069
FILE_NAME = "archivo_test.txt"
UP = 0
DOWN = 1   

REQUEST_TIMEOUT = 1 
REQUEST_ATTEMPTS = 10

def request_download(options: Options, sock: socket):
    download_request = Message.make(Type.Receive, options.name, 0, 0, 0,b"")
    print(download_request)
    download_request.send_to(sock ,options.addr)

def download(message_receiver: Channel, options: Options, sock: socket ,finished: Channel):
    status = ConnectionStatus.attempt_connection_with_server(message_receiver, sock, options.addr)
    if  status != ConnectionStatus.Connected:
        print(f"Failed to stablish connection with server address: {options.addr}")
        finished.put(None)
        return
    
    attempts = 0
    print(f"Voy a mandar con {options}")
    request_download(options, sock)
    msg = message_receiver.get(REQUEST_TIMEOUT)
    while (attempts < REQUEST_ATTEMPTS) and (Error.is_error(msg)):
        print(f"RECIBIMOS \n {msg} \n")
        request_download(options, sock)
        msg = message_receiver.get(REQUEST_TIMEOUT)
        attempts += 1
    
    if not Error.is_error(msg):
        options.src = "./" + options.src + "/" + options.name     #p falta chequear que exista la carpeta
        message_receiver.put(msg)

        file = try_open_file(options.src, "wb")
        
        if not Error.is_error(file):
            status = receive_file(message_receiver, options, sock, msg.header.file_size,file)
            file.close()
        else:
            remove_file(options.src)

        status.finish_connection(message_receiver, sock, options.addr) 

    finished.put(None)

def main():
    args = sys.argv[1:] # [1:] para omitir el nombre del script

    command = Options.download_from_args(args)
    if (Error.is_error(command)) or (command == None):
        print(f"{command}")
        return
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.2", 42069))
    sock.settimeout(TIMEOUT)

    finished = Channel()
    connection = ConnectionManager(download, (command, sock, finished))

    while finished.empty():
        msg, addr = Message.recv_from(sock)
        if not Error.is_error(msg):
            connection.send_message(msg)        #todo check direccion
    #print("TERMINOOOOOO")
    finished.get()
    if connection.try_join():
        print("JOINEEEEEEEEEE")
            

main()