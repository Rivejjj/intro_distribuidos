import sys
import os
from message import *
from command_options import Options

seq_num = 0

def send_file(options: Options):
    file_size = os.path.getsize(options.src)
    if file_size > MAX_FILE_SIZE:
        print("Invalid file size")
        return
    
    file = open(options.src, "rb")

    read = file.read(PAYLOAD_SIZE)
    #iterar sobre read para leer todo el archivo
    while read != b'':
        message = Message.new(options.request, options.name, file_size, len(read), seq_num, read)
        print(message)
        message.send_to(options.host, options.port)
        # wait_for_ack() #si estamos en stop & wait
        
        read = file.read(PAYLOAD_SIZE)

def store_package(path, data: bytearray):
    print(f"Storing file in {path}")
    with open(path, 'ab') as file:
        file.write(data)
    return 0
