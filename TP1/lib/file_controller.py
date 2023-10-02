import os
import threading
from lib.errors import Error

class FileOpening():
    def __init__(self, path):
        self.readers = 0
        self.writing = False
        self.path = path
    
    def try_read_lock(self):
        if self.writing:
            return Error.CannotReadFromFile
        self.readers += 1
        return open(self.path, "rb")
    
    def try_write_lock(self):
        if (self.writing) or (self.readers > 0):
            return Error.CannotWriteFile
        self.writing = True
        return open(self.path, "wb")

    def release_read_lock(self, file):
        self.readers -=1
        file.close()
        
    def release_write_lock(self,file):
        self.writing = False
        file.close()
    
class FileController():
    def __init__(self):
        self.dict = {}
        self.lock = threading.Lock()        

    def try_read_lock(self, path):
        if (not os.path.exists(path)) or (not os.path.isfile(path)):
            return Error.FileDoesNotExist
        try:
            self.lock.acquire()
        except:
            return Error.ErrorSharingData
            
        name = os.path.basename(path)
        self.dict[name] = self.dict.get(name, FileOpening(path))
        file = self.dict[name].try_read_lock()

        self.lock.release()
        return file 

    def try_write_lock(self, path):
        try:
            self.lock.acquire()
        except:
            return Error.ErrorSharingData
        name = os.path.basename(path)
        self.dict[name] = self.dict.get(name, FileOpening(path))
        file =  self.dict[name].try_write_lock()

        self.lock.release()
        return file
    
    def release_read_lock(self, file):
        try:
            self.lock.acquire()
        except:
            return Error.ErrorSharingData
        self.dict[os.path.basename(file.name)].release_read_lock(file)
        self.lock.release()
        

    def release_write_lock(self, file):
        try:
            self.lock.acquire()
        except:
            return Error.ErrorSharingData
        self.dict.pop(os.path.basename(file.name)).release_write_lock(file)
        self.lock.release()