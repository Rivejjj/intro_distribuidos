import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 6969


def init_server():
    suck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    suck.bind((UDP_IP,UDP_PORT))

    while True:
        data, addr = suck.recvfrom(1024)
        header = data[0:5].decode()
        data = data[5:]
        print(f"received message: \nHeader: {header}\n, Data: {data}")
        if data == b"Chao":
            suck.sendto(b"OK, chao", addr)
            break
        

    print("recieved from: ", addr)
    suck.sendto(b"OK, chao", addr)
    suck.close()




def main():
    print("OK SV")
    init_server()

main()