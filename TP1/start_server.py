import socket
import threading
import sys
from lib.transfer_file import receive_file, send_file, ConnectionManager
from lib.errors import Error
from lib.message import Type, Message
from lib.channel import Channel
from lib.connection_edges import ConnectionStatus
from lib.command_options import Options
from lib.file_controller import FileController
from lib.print import print_verbose

TIMEOUT = 1


def handle_client(
    message_receiver: Channel,
    client_addr,
    server_options: Options,
    sock: socket,
    controller: FileController,
    finished_channel: Channel,
):
    print_verbose(f"--------------- New client: {client_addr} ---------------")
    status = ConnectionStatus.attempt_connection_with_client(
        message_receiver, sock, client_addr
    )
    if status != ConnectionStatus.Connected:
        print(f"Failed to connect to Client: {client_addr}")
        finished_channel.put(client_addr)
        return

    first_msg = message_receiver.peek(TIMEOUT)
    if Error.is_error(first_msg):
        finished_channel.put(client_addr)
        return

    # message_receiver.put(first_msg)
    file_handling_options = Options(
        client_addr,
        server_options.src + first_msg.header.file_name,
        first_msg.header.file_name,
        server_options.window_size,
    )  # to-do
    if first_msg.header.type == Type.Send:
        file = controller.try_write_lock(file_handling_options.src)
        if not Error.is_error(file):
            print(
                f"Receiving file: {file_handling_options.name} from: {file_handling_options.addr}"
            )
            status = receive_file(
                message_receiver,
                file_handling_options,
                sock,
                first_msg.header.file_size,
                file,
            )
            controller.release_write_lock(file)

    elif first_msg.header.type == Type.Receive:
        file = controller.try_read_lock(file_handling_options.src)
        if not Error.is_error(file):
            print(
                f"Sending file: {file_handling_options.name} to: {file_handling_options.addr}"
            )
            status = send_file(message_receiver, file_handling_options, sock, 0, file)
            controller.release_read_lock(file)

    status.finish_connection(message_receiver, sock, client_addr)
    print(f"Finish with status: {status}")
    finished_channel.put(client_addr)


def server_init():
    args = sys.argv[1:]
    server_options = Options.server_from_args(args)
    if Error.is_error(server_options) or (server_options is None):
        return
    print_verbose(f"Starting configuration {server_options}")
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
        while not finished_clients.empty():
            finished_addr = finished_clients.get()
            if clients.pop(finished_addr).try_join():
                print_verbose(
                    f"Joined thread handling communications with {finished_addr}"
                )

        if not Error.is_error(msg):
            if (clients.get(addr) is None) and end_of_program.empty():
                clients[addr] = ConnectionManager(
                    handle_client,
                    (addr, server_options, sock, controller, finished_clients),
                )
            clients[addr].send_message(msg)
        if not end_of_program.empty() and len(clients) == 0:
            running = False

    print("Closing server")
    sock.close()


def main():
    finish = Channel()
    join_handle = threading.Thread(target=server, args=(finish,))
    join_handle.start()
    end_of_program = False
    while not end_of_program:
        try:
            input("")
        except EOFError as e:
            finish.put(e)
            end_of_program = True

    join_handle.join()


main()
