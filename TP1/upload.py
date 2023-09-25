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

def main():
    args = sys.argv[1:] # [1:] para omitir el nombre del script

    command = Options.from_args(args, Request.Upload)
    if (command == None):
        return
    send_file(command, 0)

main()