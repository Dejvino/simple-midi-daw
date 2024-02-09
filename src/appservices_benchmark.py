import timeit
import queue
from collections import deque
from .appservice import AppService, AppServiceInbox
from .appservices import AppServices, AppServiceThread

msgs_per_run = 10000

class Benchmark:
    def setUp(self):
        pass
    def run(self):
        print("TEST HERE")
    def tearDown(self):
        pass

def genMessages(receiver):
    for i in range(1, msgs_per_run):
        receiver("message{i}")
    receiver("EOF")

def test_q(q):
    class B(Benchmark):
        def run(self):
            genMessages(lambda m : q.put(m))
            while not q.empty():
                m = q.get()
            assert q.empty()
    return B()

def test_queue():
    return test_q(queue.Queue())

def test_deque():
    q = deque()
    class B(Benchmark):
        def run(self):
            genMessages(lambda m : q.append(m))
            while len(q) > 0:
                m = q.popleft()
            assert len(q) == 0
    return B()

def test_AppServiceInbox():
    return test_q(AppServiceInbox())

def test_AppService():
    q = AppServiceInbox()
    service = AppService(q)
    class B(Benchmark):
        def run(self):
            genMessages(lambda m : service.deliver_message(m))
            while not q.empty():
                service.check_inbox()
            assert q.empty()
    return B()

def test_AppService_nonblocking():
    q = AppServiceInbox()
    service = AppService(q, blocking=False)
    class B(Benchmark):
        def run(self):
            genMessages(lambda m : service.deliver_message(m))
            service.check_inbox()
            assert q.empty()
    return B()

def test_AppServiceThread():
    class AuxService(AppService):
        def __init__(self, qin, qout):
            super().__init__(qin, blocking=False)
            self.qout = qout
        def on_message(self, msg):
            if msg == "EOF":
                self.qout.put(msg)
    qin = AppServiceInbox()
    qout = AppServiceInbox()
    service = AuxService(qin, qout)
    thread = AppServiceThread(service)
    class B(Benchmark):
        def setUp(self):
            thread.start()
        def run(self):
            genMessages(lambda m : qin.put(m))
            assert qout.get() == "EOF"
            assert qin.empty()
        def tearDown(self):
            thread.deliver_message("exit")
            thread.join()
    return B()

def bmark(name, gen, times):
    print("Benchmark of " + name)
    try:
        obj = gen()
        obj.setUp()
        t = timeit.timeit(lambda : obj.run(), number=times)
        obj.tearDown()
    except Exception as e:
        print("EXCEPTION: " + str(e))
        traceback.print_exc(file=sys.stdout)
        print("")
    time = t / times
    runs_per_second = 1 / time
    msgs_per_minute = msgs_per_run * runs_per_second / 60
    print(f"\t\t msgs/min: {msgs_per_minute:12.2f}")

def main():
    bmark("queue", test_queue, 10)
    bmark("deque", test_deque, 100)
    bmark("AppServiceInbox", test_AppServiceInbox, 100)
    bmark("AppService default", test_AppService, 100)
    bmark("AppService non-blocking", test_AppService_nonblocking, 100)
    bmark("AppServiceThread", test_AppServiceThread, 100)
