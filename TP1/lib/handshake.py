from lib.channel import Channel
from lib.message import *
import socket
import random
MAX_ATTEMPS = 5
TIMEOUT = 3

def send_sync(sync: Type, sock: socket, addr):
    msg = Message.make(sync,"",0,0,0,b"")
    msg.send_to(sock, addr)

def receive_sync(message_receiver: Channel, sync: Type):
    msg = message_receiver.get(TIMEOUT)
    if Error.is_error(msg):
        return False
    print(f"Recibi: {sync}")
    return msg.header.type == sync
    

def client_three_way_handshake(message_receiver: Channel, sock: socket, addr):
    send_sync(Type.Sync1, sock, addr)
    if not receive_sync(message_receiver ,Type.Sync2):
        return False
    send_sync(Type.Sync3, sock, addr)           #p  En caso de que se agrege el handler de send modificarlo
    return True

def attempt_connection(message_receiver: Channel, sock: socket, addr):
    for _ in range(MAX_ATTEMPS):
        if client_three_way_handshake(message_receiver, sock, addr):
            return True
    return False


def server_three_way_handshake(message_receiver: Channel, sock: socket, addr):
    result = receive_sync(message_receiver, Type.Sync1)
    send_sync(Type.Sync2, sock, addr)
    return receive_sync(Type.Sync3, sock) and result

