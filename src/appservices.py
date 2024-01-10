import sys, traceback
import subprocess
from threading import Thread

class AppServices:
    def __init__(self):
        self.running = False
        self.main_service = None
        self.main_thread = None
        self.aux_services = []
        self.aux_threads = []

    def start_main_service(self, service):
        assert self.running == False
        self.main_service = service
        self.main_thread = wrap_runnable_in_thread(service)
        self.main_thread.start()
        for aux_thread in self.aux_threads:
            aux_thread.start()
        self.running = True

    def add_aux_service(self, service):
        self.aux_services.append(service)
        thread = wrap_runnable_in_thread(service)
        self.aux_threads.append(thread)
        if self.running:
            thread.start()

    def wait_for_main_service(self):
        assert self.running == True
        self.main_thread.join()
        self.running = False

    def wait_for_aux_services(self):
        assert self.running == False
        for aux_thread in self.aux_threads:
            aux_thread.join()

    def send_aux_message(self, msg):
        for aux_service in self.aux_services:
            aux_service.deliver_message(msg)

def wrap_runnable_in_thread(runnable):
    def wrapper():
        try:
            print("Thread running")
            runnable.run()
        except Exception as e:
            print("EXCEPTION: " + str(e))
            traceback.print_exc(file=sys.stdout)
    return Thread(target=wrapper)
