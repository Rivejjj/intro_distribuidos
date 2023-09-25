from enum import Enum

class Error(Enum):
    ErrorStoringData = 1
    RcvTimeout = 2
    CorruptedMessage = 3
    UnknownRequest = 4
    InvalidMessageSize = 5
    DupMessage = 6

    def __str__(self):
        return f"Error: {self.name}"

    @classmethod
    def is_error(self, value):
        return isinstance(value, Error)
            

