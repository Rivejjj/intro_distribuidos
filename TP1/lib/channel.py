from multiprocessing import Queue
from lib.errors import Error

class Channel():
    def __init__(self):
        self.queue = Queue()

    def __str__(self):
        return str(self.queue)

    def get(self, timeout=None):
        try:
            return self.queue.get(True, timeout)
        except:
            return Error.EmptyChannel
        
    def put(self, message, timeout=None):
        try:
            self.queue.put(message, True, timeout)
        except:
            return Error.FullChannel
    
    def empty(self):
        return self.queue.empty()