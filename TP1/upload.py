import socket
import os
import sys
from enum import Enum
from lib.transfer_file import *
from lib.command_options import Options
from lib.connection_edges import ConnectionStatus, try_connect
from lib.channel import Channel
from lib.message import Message, Error

TIMEOUT = 3


def upload(
    message_receiver: Channel, options: Options, sock: socket, finished: Channel
):
    status = ConnectionStatus.attempt_connection_with_server(
        message_receiver, sock, options.addr
    )
    if status != ConnectionStatus.Connected:
        print(f"Failed to stablish connection with server addres: {options.addr}")
        finished.put(None)
        return
    print(f"Uploading file: {options.name} to: {options.addr}")
    file = try_open_file(options.src, "rb")
    if not Error.is_error(file):
        status = send_file(message_receiver, options, sock, 0, file)
        file.close()
    print(f"Finish with status: {status}")
    status.finish_connection(message_receiver, sock, options.addr)

    finished.put(None)


def main():
    args = sys.argv[1:]

    command = Options.upload_from_args(args)
    if Error.is_error(command) or command == None:
        return
    print("verbose")
    print_verbose(f"Starting configuration {command}")
    sock = try_connect("127.0.0.2")
    if Error.is_error(sock):
        print(f"{sock}")
        return
    sock.settimeout(TIMEOUT)

    finished = Channel()
    connection = ConnectionManager(upload, (command, sock, finished))

    while finished.empty():
        msg, addr = Message.recv_from(sock)
        if not Error.is_error(msg):
            connection.send_message(msg)

    connection.join()


main()
