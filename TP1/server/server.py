import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 42069
UP = 0
DOWN = 1

class File:
    def __init__(self, name, content):
        self.name = name
        self.content = content

def parse_upload_request(message):
    file_name_length = int(message[0])
    file_name = message[1:file_name_length+1].decode()
    file_content_length = int(message[file_name_length+1])
    file_content = message[file_name_length+2:].decode()


    print(f"File name: {file_name}\nFile content:\n{file_content}")
    return File(file_name, file_content)
    

def init_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP,UDP_PORT))    
    print("The server is ready to receive")
    
    while True:
        data, addr = sock.recvfrom(1024)
        request = int(data[0])

        if request == UP:
            file = parse_upload_request(data[1:])
            # guardar archivo en disco 
            sock.sendto("File uploaded successfully".encode(), addr) # envio mensaje de confirmacion              

        if request == DOWN:
            # enviar archivo al cliente
            print("Sending file to client")

def main():
    init_server()

main()