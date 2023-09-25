import socket
from enum import Enum
import sys
import time
import unittest
import hashlib
from lib.errors import Error

#numeros son provisorios
FILE_NAME_SIZE_BYTES = 64
FILE_SIZE_BYTES = 3                        #Bytes del campo FILE_SIZE del header
PAYLOAD_SIZE_BYTES = 2    #2**16 payload paquete                  #Bytes del campo PAYLOAD_SIZE del header
SEQ_NUM_BYTES = 2
HASH_BYTES = 4


MAX_FILE_SIZE = 2**(8*FILE_SIZE_BYTES)

FILE_NAME_SIZE_END = FILE_NAME_SIZE_BYTES + 1
FILE_SIZE_END = FILE_NAME_SIZE_END + FILE_SIZE_BYTES #byte del header en el que termina file size
PAYLOAD_SIZE_END = FILE_SIZE_END + PAYLOAD_SIZE_BYTES #byte del header en el que termina payload size
SEQ_SIZE_END = PAYLOAD_SIZE_END + SEQ_NUM_BYTES
HEADER_SIZE = SEQ_SIZE_END + HASH_BYTES

UDP_PAYLOAD_SIZE = 65507 #65,507 bytes for IPv4 and 65,527 bytes for IPv6
PAYLOAD_SIZE = UDP_PAYLOAD_SIZE - HEADER_SIZE
class Request(Enum):
    Upload = 0
    Download = 1
    Ack = 2

    def to_bytes(self):
        return self.value.to_bytes(1, 'big')
    
    @classmethod
    def new(self, value):
        try:
            return Request(value)
        except ValueError:
            return Error.UnknownRequest

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
    def __init__(self, request: Request, file_name: str, file_size: int, payload_size: int, seq_num: int, hash:int =None):
        self.request = request
        self.file_name = file_name
        self.file_size = file_size
        self.payload_size = payload_size
        self.seq_num = seq_num
        self.hash = hash

    def __str__(self):
        representation = f"Request: {self.request}\n"
        representation += f"File name: {self.file_name}\n"
        representation += f"File size: {self.file_size}\n"
        representation += f"Payload size: {self.payload_size}\n"
        representation += f"Sequence number: {self.seq_num}\n"
        representation += f"Hash: {self.hash}\n"
        return representation

    def hashless_bytes(self):
        lenght = len(self.file_name)
        byte_seq = self.request.to_bytes()
        byte_seq += self.file_name.encode()
        byte_seq += int(0).to_bytes(FILE_NAME_SIZE_BYTES - lenght, 'big')
        byte_seq += self.file_size.to_bytes(FILE_SIZE_BYTES, 'big')
        byte_seq += self.payload_size.to_bytes(PAYLOAD_SIZE_BYTES, 'big')
        byte_seq += self.seq_num.to_bytes(SEQ_NUM_BYTES, 'big')
        return byte_seq
    
    def to_bytes(self):
        return self.hashless_bytes() + self.hash.to_bytes(HASH_BYTES, 'big')
        
    def calculate_hash(self):
        return hash_bytes(self.hashless_bytes())

    @classmethod
    def from_bytes(self, data):
        request = Request.new(int.from_bytes(data[:1], byteorder='big'))
        if Error.is_error(request):
            return request
        file_name = data[1:FILE_NAME_SIZE_END].decode().rstrip('\x00')
        file_size = int.from_bytes(data[FILE_NAME_SIZE_END:FILE_SIZE_END], byteorder='big')
        payload_size = int.from_bytes(data[FILE_SIZE_END: PAYLOAD_SIZE_END], byteorder='big')
        seq_num = int.from_bytes(data[PAYLOAD_SIZE_END:SEQ_SIZE_END], byteorder='big')
        hash = int.from_bytes(data[SEQ_SIZE_END: HEADER_SIZE], byteorder='big')
        return MessageHeader(request, file_name, file_size, payload_size, seq_num, hash)

class Message:
    def __init__(self, header: MessageHeader, payload: bytearray):
        self.header = header
        self.payload = payload
    
    def __str__(self):
        return self.header.__str__() #+ "\n payload: \n" + self.payload.hex()
    
    def __lt__(self, other): 
        return self.header.seq_num < other.header.seq_num
    
    def calculate_hash(self):
        header_hash = int.from_bytes(self.header.calculate_hash(), byteorder='big')
        payload_hash = int.from_bytes(hash_bytes(self.payload), byteorder='big')
        return (header_hash + payload_hash) % (2**32)
    
    def send_to(self, sock: socket, addr):
        #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytes_to_send = self.header.to_bytes() + self.payload
        print(f"\n longitud {len(bytes_to_send)}")
        sock.sendto(bytes_to_send, addr)
    

    def acknowledge(self, sock: socket, addr):
        ack_msg = Message.make(Request.Ack, self.header.file_name, self.header.file_size, 0, self.header.seq_num, b"")
        ack_msg.send_to(sock, addr)

    @classmethod
    #crea un mensaje ya hasheado
    def make(self ,request: Request, file_name: str, file_size: int, payload_size: int, seq_num: int, payload: bytearray):
        header = MessageHeader(request, file_name, file_size, payload_size, seq_num)
        msg = Message(header, payload)
        msg.header.hash = msg.calculate_hash()
        return msg

    @classmethod
    def from_bytes(self, data):
        header = MessageHeader.from_bytes(data[:HEADER_SIZE])
        if Error.is_error(header):
            header
        if header.payload_size > PAYLOAD_SIZE:
            print("Received invalid message size")
            #ver que hacer porque te pueden haber mandado lo bytes de mas en otro paquete de udp
            return Error.InvalidMessageSize
    
        msg = Message(header, data[HEADER_SIZE:])
        if msg.calculate_hash() != msg.header.hash:
            return Error.CorruptedMessage
        return msg


    @classmethod
    def recv_from(self, sock: socket.socket):
        try:
            datagram_payload, addr = sock.recvfrom(UDP_PAYLOAD_SIZE)
        except socket.timeout:
            return Error.RcvTimeout, None

        return Message.from_bytes(datagram_payload), addr


def hash_bytes(bytes: bytearray):
    # Crea un objeto hasher SHA-256
    hasher = hashlib.sha256()
    
    # Actualiza el hasher con los datos
    hasher.update(bytes)
    
    # Devuelve el hash en formato de bytes
    return hasher.digest()[:4]

class TestMessageHeaderMethods(unittest.TestCase):
    
    def test_parse_and_serialize(self):
        header1 = MessageHeader(request=1, 
                               file_name="test.txt", 
                               file_size=2, 
                               payload_size=2, 
                               seq_num=3)
        bytes = header1.to_bytes()
        header2 = MessageHeader.from_bytes(bytes)

        self.assertEqual(header1.file_name,header2.file_name)
        self.assertEqual(header1.file_size,header2.file_size)
        self.assertEqual(header1.payload_size,header2.payload_size)
        self.assertEqual(header1.seq_num,header2.seq_num)
        self.assertDictEqual(vars(header1),vars(header2))


if __name__ == '__main__':
    unittest.main()

        