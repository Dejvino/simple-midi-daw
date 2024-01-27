from .appservice import AppService
from .dawconfig import DawConfig

class DawStatusOp:
    def __init__(self, operation, receiver=None):
        self.operation = operation
        self.receiver = receiver

    def perform(self, status):
        new_status, response = self.operation(status)
        if self.receiver != None:
            self.receiver.put(response)
        return new_status

class DawStatusGet(DawStatusOp):
    def __init__(self, receiver):
        def op(status):
            return status, status
        super().__init__(op, receiver)

class DawStatusSetKeyValue(DawStatusOp):
    def __init__(self, key, value, receiver):
        def op(status):
            status[key] = value
            return status, status
        super().__init__(op, receiver)

class DawStatusTestAndSetKeyValue(DawStatusOp):
    def __init__(self, key, oldvalue, newvalue, receiver):
        def op(status):
            success = False
            if status[key] == oldvalue:
                success = True
                status[key] = newvalue
            return status, {"status": status, "success": success}
        super().__init__(op, receiver)


class DawStatus(AppService):
    def __init__(self, inbox, blocking=True):
        super().__init__(inbox, blocking)
        self.status = {}

    def startup(self):
        pass

    def shutdown(self):
        pass

    def on_message(self, msg):
        if (isinstance(msg, DawStatusOp)):
            self.status = msg.perform(dict(self.status))
        else:
            print("Message in DawStatus not processed: " + repr(msg))

