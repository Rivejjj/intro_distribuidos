from enum import Enum

class Error(Enum):
    ErrorStoringData = 1
    RcvTimeout = 2
    CorruptedMessage = 3
    UnknownRequest = 4
    InvalidMessageSize = 5
    InvalidFileSize = 6
    DupMessage = 7
    EmptyChannel = 8
    FullChannel = 9
    WindowFull = 10
    InvalidSeqNum = 11
    TooManyDupAck = 12


    def __str__(self):
        return f"Error: {self.name}"

    @classmethod
    def is_error(self, value):
        return isinstance(value, Error)
            

