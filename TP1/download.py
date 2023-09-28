import socket
import os
from enum import Enum
from lib.transfer_file import *
from lib.command_options import *
from lib.handshake import *
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
    if not attempt_connection(message_receiver ,sock, options.addr):
        print(f"Failed to stablish connection with server addres: {options.addr}")
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
    options.src = "./" + options.src + "/" + options.name
    receive_file(message_receiver, options, sock)

    #p falta chequear que exista la carpeta

    #fin
    finished.put(None)

def main():
    args = sys.argv[1:] # [1:] para omitir el nombre del script

    command = Options.from_args(args)
    if (command == None):
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