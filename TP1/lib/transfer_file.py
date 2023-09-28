import sys
import os
import time
import heapq
import threading
import random
from lib.message import *
from lib.command_options import Options
from lib.channel import Channel
from lib.connection_edges import ConnectionStatus
from lib.errors import Error

TIMEOUT = 0.2 # A definir
PACKAGE_TIMEOUT = 2 # A definir
RECEIVE_TIMEOUT = 10
VALID_PACKAGE_TIMEOUT = 10
MAX_ATTEMPTS = 10

class ConnectionManager:
    def __init__(self, conection_function, args):
        self.channel = Channel()
        self.join_handle = threading.Thread(target=conection_function, args=(self.channel,) + args)
        self.join_handle.start()
        print("--------------SE SPAWNEA THREAD-----------")
    
    def try_join(self):
        if not self.join_handle.is_alive():
            print("joinea el thread")
            self.join_handle.join()
            return True
        return False

    def send_message(self, msg: Message):
        self.channel.put(msg)

def send_file(message_receiver: Channel, options: Options, sock: socket, seq_num)->ConnectionStatus:
    print("entre a send")
    file_size = os.path.getsize(options.src)
    if file_size > MAX_FILE_SIZE:
        print("Invalid file size")
        return ConnectionStatus.Connected
    
    #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    file = open(options.src, "rb")
    #sock.bind(addr)

    read = file.read(PAYLOAD_SIZE)
    #sock.settimeout(TIMEOUT) #p ver este valor
    send_attempts = 0
    #iterar sobre read para leer todo el archivo
    while (read != b''):
        if send_attempts > MAX_ATTEMPTS:
            return ConnectionStatus.ConnectionLost
        message = Message.make(Type.Send, options.name, file_size, len(read), seq_num, read)
        print(message)
        
        if random.random() > 0.9:
            message.header.seq_num = 1000
            print("## corrompiendo un paquete")

        message.send_to(sock, options.addr)
        send_attempts += 1
        sent = time.time()
        while time.time() - sent < PACKAGE_TIMEOUT:
            msg = message_receiver.get(PACKAGE_TIMEOUT - (time.time() - sent))
            if Error.is_error(msg):
                continue
            if msg.header.type == Type.Fin:
                return ConnectionStatus.FinRequested
            if (msg.header.type == Type.Ack) and (msg.header.seq_num == seq_num + 1):
                send_attempts = 0
                seq_num += 1
                read = file.read(PAYLOAD_SIZE)
                print("received_ack")
                break
        # wait_for_ack() #si estamos en stop & wait
    return ConnectionStatus.Connected



def receive_file(message_receiver: Channel, options: Options, sock: socket, expected_file_size)->ConnectionStatus:
    print("Im ready to receive")
    
    next_message = [0]
    bytes_received = [0]
    messages = []
    last_usefull_package_time = time.time()
    status = ConnectionStatus.Connected
    
    while time.time() - last_usefull_package_time < RECEIVE_TIMEOUT:
        msg = message_receiver.get(RECEIVE_TIMEOUT - (time.time() - last_usefull_package_time))
        if Error.is_error(msg):
            status = ConnectionStatus.ConnectionLost
            break
        if msg.header.type == Type.Fin:
            print("ME LLEGO EL PRIMER FIN LOCO")
            status = ConnectionStatus.FinRequested
            break
        if random.random() > 0.1:
            heapq.heappush(messages, msg)
        else:
            print(f"\n Dropeamos el paquete {msg.header.seq_num}\n")
            continue

        increased_bytes = handle_send_type_messages(messages, next_message, bytes_received, expected_file_size, options, sock)
        if Error.is_error(increased_bytes):
            status = ConnectionStatus.ConnectionLost
            break
        if increased_bytes:
            last_usefull_package_time = time.time()

    if not (bytes_received[0] == expected_file_size):
        print("Failed to download File")
        
        #hacer algo de los archivos corruptos si pinta
    return status
    

def handle_send_type_messages(messages: list, next_message, bytes_received, expected_file_size, options: Options,sock: socket):
    increased_bytes = False
    while (len(messages) != 0) and (messages[0].header.seq_num <= next_message[0]):
        msg = heapq.heappop(messages)
        if msg.header.type != Type.Send:
            continue
        if (msg.header.seq_num == next_message[0]) and (bytes_received[0] + msg.header.payload_size <= expected_file_size):
            stored = store_package(options.src, msg.payload)
            if Error.is_error(stored):
                return stored
            bytes_received[0] += stored
            next_message[0] +=1
            if msg.header.payload_size != 0:
                increased_bytes = True
                
    Message.send_ack(next_message[0],sock, options.addr)
    print(f"mande ack a {options.addr}")
    return increased_bytes

def store_package(path, data: bytearray):
    print(f"Storing file in {path}")
    try:
        with open(path, 'ab') as file:
            file.write(data)
    except OSError:
        return Error.ErrorStoringData
    return len(data)