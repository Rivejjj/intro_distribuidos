import os
from lib.message import Type
from enum import Enum


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 42069
MAX_IPV4 = 2**8 -1
IPV4_SECTIONS = 4
MAX_IPV6 = 2**16 -1
IPV6_SECTIONS = 8
MIN_PORT = 2**10 
MAX_PORT = 2**16 -1

class Options:
    def __init__(self, verbosity, addr, src, name):
        self.verbosity = verbosity
        self.addr = addr
        self.src = src
        self.name = name

    def from_args(args):
        if "-h" in args or "--help" in args:
            print_help()
            return None
        
        verbosity = False
        host = DEFAULT_HOST 
        port = DEFAULT_PORT
        src = None
        filename = "nombre que se yo" #p ver
        
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
            
        return Options(verbosity, (host, port), src, filename)

    def __str__(self):
        return f"UploadOptions(verbosity={self.verbosity}, host={self.addr[0]}, port={self.addr[1]}, src={self.src}, name={self.name})"
    

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

# def print_help_upload():
#     print("usage : upload [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s FILEPATH ] [ - n FILENAME ]")
#     print("<command description>")
#     print("Options:")
#     print("-h, --help            Show this help message and exit")
#     print("-v, --verbose         Increase output verbosity")
#     print("-q, --quiet           Decrease output verbosity")
#     print("-H, --host ADDR       Server IP address")
#     print("-p, --port PORT       Server port")
#     print("-s, --src FILEPATH    Source file path")
#     print("-n, --name FILENAME   File name")

# def print_help_download():
#     print("usage : download [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - d FILEPATH ] [ - n FILENAME ]")
#     print("<command description>")
#     print("Options:")
#     print("-h, --help            Show this help message and exit")
#     print("-v, --verbose         Increase output verbosity")
#     print("-q, --quiet           Decrease output verbosity")
#     print("-H, --host ADDR       Server IP address")
#     print("-p, --port PORT       Server port")
#     print("-s, --src FILEPATH    Source file path")
#     print("-n, --name FILENAME   File name")

# Si se aprueba esa implementacion, cambiar a nombre set_path
def set_path_definitive(path):
    if os.path.exists(path):
        return path
    return None

class Arguments(Enum):
    Helpito = 1 #help es palabra reservada
    Verbose = 2
    Quiet = 3
    Host = 4
    Port = 5
    Src = 6
    Name = 7
    Dst = 8
    Storage = 9

    def print_help(self):
        if self == Arguments.Helpito:
            print("-h , -- help     show this help message and exit")
        elif self == Arguments.Verbose:
            print("-v , -- verbose  increase output verbosity")
        elif self == Arguments.Quiet:
            print("-q , -- quiet    decrease output verbosity")
        elif self == Arguments.Host:
            print("-H , -- host     server IP address")
        elif self == Arguments.Port:
            print("-p , -- port     server port")
        elif self == Arguments.Src:
            print("-s , -- src      source file path")
        elif self == Arguments.Name:
            print("-n , -- name     file name")
        elif self == Arguments.Dst:
            print("-d , -- dst      destination file path")
        elif self == Arguments.Storage:
            print("-s , -- storage  storage file path")
        else:
            print(f"No help for this argument: {self}")

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if self.value == Arguments.Helpito.value:
            return other == "-h" or other == "--help"
        elif self.value == Arguments.Verbose.value:
            return other == "-v" or other == "--verbose"
        elif self.value == Arguments.Quiet.value:
            return other == "-q" or other == "--quiet"
        elif self.value == Arguments.Host.value:
            return other == "-H" or other == "--host"
        elif self.value == Arguments.Port.value:
            return other == "-p" or other == "--port"
        elif self.value == Arguments.Src.value:
            return other == "-s" or other == "--src"
        elif self.value == Arguments.Name.value:
            return other == "-n" or other == "--name"
        elif self.value == Arguments.Dst.value:
            return other == "-d" or other == "--dst"
        elif self.value == Arguments.Storage.value:
            return other == "-s" or other == "--storage"
        else:
            return False
    
    def default(self):
        if self == Arguments.Quiet:
            return False
        if self == Arguments.Verbose:
            return False
        elif self == Arguments.Host:
            return DEFAULT_HOST
        elif self == Arguments.Port:
            return DEFAULT_PORT
        elif self == Arguments.Src:
            return None
        elif self == Arguments.Name:
            return None
        elif self == Arguments.Dst:
            return None

    def get_index(self, args):
        if len(args) == 0:
            return None
        try:
            index =  args.index(self)
        except ValueError:
            return None
        return index
    
    def get_argument(self, args):
        index = self.get_index(args)
        if index == None:
            return self.default()
        
        # Sin argumentos
        if self == Arguments.Verbose:
            return False
        elif self == Arguments.Quiet:
            return True

        # Con argumentos
        index += 1 # El argumento esta en la siguiente posicion
        if index >= len(args):
            return self.default()
        
        value = self.valid_value(args[index])
        return value if value != None else self.default()


    def valid_value(self, arg):
        if self == Arguments.Host:
            return set_host(arg)
        elif self == Arguments.Port:
            return set_port(arg)
        elif self == Arguments.Src:
            return set_path_definitive(arg) # Nose porque llamabamos a set_filename pero lo dejo como esta
        elif self == Arguments.Name: 
            return set_filename(arg) # Nose porque llamabamos a set_filename pero lo dejo como esta
        elif self == Arguments.Dst:
            return set_path_definitive(arg) # Nose porque llamabamos a set_filename pero lo dejo como esta
        elif self == Arguments.Storage:
            return set_path_definitive(arg) # Nose porque llamabamos a set_filename pero lo dejo como esta
        else:
            return None

class OptionsUpload:
    def __init__(self, verbosity, addr, src, name):
        self.verbosity = verbosity
        self.addr = addr
        self.src = src
        self.name = name

    @classmethod
    def valid_arguments(self):
        return {Arguments.Verbose: None, Arguments.Quiet: None, Arguments.Host: None, Arguments.Port: None, Arguments.Src: None, Arguments.Name: None}
    
    def from_args(args):
        if "-h" in args or "--help" in args:
            OptionsUpload.upload_help()
            return None
        
        valid_args = OptionsUpload.valid_arguments()
        for arg in valid_args:
            valid_args[arg] = arg.get_argument(args)
        
        return OptionsUpload(
                    valid_args[Arguments.Quiet], # Porque por default es False
                    (valid_args[Arguments.Host], valid_args[Arguments.Port]),
                    valid_args[Arguments.Src],
                    valid_args[Arguments.Name]
                    )

    def __str__(self):
        return f"UploadOptions(verbosity={self.verbosity}, host={self.addr[0]}, port={self.addr[1]}, src={self.src}, name={self.name})"

    def upload_help():
        print("usage : upload [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s FILEPATH ] [ - n FILENAME ]")
        print("<command description>")
        print("Options:")
        args = OptionsUpload.valid_arguments()
        for arg in args:
            arg.print_help()

class OptionsDownload:
    def __init__(self, verbosity, addr, dst, name):
        self.verbosity = verbosity
        self.addr = addr
        self.dst = dst
        self.name = name

    @classmethod
    def valid_arguments(self):
        return {Arguments.Verbose: None, Arguments.Quiet: None, Arguments.Host: None, Arguments.Port: None, Arguments.Dst: None, Arguments.Name: None}
    
    def from_args(args):
        if "-h" in args or "--help" in args:
            OptionsDownload.download_help()
            return None
        
        valid_args = OptionsDownload.valid_arguments()
        for arg in valid_args:
            valid_args[arg] = arg.get_argument(args)
        
        return OptionsDownload(
                    valid_args[Arguments.Quiet], # Porque por default es False
                    (valid_args[Arguments.Host], valid_args[Arguments.Port]),
                    valid_args[Arguments.Dst],
                    valid_args[Arguments.Name]
                    )

    def __str__(self):
        return f"OptionsDownload(verbosity={self.verbosity}, host={self.addr[0]}, port={self.addr[1]}, dst={self.dst}, name={self.name})"

    def download_help():
        print("usage : download [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - d FILEPATH ] [ - n FILENAME ]")
        print("<command description>")
        print("Options:")
        args = OptionsDownload.valid_arguments()
        for arg in args:
            arg.print_help()

class OptionsStartServer:
    def __init__(self, verbosity, addr, storage):
        self.verbosity = verbosity
        self.addr = addr
        self.storage = storage

    @classmethod
    def valid_arguments(self):
        return {Arguments.Verbose: None, Arguments.Quiet: None, Arguments.Host: None, Arguments.Port: None, Arguments.Storage: None}
    
    def from_args(args):
        if "-h" in args or "--help" in args:
            OptionsStartServer.start_server_help()
            return None
        
        valid_args = OptionsStartServer.valid_arguments()
        for arg in valid_args:
            valid_args[arg] = arg.get_argument(args)
        
        return OptionsStartServer(
                    valid_args[Arguments.Quiet], # Porque por default es False
                    (valid_args[Arguments.Host], valid_args[Arguments.Port]),
                    valid_args[Arguments.Storage]
                    )

    def __str__(self):
        return f"OptionsStartServer(verbosity={self.verbosity}, host={self.addr[0]}, port={self.addr[1]}, storage={self.storage})"

    def start_server_help():
        print("usage : download [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - d FILEPATH ] [ - n FILENAME ]")
        print("<command description>")
        print("Options:")
        args = OptionsStartServer.valid_arguments()
        for arg in args:
            arg.print_help()

