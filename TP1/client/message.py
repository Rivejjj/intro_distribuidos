import socket
from enum import Enum

#numeros son provisorios
MAX_FILE_NAME_SIZE = 64
FILE_SIZE_BYTES = 3
PAYLOAD_SIZE_BYTES = 2
SEQ_NUM_BYTES = 2
MAX_PAYLOAD_SIZE = 2**(8*PAYLOAD_SIZE_BYTES) -1
MAX_FILE_SIZE = 2**(8*FILE_SIZE_BYTES)

class Request(Enum):
    Upload = 0
    Download = 1

# formato:
    #     2 bits 0: request (UPLOAD=0, DOWNLOAD=1, ack= 2, solicitud de files disponibles = 3)
    #     32 u 64 bytes para el nombre del archivo
    #     x bytes para 2gs: longitud del archivo (por ahora no es necesaria) //cantidad de paquetes (dividido el tam max)
    #     2 bytes longitud [0-65535] del payload variable con tope superior
    #     sequence number
    #     Hash

    # a decidir: se manda un ack y despues el archivo o directamente el archivo?

    #     payload bytes n+1 a m: contenido del archivo (solo si request es UPLOAD)

class MessageHeader:
    def __init__(self, request: Request, file_name: str, file_size: int, payload_size: int, seq_num: int):
        self.request = request
        self.file_name = file_name.encode()[:MAX_FILE_NAME_SIZE]
        self.file_size = file_size
        self.payload_size = payload_size
        self.seq_num = seq_num
        self.hash = None
        #p ver lo de hash

    def to_bytes(self):
        byte_seq = self.request.to_bytes()
        byte_seq += self.file_name
        byte_seq += self.file_size.to_bytes(FILE_SIZE_BYTES, 'big')                     #p chequear overflow
        byte_seq += self.payload_size.to_bytes(PAYLOAD_SIZE_BYTES, 'big')
        byte_seq += self.seq_num.to_bytes(SEQ_NUM_BYTES, 'big')
        #p ver lo de hash

class Message:
    def __init__(self, request: Request, file_name: str, file_size: int, payload_size: int, seq_num: int, payload: bytearray):
        self.header = MessageHeader(request, file_name, file_size, payload_size, seq_num)
        self,payload = payload

    def send_to(self, dest_ip, dest_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytes_to_send = self.header.to_bytes() + self.payload
        sock.sendto(, (dest_ip, dest_port))
        #sock.sendto(self.header.to_bytes(), (dest_ip, dest_port))
        #sock.sendto(self.payload, (dest_ip, dest_port))

12323123- 127356832- || - 127356832-6947328741
palitoooooooooooooooooooo
12345  - sock.send_to(header 81463 headerr 24798 header2347293847928347293847293873289487293847)
        
headerUDP - askjd - hahsj - kdkjhas

headerUDP - askjdhahsjkdkjhas


1273568--287 46239-87423984
           |


#class Message:
    #def __init__(self):
        
        