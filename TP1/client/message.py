import socket
from enum import Enum
import sys
import unittest

#numeros son provisorios
FILE_NAME_SIZE_BYTES = 64
FILE_SIZE_BYTES = 4                        #Bytes del campo FILE_SIZE del header
PAYLOAD_SIZE_BYTES = 2    #2**16 payload paquete                  #Bytes del campo PAYLOAD_SIZE del header
SEQ_NUM_BYTES = 2 

FILE_SIZE = 2**(8*FILE_SIZE_BYTES)          
PAYLOAD_SIZE = 2**(8*PAYLOAD_SIZE_BYTES) - 1

FILE_NAME_SIZE_END = FILE_NAME_SIZE_BYTES + 1
FILE_SIZE_END = FILE_NAME_SIZE_END + FILE_SIZE_BYTES #byte del header en el que termina file size
PAYLOAD_SIZE_END = FILE_SIZE_END + PAYLOAD_SIZE_BYTES #byte del header en el que termina payload size
HEADER_SIZE = PAYLOAD_SIZE_END + SEQ_NUM_BYTES

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
        self.file_name = file_name
        self.file_size = file_size
        self.payload_size = payload_size
        self.seq_num = seq_num
        self.hash = None
        #p ver lo de hash

    def print_header(self):
        print(f"Request: {self.request}\\" )
        print(f"File name: {self.file_name}\\")
        print(f"File size: {self.file_size}\\")
        print(f"Payload size: {self.payload_size}\\")
        print(f"Sequence number: {self.seq_num}\\")
        #p ver lo de hash

    def to_bytes(self):
        lenght = len(self.file_name.encode())
        tail_lenght =  FILE_NAME_SIZE_BYTES - lenght - len('\r\n')
        byte_seq = self.request.to_bytes(1, byteorder='big')
        #byte_seq += self.file_name.encode()[:FILE_NAME_SIZE_BYTES]
        byte_seq += self.file_name.encode()
        byte_seq += '\r\n'.encode()
        byte_seq += int(0).to_bytes(tail_lenght, 'big')
        byte_seq += self.file_size.to_bytes(FILE_SIZE_BYTES, 'big')
        byte_seq += self.payload_size.to_bytes(PAYLOAD_SIZE_BYTES, 'big')
        byte_seq += self.seq_num.to_bytes(SEQ_NUM_BYTES, 'big')
        print("BYTE SEQ seq num     : ",byte_seq)
        print("BITS ",bin(int.from_bytes(byte_seq[0:], byteorder='big')))
        return byte_seq
        
        #p ver lo de hash

    @classmethod
    def from_bytes(self, data):
        request = int.from_bytes(data[:1], byteorder='big')
        file_name = str(data[1:FILE_NAME_SIZE_END].decode())  
        file_name = file_name.split('\r\n')[0] #
        print(f"FILE NAME: {data[1:FILE_NAME_SIZE_END].decode()}")
        file_size = int.from_bytes(data[FILE_NAME_SIZE_END:FILE_SIZE_END], byteorder='big')
        payload_size = int.from_bytes(data[FILE_SIZE_END: PAYLOAD_SIZE_END], byteorder='big')
        seq_num = int.from_bytes(data[PAYLOAD_SIZE_END:HEADER_SIZE], byteorder='big')
        return MessageHeader(request, file_name, file_size, payload_size, seq_num)
        #hash =

 # 00000010 00000000 = \x02\x00
class Message:
    def __init__(self, request: Request, file_name: str, file_size: int, payload_size: int, seq_num: int, payload: bytearray):
        self.header = MessageHeader(request, file_name, file_size, payload_size, seq_num)
        self.payload = payload

    def __init__(self, header: MessageHeader, payload: str):
        self.header = header
        self.payload = payload
    
    def send_to(self, dest_ip, dest_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytes_to_send = self.header.to_bytes() + self.payload
        sock.sendto(bytes_to_send, (dest_ip, dest_port))
        #sock.sendto(self.header.to_bytes(), (dest_ip, dest_port))
        #sock.sendto(self.payload, (dest_ip, dest_port))

    def read(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data, addr = sock.recvfrom(PAYLOAD_SIZE)
        return self.parse(data)

    @classmethod
    def parse(self,data):
        header = MessageHeader.from_bytes(data)
        payload_size = header.payload_size
        payload = data[HEADER_SIZE: HEADER_SIZE+payload_size+1].decode()
        return Message(header, payload)


class TestStringMethods(unittest.TestCase):
    def test(self):
    
        request = 1
        file_name = "test.txt"
        file_size = 2
        payload_size = 2
        seq_num = 3
        header = MessageHeader(request, file_name, file_size, payload_size, seq_num)

        bytes = header.to_bytes()
        
        header2 = MessageHeader.from_bytes(bytes)

        self.assertEqual(header.file_name,header2.file_name)
        self.assertEqual(header.file_size,header2.file_size)
        self.assertEqual(header.payload_size,header2.payload_size)
        self.assertEqual(header.seq_num,header2.seq_num)
        self.assertDictEqual(vars(header),vars(header2))


unittest.main()
    


# 12323123- 127356832- || - 127356832-6947328741
# palitoooooooooooooooooooo
# 12345  - sock.send_to(header 81463 headerr 24798 header2347293847928347293847293873289487293847)
        
# headerUDP - askjd - hahsj - kdkjhas

# headerUDP - askjdhahsjkdkjhas


# 1273568--287 46239-87423984
#            |


#class Message:
    #def __init__(self):
        
        