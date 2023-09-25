import socket
import os
import time
import random
import heapq
import threading
from multiprocessing import SimpleQueue
from lib.message import *
from lib.transfer_file import store_package
from lib.errors import Error
from lib.message import Message

UNIDIRECTIONAL_PIPE = False
UDP_IP = "127.0.0.1"
UDP_PORT = 42069
UP = 0
DOWN = 1
TIMEOUT = 10



def store_package_server(file_name, payload):
    print("entra a store package")
    if not os.path.exists('./server_files/'):
        try:
            os.mkdir('./server_files/')
        except OSError: 
            print("fue el OS")
            return -Error.ErrorStoringData
    
    path = './server_files/' + file_name
    return store_package(path, payload)

def receive_file(message_receiver: SimpleQueue, addr, finished_queue: SimpleQueue):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.bind((UDP_IP,UDP_PORT))
    #sock.settimeout(TIMEOUT) #p ver este valor
    print("The server is ready to receive")

    next_message = [0]
    messages = []
    received_bytes = 0

    while True:
        print("entra a while de receive file")
        msg = message_receiver.get()
        print("sigue despues de message_receiver.get()")
        if random.random() > 0.5:
            heapq.heappush(messages, msg)
            received_bytes += msg.header.payload_size
        else:
            print(f"\n Dropeamos el paquete {msg.header.seq_num}\n")
        print(msg)
        
        result = handle_upload_messages(messages, next_message, addr, sock)
        if Error.is_error(result):
            print(result)
            break
        if received_bytes == msg.header.file_size:
            break
    
    #hacer el fin

    finished_queue.put(addr)
    
    

def handle_upload_message(msg: Message):
    result = store_package_server(msg.header.file_name, msg.payload)
    if Error.is_error(result): 
        return result
    #msg.acknowledge(sock, addr)

#ver que hacer con lo de que te manden mas packetes de los que dice el header
def handle_upload_messages(messages: list, next_message, addr, sock: socket):
    print(f"{messages}, next msg {next_message}")
    last_handled_msg = None
    result = None
    while (len(messages) != 0) and (messages[0].header.seq_num <= next_message[0]):
        print(next_message[0])
        msg = heapq.heappop(messages)
        if (msg.header.seq_num < next_message[0]) or (msg.header.type != Type.Send):
            continue
        
        result = handle_upload_message(msg)
        if Error.is_error(result):
            break
        next_message[0] += 1
        last_handled_msg = msg
    if last_handled_msg!= None:
        last_handled_msg.acknowledge(sock, addr)
    return result
    
class ClientManager:
    def __init__(self, addr, first_msg_type, finished_clients):
        queue = SimpleQueue()

        self.addr = addr
        self.queue = queue
        if first_msg_type == Type.Send:
            self.join_handle = threading.Thread(target=receive_file, args=(queue, addr, finished_clients))
        self.join_handle.start()
    
    def try_join(self):
        if not self.join_handle.is_alive():
            print("joinea el thread")
            self.join_handle.join()
            return True
        return False

    def send_message(self, msg: Message):
        self.queue.put(msg)

def server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP,UDP_PORT))
    sock.settimeout(TIMEOUT)
    clients = {}
    finished_clients = SimpleQueue()

    while True:
        print(clients)

        msg, addr = Message.recv_from(sock)
        print("SERVIDOR: recibi")
        if not Error.is_error(msg):
            clients[addr] = clients.get(addr, ClientManager(addr, msg.header.type, finished_clients)) #crear un thread x ip de cliente si no está creado
            print("SERVIDOR: pase")             #guarda cuando se corre dos veces seguidas, si no termino lo anterior hay que dropear el handshake

            clients[addr].send_message(msg) #enviar paquete x pipe a thread correspondiente
        
        while not finished_clients.empty():
            addr = finished_clients.get()
            #print("TERMINOOOOOO")
            if clients.pop(addr).try_join():
                print("JOINEEEEEEEEEE")
        print("SERVIDOR: pase while")

        

    #sock.close()
        
        
        


def main():
    #init_server()
    server()

main()



# import socket

# # Crea un socket UDP
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# # Establece un tiempo de espera en segundos
# timeout = 5

# try:
#     # Espera la respuesta durante el tiempo especificado
#     sock.settimeout(timeout)
#     data, addr = sock.recvfrom(1024)
#     print("Respuesta recibida:", data.decode())
# except socket.timeout:
#     print("Tiempo de espera agotado. No se recibió ninguna respuesta.")
# finally:
#     sock.close()





