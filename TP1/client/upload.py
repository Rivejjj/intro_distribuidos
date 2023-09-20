import sys
import os
from message import *

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 42069
MAX_IPV4 = 2**8 -1
IPV4_SECTIONS = 4
MAX_IPV6 = 2**16 -1
IPV6_SECTIONS = 8
MIN_PORT = 2**10 
MAX_PORT = 2**16 -1

seq_num = 0

class UploadOptions:
    def __init__(self, verbosity, host, port, src, name):
        self.verbosity = verbosity
        self.host = host
        self.port = port
        self.src = src
        self.name = name

    def __str__(self):
        return f"UploadOptions(verbosity={self.verbosity}, host={self.host}, port={self.port}, src={self.src}, name={self.name})"
    

def print_help():
    print("usage : upload [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s FILEPATH ] [ - n FILENAME ]")
    print("<command description>")
    print("Options:")
    print("-h, --help            Show this help message and exit")
    print("-v, --verbose         Increase output verbosity")
    print("-q, --quiet           Decrease output verbosity")
    print("-H, --host ADDR       Server IP address")
    print("-p, --port PORT       Server port")
    print("-s, --src FILEPATH    Source file path")
    print("-n, --name FILENAME   File name")

def is_invalid_ip_segment(str, max_ip):
    base = 16
    if max_ip == MAX_IPV4:
        base = 10
    try:
        if int(str, base) > max_ip:
            return True
    except ValueError:
        return True
    return False

def is_ipv4(str):
    str = str.split('.')
    if len(str) != IPV4_SECTIONS:
        return False
    
    for i in str:
        if is_invalid_ip_segment(i, MAX_IPV4):
            return False
    return True

def is_ipv6(str):
    str = str.split(':')
    if len(str) != IPV6_SECTIONS:
        return False
    
    for i in str:
        if is_invalid_ip_segment(i, MAX_IPV6):
            return False        
    return True
    
def is_ip(str):
    return is_ipv4(str) or is_ipv6(str)

def is_not_command(arg):
    return arg not in { "-h","-v","-q","-H","-p","-s" ,"-n"}
    
def set_host(arg):
    if is_ip(arg):
        return arg
    else: 
        print("Invalid host, using default port.")
        return DEFAULT_HOST

def set_port(arg):
    try:
        port = int(arg)
        if port >= MIN_PORT and port <= MAX_PORT:
            return port
    except ValueError:
        print("Invalid port, using default port.")
        return DEFAULT_PORT
    

def set_path(arg):
    if is_not_command(arg) and ('/' in arg):
        return arg
    print("Invalid path.")
    return None

def set_filename(arg):
    if is_not_command(arg):
        return arg
    print("Invalid filename.")
    return None

def set_args(args):
    verbosity = False
    host = None #host default
    port = None
    src = None
    filename = None
    
    for i, arg in enumerate(args):
        if arg == "-q" or arg == "--quiet":
            verbosity = False
        elif arg == "-v" or arg == "--verbose":
            verbosity = True
        elif i + 1 < len(args):
            if arg == "-H" or arg == "--host":
                host = set_host(args[i + 1])
            elif arg == "-p" or arg == "--port":
                port = set_port(args[i + 1])
            elif arg == "-s" or arg == "--src":
                src = set_filename(args[i + 1])
            elif arg == "-n" or arg == "--name":
                filename = set_filename(args[i + 1])
        
    return UploadOptions(verbosity, host, port, src, filename)



def upload_file(upload_options):
    # Aquí puedes implementar la lógica para cargar el archivo al servidor
    # Utiliza la variable option según sea necesario.

    file_size = os.path.getsize(upload_options.src)
    if file_size > MAX_FILE_SIZE:
        print("Invalid file size")
        return
    
    file = open(upload_options.src, "rb")

    read = file.read(MAX_PAYLOAD_SIZE)
    while read != b'':
        message = Message(Request.Upload, upload_options.name, file_size, sys.getsizeof(read), seq_num, read)
        message.send_to(upload_options.host, upload_options.port)
        
        wait_for_ack()
        
        read = file.read(MAX_PAYLOAD_SIZE)
        

    

def main():
    args = sys.argv[1:] # [1:] para omitir el nombre del script

    # Solo es un help
    if "-h" in args or "--help" in args:
        print_help()
        return
    
    option = set_args(args)
    print(option)
    
    upload_file(option) 

if __name__ == '__main__':
    main()