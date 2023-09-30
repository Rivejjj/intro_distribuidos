import os
import time
import heapq
import threading
import random
import math
from queue import Queue
from lib.message import *
from lib.command_options import Options
from lib.channel import Channel
from lib.connection_edges import ConnectionStatus
from lib.errors import Error

TIMEOUT = 1 # A definir
PACKAGE_TIMEOUT = 2 # A definir
RECEIVE_TIMEOUT = 10
VALID_PACKAGE_TIMEOUT = 10
MAX_ATTEMPTS = 10
MAX_DUP = 2
MAX_ACK_RESENDS = 5
MAX_TIMEOUTS = 4 #ojo con estos numeros

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

class TimeoutEntry:
    def __init__(self, seq_num):
        self.seq_num = seq_num
        self.timeout = time.time() + TIMEOUT
        self.amount_of_timeouts = 0
    
    def restart_timeout(self):
        self.timeout = time.time() + TIMEOUT
        self.amount_of_timeouts += 1
        return self

    def __lt__(self, other): 
        return self.timeout < other.timeout

class Window:
    def __init__(self, max_size, file_size): 
        self.max_size = max_size
        self.amount_of_packages = math.ceil(file_size/PAYLOAD_SIZE)
        self.timeouts = []
        self.messages = []
        self.last_ack = 0
        self.duped_acks = 0
        self.ack_resends = 0

    def __str__(self):
        string = "buffer: ["
        for entry in self.timeouts:
            string += f"{entry.seq_num}, "
        string += "]\n Messages: ["
        for message in self.messages:
            string += f"{message.header.seq_num}, "
        string += f"]\n Last_ack: {self.last_ack}\n Ack resends: {self.ack_resends} \n"
        
        return string
    
    def send(self, message: Message, sock: socket, addr):
        if len(self.messages) >= self.max_size:
            return Error.WindowFull
        message.send_to(sock, addr)
        self.timeouts.append(TimeoutEntry(message.header.seq_num))
        self.messages.append(message)

    def time_until_next_timeout(self):
        if len(self.timeouts) == 0:
            return 0
        next_time_out = self.timeouts[0].timeout - time.time()
        if next_time_out > 0:
            return next_time_out
        return 0

    def resend(self, seq_number, sock, addr):
        position = seq_number - self.last_ack
        #print(f"resend: \n {self}")
        self.messages[position].send_to(sock, addr)
        
        for i in range(len(self.timeouts)):
            if self.timeouts[i].seq_num == seq_number:
                entry = self.timeouts.pop(i)
                break
        
        self.timeouts.append(entry.restart_timeout())

    def acknowledge(self, seq_num):
        print(f"aknowledge\n {self}")
        last_msg_sent = self.messages[len(self.messages)-1]
        if seq_num > last_msg_sent.header.seq_num + 1:
            return Error.InvalidSeqNum
        starting = seq_num - self.last_ack

        self.messages = self.messages[starting:]
        aux = []
        for entry in self.timeouts:
            if entry.seq_num >= seq_num:
                aux.append(entry)
        self.timeouts = aux
        self.last_ack = seq_num
        self.duped_acks = 0
        self.ack_resends = 0

    def handle_ack(self, ack: Message, sock, addr):
        print("handle_ack")
        if ack.header.seq_num == self.last_ack:
            self.duped_acks +=1
            if self.duped_acks > MAX_DUP:
                if self.ack_resends >= MAX_ACK_RESENDS:
                    return Error.TooManyDupAck
                self.resend(self.last_ack, sock, addr)
                
                self.ack_resends += 1
        if ack.header.seq_num > self.last_ack:
            return self.acknowledge(ack.header.seq_num)

    
    def handle_timeout(self, sock: socket, addr):
        if len(self.timeouts) == 0:
            return
        next_time_out = self.time_until_next_timeout()
        while next_time_out <= 0:
            entry = self.timeouts[0]
            if entry.amount_of_timeouts > MAX_TIMEOUTS:
                return Error.RcvTimeout
            self.resend(entry.seq_num, sock, addr)
            next_time_out = self.time_until_next_timeout()
        print(f"final timeout {self}")

    def finished(self):
        if self.last_ack == self.amount_of_packages:
            return True
        return False

#selective 
def send_file(message_receiver: Channel, options: Options, sock: socket, seq_num)->ConnectionStatus:
    print("entre a send")
    file_size = os.path.getsize(options.src)
    if file_size > MAX_FILE_SIZE:
        print("Invalid file size")
        return ConnectionStatus.Connected
    window_size = 3
    window = Window(window_size, file_size)
    file = open(options.src, "rb")
    read = file.read(PAYLOAD_SIZE)
    
    while not window.finished():
        timeout = window.time_until_next_timeout()
        if (read != b''):
            message = Message.make(Type.Send, options.name, file_size, len(read), seq_num, read)
            sent = window.send(message, sock, options.addr)
            if not Error.is_error(sent):
                seq_num += 1
                read = file.read(PAYLOAD_SIZE)
                timeout = 0

        msg = message_receiver.get(timeout)
        if not Error.is_error(msg):
            if msg.header.type == Type.Fin:
                return ConnectionStatus.FinRequested
            if msg.header.type == Type.Ack:
                result = window.handle_ack(msg, sock, options.addr)
                if Error.is_error(result):
                    return ConnectionStatus.Connected
        if Error.is_error(window.handle_timeout(sock, options.addr)):
            return ConnectionStatus.ConnectionLost
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
        if random.random() >= 0.5:
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