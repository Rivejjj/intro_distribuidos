from lib.command_options import verbose

def print_verbose(string):
    if verbose[0]:
        print(string)