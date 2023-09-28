import socket
import os
from enum import Enum
from lib.transfer_file import *
from lib.command_options import *
from lib.handshake import attempt_connection
from lib.channel import Channel

UDP_IP = "127.0.0.1"
UDP_PORT = 42069
FILE_NAME = "archivo_test.txt"
UP = 0
DOWN = 1   
TIMEOUT = 3

def upload(message_receiver: Channel, options: Options, sock: socket ,finished: Channel):
    if not attempt_connection(message_receiver, sock, options.addr):
        print(f"Failed to stablish connection with server addres: {options.addr}")
        finished.put(None)
        return

    send_file(message_receiver, options, sock, 0)

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
    connection = ConnectionManager(upload, (command, sock, finished))

    while finished.empty():
        msg, addr = Message.recv_from(sock)
        if not Error.is_error(msg):
            connection.send_message(msg)
    #print("TERMINOOOOOO")
    
    if connection.try_join():
        print("JOINEEEEEEEEEE")

main()