import socket
from enum import Enum
import sys
import time
import unittest
from errors import Error

#numeros son provisorios
FILE_NAME_SIZE_BYTES = 64
FILE_SIZE_BYTES = 3                        #Bytes del campo FILE_SIZE del header
PAYLOAD_SIZE_BYTES = 2    #2**16 payload paquete                  #Bytes del campo PAYLOAD_SIZE del header
SEQ_NUM_BYTES = 2 


MAX_FILE_SIZE = 2**(8*FILE_SIZE_BYTES)

FILE_NAME_SIZE_END = FILE_NAME_SIZE_BYTES + 1
FILE_SIZE_END = FILE_NAME_SIZE_END + FILE_SIZE_BYTES #byte del header en el que termina file size
PAYLOAD_SIZE_END = FILE_SIZE_END + PAYLOAD_SIZE_BYTES #byte del header en el que termina payload size
HEADER_SIZE = PAYLOAD_SIZE_END + SEQ_NUM_BYTES

UDP_PAYLOAD_SIZE = 65507 #65,507 bytes for IPv4 and 65,527 bytes for IPv6
PAYLOAD_SIZE = UDP_PAYLOAD_SIZE - HEADER_SIZE
class Request(Enum):
    Upload = 0
    Download = 1
    Ack = 2

    def to_bytes(self):
        return self.value.to_bytes(1, 'big')

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

    def __str__(self):
        representation = f"Request: {self.request}\n"
        representation += f"File name: {self.file_name}\n"
        representation += f"File size: {self.file_size}\n"
        representation += f"Payload size: {self.payload_size}\n"
        representation += f"Sequence number: {self.seq_num}\n"
        return representation

    def to_bytes(self):
        lenght = len(self.file_name)
        byte_seq = self.request.to_bytes()
        byte_seq += self.file_name.encode()
        byte_seq += int(0).to_bytes(FILE_NAME_SIZE_BYTES - lenght, 'big')
        byte_seq += self.file_size.to_bytes(FILE_SIZE_BYTES, 'big')
        byte_seq += self.payload_size.to_bytes(PAYLOAD_SIZE_BYTES, 'big')
        byte_seq += self.seq_num.to_bytes(SEQ_NUM_BYTES, 'big')
        # print("BYTE SEQ seq num     : ",byte_seq)
        # print("BITS ",bin(int.from_bytes(byte_seq[0:], byteorder='big')))
        #print(f"el to bytes del header es {byte_seq}")
        return byte_seq
        
        #p ver lo de hash

    @classmethod
    def from_bytes(self, data):
        request = int.from_bytes(data[:1], byteorder='big')
        file_name = data[1:FILE_NAME_SIZE_END].decode().rstrip('\x00')
        file_size = int.from_bytes(data[FILE_NAME_SIZE_END:FILE_SIZE_END], byteorder='big')
        payload_size = int.from_bytes(data[FILE_SIZE_END: PAYLOAD_SIZE_END], byteorder='big')
        seq_num = int.from_bytes(data[PAYLOAD_SIZE_END:HEADER_SIZE], byteorder='big')
        return MessageHeader(request, file_name, file_size, payload_size, seq_num)
        #hash =


class Message:
    def __init__(self, header: MessageHeader, payload: bytearray):
        self.header = header
        self.payload = payload
    
    def __str__(self):
        return self.header.__str__() #+ "\n payload: \n" + self.payload.hex()
    
    def new(request: Request, file_name: str, file_size: int, payload_size: int, seq_num: int, payload: bytearray):
        header = MessageHeader(request, file_name, file_size, payload_size, seq_num)
        return Message(header, payload)
    
    def send_to(self, sock: socket, addr):
        #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytes_to_send = self.header.to_bytes() + self.payload
        print(f"\n longitud {len(bytes_to_send)}")
        sock.sendto(bytes_to_send, addr)
        ##sock.sendto(self.header.to_bytes(), (dest_ip, dest_port))
        #sock.sendto(self.payload, (dest_ip, dest_port))

    def acknowledge(self, sock: socket, addr):
        ack_msg = Message.new(Request.Ack, self.header.file_name, self.header.file_size, 0, self.header.seq_num, b"")
        ack_msg.send_to(sock, addr)


    @classmethod
    def from_bytes(self, data):
        header = MessageHeader.from_bytes(data[:HEADER_SIZE])
        if header.payload_size > PAYLOAD_SIZE:
            print("Received invalid message size")
            #ver que hacer porque te pueden haber mandado lo bytes de mas en otro paquete de udp
            return None
    
        return Message(header, data[HEADER_SIZE:])

    @classmethod
    def recv_from(self, socket: socket.socket):
        try:
            datagram_payload, addr = socket.recvfrom(UDP_PAYLOAD_SIZE)
        except socket.timeout:
            return Error.RcvTimeout

        return Message.from_bytes(datagram_payload), addr
# try:
#     # Espera la respuesta durante el tiempo especificado
#     data, addr = sock.recvfrom(1024)
#     print("Respuesta recibida:", data.decode())
# except socket.timeout:
#     print("Tiempo de espera agotado. No se recibió ninguna respuesta.")
# finally:
#     sock.close()


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
    


# 12323123- 127356832- || - 127356832-6947328741
# palitoooooooooooooooooooo
# 12345  - sock.send_to(header 81463 headerr 24798 header2347293847928347293847293873289487293847)
        
# headerUDP - askjd - hahsj - kdkjhas

# headerUDP - askjdhahsjkdkjhas


# 1273568--287 46239-87423984
#            |


#class Message:
    #def __init__(self):
        
        