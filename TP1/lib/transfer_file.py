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
from lib.print import print_verbose, print_progress_bar

TIMEOUT = 3 
MAX_TIMEOUTS = 5 
RECEIVE_TIMEOUT = 10
MIN_DUP = 2
MAX_ACK_RESENDS = 4

class ConnectionManager:
    def __init__(self, conection_function, args):
        self.channel = Channel()
        self.join_handle = threading.Thread(target=conection_function, args=(self.channel,) + args)
        self.join_handle.start()
    
    def try_join(self):
        if not self.join_handle.is_alive():
            self.join_handle.join()
            return True
        return False
    
    def join(self):
        return self.join_handle.join()

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
        print_verbose(f"Sending file, package {message.header.seq_num} to {addr}")
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
        self.messages[position].send_to(sock, addr)
        
        for i in range(len(self.timeouts)):
            if self.timeouts[i].seq_num == seq_number:
                entry = self.timeouts.pop(i)
                break
        
        self.timeouts.append(entry.restart_timeout())


    def acknowledge(self, seq_num):
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

    def curr_max_dup(self):
        print(f"max dup {max(MIN_DUP, len(self.messages) // 2)}")
        return max(MIN_DUP, len(self.messages) // 2)

    def handle_ack(self, ack: Message, sock, addr):
        if ack.header.seq_num == self.last_ack:
            self.duped_acks +=1
            if self.duped_acks > self.curr_max_dup():
                if self.ack_resends >= MAX_ACK_RESENDS:
                    return Error.TooManyDupAck
                self.resend(self.last_ack, sock, addr)
                print_verbose(f"Resending package {self.last_ack} to {addr} due to too many acks\n")
                self.ack_resends += 1
                self.duped_acks = 0
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
            print_verbose(f"Resending package {entry.seq_num} to {addr}due to timeout\n")
            next_time_out = self.time_until_next_timeout()

    def finished(self):
        if self.last_ack == self.amount_of_packages:
            return True
        return False
    
#selective 
def send_file(message_receiver: Channel, options: Options, sock: socket, seq_num,file)->ConnectionStatus:
    file_size = os.path.getsize(options.src)
    if file_size > MAX_FILE_SIZE:
        print("Invalid file size")
        return ConnectionStatus.Connected
    
    window = Window(options.window_size, file_size)
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
            print_verbose(f"Received msg of type {msg.header.type} with seq_num {msg.header.seq_num} from {options.addr}\n")
            if msg.header.type == Type.Fin:
                return ConnectionStatus.FinRequested
            if msg.header.type == Type.Ack:
                result = window.handle_ack(msg, sock, options.addr)
                if Error.is_error(result):
                    return ConnectionStatus.Connected
        if Error.is_error(window.handle_timeout(sock, options.addr)):
            return ConnectionStatus.ConnectionLost
        #p actualizar_barrita
    return ConnectionStatus.Connected
            
def receive_file(message_receiver: Channel, options: Options, sock: socket, expected_file_size, file)->ConnectionStatus:
    status = ConnectionStatus.Connected
    
    next_message = [0]
    bytes_received = [0]
    messages = []
    last_usefull_package_time = time.time()
    
    while time.time() - last_usefull_package_time < RECEIVE_TIMEOUT:
        msg = message_receiver.get(RECEIVE_TIMEOUT - (time.time() - last_usefull_package_time))
        if Error.is_error(msg):
            status = ConnectionStatus.ConnectionLost
            break
        print_verbose(f"Received msg of type {msg.header.type} with seq_num {msg.header.seq_num} from {options.addr}")
        if msg.header.type == Type.Fin:
            status = ConnectionStatus.FinRequested
            break
        if random.random() >= 0.1:
            heapq.heappush(messages, msg)
        else:
            print(f"\n 🗑️  Dropeamos el paquete: {msg.header.seq_num}\n") #p sacarlo
            continue

        increased_bytes = handle_send_type_messages(messages, file, next_message, bytes_received, expected_file_size, options, sock)
        if Error.is_error(increased_bytes):
            status = ConnectionStatus.Connected
            break
        if increased_bytes:
            last_usefull_package_time = time.time()
        print_progress_bar(bytes_received[0], expected_file_size, options.name)

    if (not bytes_received[0] == expected_file_size) or (expected_file_size == 0):  
        remove_file(options.src)
        print("Failed to download File")
        
    return status

def handle_send_type_messages(messages: list, file, next_message, bytes_received, expected_file_size, options: Options,sock: socket):
    increased_bytes = False
    while (len(messages) != 0) and (messages[0].header.seq_num <= next_message[0]):
        msg = heapq.heappop(messages)
        if msg.header.type != Type.Send:
            continue
        if (msg.header.seq_num == next_message[0]) and (bytes_received[0] + msg.header.payload_size <= expected_file_size):
            stored = store_package(file, options.src, msg.payload)
            if Error.is_error(stored):
                return stored
            bytes_received[0] += stored
            next_message[0] +=1
            if msg.header.payload_size != 0:
                increased_bytes = True
    Message.send_ack(next_message[0], sock, options.addr)
    print_verbose(f"Sent ack {next_message[0]} to {options.addr}\n")
    return increased_bytes

def try_open_file(path, flag):
    try:
        return open(path, flag) 
    except OSError:
        return Error.OpeningFile

def store_package(file, path, data: bytearray):
    print_verbose(f"Storing package in {path}")
    try:
        file.write(data)
    except :
        return Error.ErrorStoringData
    return len(data)
    
def remove_file(path):
    try: 
        os.remove(path)
    except:
        print("Failed to remove corrupted file")
