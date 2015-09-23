from contextlib import contextmanager
import threading
import time

class ReaderWriterGuard(object):
    def __init__(self):
        self.writer_lock = threading.Lock()
        self.num_reader_lock = threading.Lock()
        self.num_reader = 0

    @contextmanager
    def read_lock(self):
        with self.num_reader_lock:
            self.num_reader += 1
            if self.num_reader == 1:
                self.writer_lock.acquire()
        yield
        with self.num_reader_lock:
            self.num_reader -= 1
            if self.num_reader == 0:
                self.writer_lock.release()

    @contextmanager
    def write_lock(self):
        with self.writer_lock:
            yield

guard = ReaderWriterGuard()

def worker(num):
    with guard.read_lock():
        print 'reading %i start' % num
        time.sleep(num)
        print 'reading %i done' % num
    
    with guard.write_lock():
        print 'writing %i start' % num
        time.sleep(num)
        print 'writing %i done' % num

threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()
