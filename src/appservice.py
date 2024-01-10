class AppService:
    def __init__(self, inbox):
        self.inbox = inbox
        self.active = True

    def run(self):
        self.startup()
        while self.active:
            self.check_inbox()
            self.tick()
        self.shutdown()

    def deliver_message(self, msg):
        self.inbox.append(msg)

    def check_inbox(self):
        while self.inbox:
            msg = self.inbox.popleft()
            if (msg == "exit"):
                self.active = False
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
