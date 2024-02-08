from collections import deque
import queue
import time

class QDek(deque):
    def __init__(self):
        super().__init__()
    
    # Queue facade:
    def put(self, item):
        self.append(item)
    def get(self, block=True, timeout=None):
        try:
            while block and len(self) == 0:
                time.sleep(0)
            return self.popleft()
        except IndexError:
            raise queue.Empty()
    def empty(self):
        return len(self) == 0

class AppServiceInbox:
    def __init__(self):
        self.queue = QDek()

    # Queue interface:
    def put(self, item):
        self.queue.put(item)
    def get(self, block=True, timeout=None):
        return self.queue.get(block, timeout)
    def get_nowait(self, timeout=None):
        return self.get(block=False, timeout=timeout)
    def empty(self):
        return self.queue.empty()

    # deque interface:
    def append(self, item):
        self.put(item)
    def popleft(self):
        return self.get()

class AppService:
    def __init__(self, inbox, blocking=True):
        assert isinstance(inbox, AppServiceInbox)
        self.inbox = inbox
        self.active = True
        self.blocking = blocking

    def run(self):
        self.startup()
        while self.active:
            self.tick()
            self.check_inbox()
        self.shutdown()

    def deliver_message(self, msg):
        self.inbox.append(msg)

    def check_inbox(self):
        looping = True
        while looping:
            try:
                msg = self.inbox.get(self.blocking)
                if (isinstance(msg, str) and msg == "exit"):
                    self.active = False
                else:
                    self.on_message(msg)
            except queue.Empty:
                looping = False
            looping = looping and not self.blocking

    def startup(self):
        pass

    def tick(self):
        pass
        
    def on_message(self, msg):
        pass

    def shutdown(self):
        pass
