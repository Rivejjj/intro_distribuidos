import socket
from enum import Enum
from lib.transfer_file import *
from lib.command_options import Options
from lib.connection_edges import ConnectionStatus, try_connect
from lib.channel import Channel

REQUEST_TIMEOUT = 3
REQUEST_ATTEMPTS = 5


def request_download(options: Options, sock: socket):
    download_request = Message.make(Type.Receive, options.name, 0, 0, 0, b"")
    print_verbose(f"Requesting file")
    download_request.send_to(sock, options.addr)


def download(
    message_receiver: Channel, options: Options, sock: socket, finished: Channel
):
    status = ConnectionStatus.attempt_connection_with_server(
        message_receiver, sock, options.addr
    )
    if status != ConnectionStatus.Connected:
        print(f"Failed to stablish connection with server address: {options.addr}")
        finished.put(None)
        return

    print(f"Downloading file: {options.name} from: {options.addr}")

    attempts = 0
    request_download(options, sock)
    msg = message_receiver.peek(REQUEST_TIMEOUT)
    while (attempts < REQUEST_ATTEMPTS) and (Error.is_error(msg)):
        request_download(options, sock)
        msg = message_receiver.get(REQUEST_TIMEOUT)
        attempts += 1

    if not Error.is_error(msg):
        options.src = (
            "./" + options.src + "/" + options.name
        )  # p falta chequear que exista la carpeta

        file = try_open_file(options.src, "wb")
        if Error.is_error(file):
            remove_file(options.src)

        status = receive_file(
            message_receiver, options, sock, msg.header.file_size, file
        )
        file.close()

        print(f"Finish with status: {status}")
        status.finish_connection(message_receiver, sock, options.addr)

    finished.put(None)


def main():
    args = sys.argv[1:]

    command = Options.download_from_args(args)
    if Error.is_error(command) or command == None:
        return
    print_verbose(f"Starting configuration {command}")
    sock = try_connect("127.0.0.2")
    if Error.is_error(sock):
        print(sock)
        return
    sock.settimeout(TIMEOUT)

    finished = Channel()
    connection = ConnectionManager(download, (command, sock, finished))

    while finished.empty():
        msg, addr = Message.recv_from(sock)
        if not Error.is_error(msg):
            connection.send_message(msg)  # todo check direccion

    finished.get()
    connection.join()


main()
