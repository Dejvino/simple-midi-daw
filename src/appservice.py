import queue

class AppServiceInbox:
    def __init__(self):
        self.queue = queue.Queue()

    # Queue interface:
    def put(self, item):
        self.queue.put(item)
    def get(self, block=True, timeout=None):
        return self.queue.get(block, timeout)

    # deque interface:
    def append(self, item):
        self.put(item)
    def popleft(self):
        return self.get()

class AppService:
    def __init__(self, inbox, blocking=True):
        self.inbox = inbox
        self.active = True
        self.blocking = blocking

    def run(self):
        self.startup()
        while self.active:
            self.check_inbox()
            self.tick()
        self.shutdown()

    def deliver_message(self, msg):
        self.inbox.append(msg)

    def check_inbox(self):
        try:
            msg = self.inbox.get(self.blocking)
        except queue.Empty:
            return
        if (isinstance(msg, str) and msg == "exit"):
            self.active = False
            return
        else:
            self.on_message(msg)

    def startup(self):
        pass

    def tick(self):
        pass
        
    def on_message(self, msg):
        pass

    def shutdown(self):
        pass
