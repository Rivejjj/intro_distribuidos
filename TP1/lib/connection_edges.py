from lib.channel import Channel
from lib.message import Type, Message
import socket
import random
import time
from enum import Enum
from lib.errors import Error
MAX_ATTEMPS = 5
TIMEOUT = 3

class ConnectionStatus(Enum):
    Disconnected = 0
    Connected = 1
    FinRequested = 2
    ConnectionLost = 3

    def __str__(self):
        return f"Connection status: {self.name}"
    
    @classmethod
    def attempt_connection_with_server(self, message_receiver: Channel, sock: socket, addr):
        if attempt_function(client_three_way_handshake, (message_receiver, sock, addr)):
            return ConnectionStatus.Connected
        return ConnectionStatus.Disconnected
    
    @classmethod
    def attempt_connection_with_client(self, message_receiver: Channel, sock: socket, addr):
        if server_three_way_handshake(message_receiver, sock, addr):
            return ConnectionStatus.Connected
        return ConnectionStatus.Disconnected
    
    def finish_connection(self, message_receiver: Channel, sock: socket, addr):
        if self == ConnectionStatus.Connected:
            return attempt_function(start_end_of_connection, (message_receiver, sock, addr))
        elif self == ConnectionStatus.FinRequested:
            return attempt_function(proccess_end_of_connection, (message_receiver, sock, addr))
        return False


def send_connection_msg(connection_step: Type, sock: socket, addr):
    msg = Message.make(connection_step,"",0,0,0,b"")
    print(f"Mando {connection_step}")
    msg.send_to(sock, addr)

def receive_connection_msg(message_receiver: Channel, connection_step: Type):
    msg = message_receiver.get(TIMEOUT)
    if Error.is_error(msg):
        return False
    return msg.header.type == connection_step

def client_three_way_handshake(message_receiver: Channel, sock: socket, addr):
    send_connection_msg(Type.Sync1, sock, addr)
    if not receive_connection_msg(message_receiver ,Type.Sync2):
        return False
    send_connection_msg(Type.Sync3, sock, addr)           #p  En caso de que se agrege el handler de send modificarlo
    return True

def server_three_way_handshake(message_receiver: Channel, sock: socket, addr):
    if not receive_connection_msg(message_receiver, Type.Sync1):
        return False
    send_connection_msg(Type.Sync2, sock, addr)
    return receive_connection_msg(message_receiver, Type.Sync3)

def receive_until_types(message_receiver: Channel, types: list):
    sent = time.time()
    attemps = 0
    while time.time() - sent < TIMEOUT and attemps < MAX_ATTEMPS:
        msg = message_receiver.get(TIMEOUT - (time.time() - sent))
        attemps += 1
        if Error.is_error(msg) or msg.header.type not in types:
            continue
        print(f"Recibi {msg.header.type}")
        return msg.header.type
    
    return Error.RcvTimeout

#asumis que ya recibiste el fin1
def proccess_end_of_connection(message_receiver: Channel, sock: socket, addr):
    print("EMPECE A PROCESAR")
    send_connection_msg(Type.FinAck, sock, addr)
    send_connection_msg(Type.Fin, sock, addr)
    received = receive_until_types(message_receiver ,[Type.FinAck])
    if Error.is_error(received):
        return False
    return received

def start_end_of_connection(message_receiver: Channel, sock: socket, addr):
    print("ENVIO PRIMER FIN")
    send_connection_msg(Type.Fin, sock, addr)
    types = [Type.Fin, Type.FinAck]
    received = receive_until_types(message_receiver ,types)
    if Error.is_error(received):
        return False
    if received == Type.Fin:
        send_connection_msg(Type.FinAck, sock, addr)
        
    types.remove(received)
    received = receive_until_types(message_receiver ,types)
    if Error.is_error(received):
        return False
    send_connection_msg(Type.FinAck, sock, addr)
    return True

def attempt_proccess_end_of_connection(message_receiver: Channel, sock: socket, addr):
    return 

def attempt_start_end_of_connection(message_receiver: Channel, sock: socket, addr):
    return attempt_function(proccess_end_of_connection, (message_receiver, sock, addr))

def attempt_function(function, args):
    for _ in range(MAX_ATTEMPS):
        if function(*args):
            return True
    return False
