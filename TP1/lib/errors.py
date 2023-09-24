from enum import Enum

class Error(Enum):
    ErrorStoringData = 1

    def __str__(self):
        self.name

    @classmethod
    def is_error(self, value):
        return value in Error.__members__.values()
            

