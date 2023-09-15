import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 6969


def connect_to_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    test = "a ver".encode()

    for i in range(0, 100):

        message = test + f"Holis{i}".encode()
        sock.sendto(message, (UDP_IP, UDP_PORT)) 
    sock.sendto(test + b"Chao", (UDP_IP, UDP_PORT))
    
    data, addr = sock.recvfrom(1024)
    print("received message: ", data.decode())
    sock.close()


def main():
    print("OK")
    connect_to_server()

main()