from multiprocessing import Queue
import threading
from lib.errors import Error


class Channel:
    def __init__(self):
        self.list = []
        self.condition = threading.Condition()

    def get(self, timeout=None):
        with self.condition:
            if len(self.list) == 0:
                if not self.condition.wait(timeout):
                    return Error.RcvTimeout
            return self.list.pop(0)

    def put(self, element):
        with self.condition:
            try:
                if len(self.list) == 0:
                    self.condition.notify()
                self.list.append(element)
            except:
                return Error.FullChannel

    def peek(self, timeout=None):
        with self.condition:
            if len(self.list) == 0:
                if not self.condition.wait(timeout):
                    return Error.RcvTimeout
            return self.list[0]

    def empty(self):
        with self.condition:
            if len(self.list) == 0:
                return True
            return False
