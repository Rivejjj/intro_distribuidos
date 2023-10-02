import os
from lib.errors import Error
from lib.message import Type

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 41970
MAX_IPV4 = 2**8 - 1
IPV4_SECTIONS = 4
MAX_IPV6 = 2**16 - 1
IPV6_SECTIONS = 8
MIN_PORT = 2**10
MAX_PORT = 2**16 - 1
DEFAULT_WINDOW_SIZE = 1
DEFAULT_SERVER_STORAGE_PATH = "./server_files/"

verbose = [False]


class Options:
    def __init__(self, addr, src, name=None, window_size=None):
        self.addr = addr
        self.src = src
        self.name = name
        self.window_size = window_size  # -w

    @classmethod
    def upload_from_args(self, args):
        if "-h" in args or "--help" in args:
            print_upload_help()
            return None

        host = DEFAULT_HOST
        port = DEFAULT_PORT
        src = None
        filename = None
        window_size = DEFAULT_WINDOW_SIZE
        global verbose

        for i, arg in enumerate(args):
            if arg == "-q" or arg == "--quiet":
                verbose[0] = False
            elif arg == "-v" or arg == "--verbose":
                print("Encontre un -v")  # eliminar
                verbose[0] = True
            elif i + 1 < len(args):
                if arg == "-H" or arg == "--host":
                    host = validate_host(args[i + 1])
                elif arg == "-p" or arg == "--port":
                    port = validate_port(args[i + 1])
                elif arg == "-s" or arg == "--src":
                    src = validate_file_path(args[i + 1])
                elif arg == "-n" or arg == "--name":
                    filename = validate_filename(args[i + 1])
                elif arg == "-w" or arg == "--window":
                    window_size = validate_window_size(args[i + 1])
        if src == None:
            print("Invalid source argument")
            return Error.InvalidArgs
        if filename == None:
            filename = os.path.basename(src)

        return Options((host, port), src, filename, window_size)

    @classmethod
    def download_from_args(self, args):
        if "-h" in args or "--help" in args:
            print_download_help()
            return None

        host = DEFAULT_HOST
        port = DEFAULT_PORT
        dest = None
        filename = None
        global verbose

        for i, arg in enumerate(args):
            if arg == "-q" or arg == "--quiet":
                verbose[0] = False
            elif arg == "-v" or arg == "--verbose":
                print("Encontre una -v")  # Eliminar
                verbose[0] = True
            elif i + 1 < len(args):
                if arg == "-H" or arg == "--host":
                    host = validate_host(args[i + 1])
                elif arg == "-p" or arg == "--port":
                    port = validate_port(args[i + 1])
                elif arg == "-d" or arg == "--dst":
                    dest = validate_directory_path(args[i + 1])
                elif arg == "-n" or arg == "--name":
                    filename = validate_filename(args[i + 1])
        if dest == None:
            print("Invalid destination argument")
            return Error.InvalidArgs
        if filename == None:
            print("Invalid filename argument")
            return Error.InvalidArgs

        return Options((host, port), dest, filename)

    @classmethod
    def server_from_args(self, args):
        if "-h" in args or "--help" in args:
            print_server_help()
            return None

        host = DEFAULT_HOST
        port = DEFAULT_PORT
        storage = None
        window_size = DEFAULT_WINDOW_SIZE
        global verbose

        for i, arg in enumerate(args):
            if arg == "-q" or arg == "--quiet":
                verbose[0] = False
            elif arg == "-v" or arg == "--verbose":
                verbose[0] = True
            elif i + 1 < len(args):
                if arg == "-H" or arg == "--host":
                    host = validate_host(args[i + 1])
                elif arg == "-p" or arg == "--port":
                    port = validate_port(args[i + 1])
                elif arg == "-s" or arg == "--storage":
                    storage = validate_directory_path(args[i + 1])
                elif arg == "-w" or arg == "--window":
                    window_size = validate_window_size(args[i + 1])
        if storage == None:
            print("Storage not found, the directory will be created by default.")
            storage = create_dir(DEFAULT_SERVER_STORAGE_PATH)

        return Options((host, port), storage, window_size=window_size)

    def __str__(self):
        return f"UploadOptions(host={self.addr[0]}, port={self.addr[1]}, src={self.src}, name={self.name}, window_size={self.window_size})"


def print_generic_help():
    print("<command description>")
    print("Options:")
    print("-h, --help            Show this help message and exit")
    print("-v, --verbose         Increase output verbosity")
    print("-q, --quiet           Decrease output verbosity")
    print("-H, --host ADDR       Server IP address")
    print("-p, --port PORT       Server port")


def print_upload_help():
    print(
        "usage : upload [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s FILEPATH ] [ - n FILENAME ] [-w NUMBER]"
    )
    print_generic_help()
    print("-n, --name FILENAME   File name")
    print("-s, --src FILEPATH          Source file path")
    print("-w, --window WINDOW SIZE    Window size")


def print_download_help():
    print(
        "usage : download [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - d FILEPATH ] [ - n FILENAME ]"
    )
    print_generic_help()
    print("-n, --name FILENAME   File name")
    print("-d , --dst destination file path")


def print_server_help():
    print(
        "usage : start - server [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s DIRPATH ] [-w NUMBER]"
    )
    print_generic_help()
    print("-s , --storage storage dir path")
    print("-w, --window WINDOW SIZE    Window size")


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
    str = str.split(".")
    if len(str) != IPV4_SECTIONS:
        return False

    for i in str:
        if is_invalid_ip_segment(i, MAX_IPV4):
            return False
    return True


def is_ipv6(str):
    str = str.split(":")
    if len(str) != IPV6_SECTIONS:
        return False

    for i in str:
        if is_invalid_ip_segment(i, MAX_IPV6):
            return False
    return True


def is_ip(str):
    return is_ipv4(str) or is_ipv6(str)


def is_not_command(arg):
    if len(arg) == 0:
        return False
    return arg[0] != "-"


def validate_host(arg):
    if is_ip(arg):
        return arg
    else:
        print("Invalid host, using default port.")
        return DEFAULT_HOST


def validate_port(arg):
    try:
        port = int(arg)
        if port >= MIN_PORT and port <= MAX_PORT:
            return port
    except ValueError:
        print("Invalid port, using default port.")
        return DEFAULT_PORT


def validate_filename(arg):
    if is_not_command(arg):
        return arg
    print("Invalid filename, using last part of path.")
    return None


def validate_file_path(path):
    if os.path.exists(path) and os.path.isfile(path):
        return path
    return None


def validate_directory_path(path):
    if os.path.exists(path) and os.path.isdir(path):
        return path
    return None


def validate_window_size(size):
    try:
        size = int(size)
        if size > 0:
            return size
    except ValueError:
        print("Invalid window size, using default window size.")
    return DEFAULT_WINDOW_SIZE


def create_dir(path):
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except OSError:
            print("Could not create the directory")
            return Error.CreatingStorage
    return path
