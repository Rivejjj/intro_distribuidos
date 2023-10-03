import socket
from enum import Enum
import unittest
import hashlib
from lib.errors import Error

# numeros son provisorios
FILE_NAME_SIZE_BYTES = 64
FILE_SIZE_BYTES = 4  # Bytes del campo FILE_SIZE del header
PAYLOAD_SIZE_BYTES = (
    2  # 2**16 payload paquete
    # Bytes del campo PAYLOAD_SIZE del header
)
SEQ_NUM_BYTES = 2
HASH_BYTES = 4


MAX_FILE_SIZE = 2 ** (8 * FILE_SIZE_BYTES - 1)

TYPE_BYTES = 1
FILE_NAME_SIZE_END = FILE_NAME_SIZE_BYTES + TYPE_BYTES
FILE_SIZE_END = (
    FILE_NAME_SIZE_END + FILE_SIZE_BYTES
)  # byte del header en el que termina file size
PAYLOAD_SIZE_END = (
    FILE_SIZE_END + PAYLOAD_SIZE_BYTES
)  # byte del header en el que termina payload size
SEQ_SIZE_END = PAYLOAD_SIZE_END + SEQ_NUM_BYTES
HEADER_SIZE = SEQ_SIZE_END + HASH_BYTES

UDP_PAYLOAD_SIZE = 65507  # 65,507 bytes for IPv4 and 65,527 bytes for IPv6
PAYLOAD_SIZE = UDP_PAYLOAD_SIZE - HEADER_SIZE


class Type(Enum):
    Send = 0
    Receive = 1
    Ack = 2
    Sync1 = 3
    Sync2 = 4
    Sync3 = 5
    Fin = 6
    FinAck = 7

    def to_bytes(self):
        return self.value.to_bytes(1, "big")

    @classmethod
    def new(self, value):
        try:
            return Type(value)
        except ValueError:
            return Error.UnknownType


class MessageHeader:
    def __init__(
        self,
        type: Type,
        file_name: str,
        file_size: int,
        payload_size: int,
        seq_num: int,
        hash: int = None,
    ):
        self.type = type
        self.file_name = file_name
        self.file_size = file_size
        self.payload_size = payload_size
        self.seq_num = seq_num
        self.hash = hash

    def __str__(self):
        representation = f"Type: {self.type}\n"
        representation += f"File name: {self.file_name}\n"
        representation += f"File size: {self.file_size}\n"
        representation += f"Payload size: {self.payload_size}\n"
        representation += f"Sequence number: {self.seq_num}\n"
        representation += f"Hash: {self.hash}\n"
        return representation

    def hashless_bytes(self):
        lenght = len(self.file_name)
        byte_seq = self.type.to_bytes()
        byte_seq += self.file_name.encode()
        byte_seq += int(0).to_bytes(FILE_NAME_SIZE_BYTES - lenght, "big")
        byte_seq += self.file_size.to_bytes(FILE_SIZE_BYTES, "big")
        byte_seq += self.payload_size.to_bytes(PAYLOAD_SIZE_BYTES, "big")
        byte_seq += self.seq_num.to_bytes(SEQ_NUM_BYTES, "big")
        return byte_seq

    def to_bytes(self):
        return self.hashless_bytes() + self.hash.to_bytes(HASH_BYTES, "big")

    def calculate_hash(self):
        return hash_bytes(self.hashless_bytes())

    @classmethod
    def from_bytes(self, data):
        type = Type.new(int.from_bytes(data[:1], byteorder="big"))
        if Error.is_error(type):
            return type
        file_name = data[1:FILE_NAME_SIZE_END].decode().rstrip("\x00")
        file_size = int.from_bytes(
            data[FILE_NAME_SIZE_END:FILE_SIZE_END], byteorder="big"
        )
        payload_size = int.from_bytes(
            data[FILE_SIZE_END:PAYLOAD_SIZE_END], byteorder="big"
        )
        seq_num = int.from_bytes(
            data[PAYLOAD_SIZE_END:SEQ_SIZE_END], byteorder="big"
            )
        hash = int.from_bytes(data[SEQ_SIZE_END:HEADER_SIZE], byteorder="big")
        return MessageHeader(
            type,
            file_name,
            file_size,
            payload_size,
            seq_num,
            hash
        )


class Message:
    def __init__(self, header: MessageHeader, payload: bytearray):
        self.header = header
        self.payload = payload

    def __str__(self):
        return self.header.__str__()  # + "\n payload: \n" + self.payload.hex()

    def __lt__(self, other):
        return self.header.seq_num < other.header.seq_num

    def __reduce__(self):
        # Devuelve una tupla con la función para reconstruir la instancia.
        # y los argumentos necesarios para esa función.
        return (
            self.__class__,
            (
                self.header,
                self.payload,
            ),
        )

    def calculate_hash(self):
        header = int.from_bytes(self.header.calculate_hash(), byteorder="big")
        payload = int.from_bytes(hash_bytes(self.payload), byteorder="big")
        return (header + payload) % (2**32)

    def send_to(self, sock: socket, addr):
        bytes_to_send = self.header.to_bytes() + self.payload
        sock.sendto(bytes_to_send, addr)  # p handelear la excepcion

    @classmethod
    # p crea un mensaje ya hasheado
    def make(
        self,
        type: Type,
        file_name: str,
        file_size: int,
        payload_size: int,
        seq_num: int,
        payload: bytearray,
    ):
        header = MessageHeader(
            type,
            file_name,
            file_size,
            payload_size,
            seq_num
        )
        msg = Message(header, payload)
        msg.header.hash = msg.calculate_hash()
        return msg

    @classmethod
    # p capas podria estar bueno pasar el nombre, capaz que no
    def send_ack(self, seq_num, sock: socket, addr):
        ack_msg = Message.make(Type.Ack, "", 0, 0, seq_num, b"")
        ack_msg.send_to(sock, addr)

    @classmethod
    def from_bytes(self, data):
        header = MessageHeader.from_bytes(data[:HEADER_SIZE])
        if Error.is_error(header):
            header
        if header.payload_size > PAYLOAD_SIZE:
            print("Received invalid message size")
            return Error.InvalidMessageSize
        if header.file_size > MAX_FILE_SIZE:
            print("Received invalid file size")
            return Error.InvalidFileSize

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


class TestMessageHeaderMethod(unittest.TestCase):
    def test_parse_and_serialize(self):
        header1 = MessageHeader(
            type=1,
            file_name="test.txt",
            file_size=2,
            payload_size=2,
            seq_num=3
        )
        bytes = header1.to_bytes()
        header2 = MessageHeader.from_bytes(bytes)

        self.assertEqual(header1.file_name, header2.file_name)
        self.assertEqual(header1.file_size, header2.file_size)
        self.assertEqual(header1.payload_size, header2.payload_size)
        self.assertEqual(header1.seq_num, header2.seq_num)
        self.assertDictEqual(vars(header1), vars(header2))


def hash_bytes(bytes: bytearray):
    # Crea un objeto hasher SHA-256
    hasher = hashlib.sha256()

    # Actualiza el hasher con los datos
    hasher.update(bytes)

    # Devuelve el hash en formato de bytes
    return hasher.digest()[:4]


if __name__ == "__main__":
    unittest.main()
