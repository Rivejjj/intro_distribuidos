from lib.command_options import verbose

MAX_PROGRESS_BAR_LEN = 50


def print_verbose(string):
    if verbose[0]:
        print(string)


def print_progress_bar(proccesed_bytes, total_bytes, file_name):
    if verbose[0]:
        return
    progress = round(proccesed_bytes / total_bytes, 2)
    progress_bar_len = int((progress * MAX_PROGRESS_BAR_LEN))
    progress_bar = f"{file_name} |" + "#" * progress_bar_len
    progress_bar += " " * (MAX_PROGRESS_BAR_LEN - progress_bar_len) + f"| {progress}"

    # os.system('clear')
    print(progress_bar)
