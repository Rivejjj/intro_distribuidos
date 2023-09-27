import sys
import os
import time
import heapq
import threading
from multiprocessing import Queue
import queue
import random
from lib.message import *
from lib.command_options import Options

TIMEOUT = 0.2 # A definir
PACKAGE_TIMEOUT = 2 # A definir
RECEIVE_TIMEOUT = 10
MAX_ATTEMPTS = 10

class ConnectionManager:
    def __init__(self, conection_function, args):
        channel = Channel()
        self.channel = channel
        self.join_handle = threading.Thread(target=conection_function, args=(channel,) + args)
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

def send_file(message_receiver: Channel, options: Options, sock: socket, seq_num):
    print("entre a send")
    file_size = os.path.getsize(options.src)
    if file_size > MAX_FILE_SIZE:
        print("Invalid file size")
        return
    
    #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    file = open(options.src, "rb")
    #sock.bind(addr)

    read = file.read(PAYLOAD_SIZE)
    #sock.settimeout(TIMEOUT) #p ver este valor
    send_attempts = 0
    #iterar sobre read para leer todo el archivo
    while (read != b'') and (send_attempts < MAX_ATTEMPTS):
        message = Message.make(Type.Send, options.name, file_size, len(read), seq_num, read)
        print(message)
        
        if random.random() > 0.8:
            message.header.seq_num = 1000
            print(" corrompiendo un paquete")

        message.send_to(sock, options.addr)
        send_attempts +=1
        sent = time.time()
        while time.time() - sent < PACKAGE_TIMEOUT:
            msg = message_receiver.get(PACKAGE_TIMEOUT - (time.time() - sent))
            if Error.is_error(msg):
                continue
        
            if (msg.header.type == Type.Ack) and (msg.header.seq_num == seq_num + 1):
                send_attempts = 0
                seq_num += 1
                read = file.read(PAYLOAD_SIZE)
                print("received_ack")
                break
        # wait_for_ack() #si estamos en stop & wait

def receive_file(message_receiver: Channel, options: Options, sock: socket):
    #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.bind((UDP_IP,UDP_PORT))
    #sock.settimeout(TIMEOUT) #p ver este valor
    print("The server is ready to receive")

    next_message = [0]
    messages = []
    received_bytes = 0

    while True:
        msg = message_receiver.get(RECEIVE_TIMEOUT)
        if Error.is_error(msg):
            break
        if random.random() > 0.5:
            heapq.heappush(messages, msg)
            received_bytes += msg.header.payload_size
        else:
            print(f"\n Dropeamos el paquete {msg.header.seq_num}\n")
        
        result = handle_send_messages(messages, next_message, options, sock)
        if Error.is_error(result):
            print(result)
            break
        if received_bytes == msg.header.file_size:
            break
    
    
def handle_send_message(msg: Message, path):
    result = store_package(path, msg.payload)
    if Error.is_error(result): 
        return result
    #msg.acknowledge(sock, addr)

#ver que hacer con lo de que te manden mas paquetes de los que dice el header
def handle_send_messages(messages: list, next_message, options: Options,sock: socket):
    result = None
    
    while (len(messages) != 0) and (messages[0].header.seq_num <= next_message[0]):
        print(next_message[0])
        msg = heapq.heappop(messages)
        if (msg.header.seq_num < next_message[0]) or (msg.header.type != Type.Send):
            continue
        
        result = handle_send_message(msg, options.src)
        if Error.is_error(result):
            break
        next_message[0] += 1
    
    Message.send_ack(next_message[0],sock, options.addr)
    print(f"mande ack a {options.addr}")
    return result


# def handle_msg( : Message):
#     if msg.header.request == Request.Upload:
#         result = store_package_server(msg.header.file_name, msg.payload)
#         if result == -1:
#             print("Filed to store file")
    
#         # EN LUGAR DEL ACK SE MANDA ERROR PA CORTAR LA TRANSMICION
#         return # Y muere hilo de este cliente
#     print(msg)

def store_package(path, data: bytearray):
    print(f"Storing file in {path}")
    with open(path, 'ab') as file:
        file.write(data)

    return 0