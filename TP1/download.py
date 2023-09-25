from lib.transfer_file import *
from lib.command_options import *

def main():
    args = sys.argv[1:] # [1:] para omitir el nombre del script

    command = Options.from_args(args, Type.Receive)
    if (command == None):
        return
    receive_file()

main()