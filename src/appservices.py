import sys, traceback
import subprocess
import time
import threading
from threading import Thread

class AppServiceThread:
    def __init__(self, service):
        self.service = service
        self.thread = wrap_runnable_in_thread(service)

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

    def is_alive(self):
        return self.thread.is_alive()

    def deliver_message(self, msg):
        self.service.deliver_message(msg)

class AppServices:
    def __init__(self):
        self.running = False
        self.main_service = None
        self.main_thread = None
        self.aux_services = []
        self.aux_threads = []

    def _prepare_to_run_main_service(self, service):
        assert self.running == False
        self.main_service = service
        for aux_thread in self.aux_threads:
            if not aux_thread.is_alive:
                aux_thread.start()
        self.running = True

    # Usage 1: sync execution
    def run_main_service(self, service):
        self._prepare_to_run_main_service(service)
        try:
            service.run()
        finally:
            self.running = False

    # Usage 2: async execution
    def start_main_service(self, service):
        self._prepare_to_run_main_service(service)
        self.main_thread = AppServiceThread(service)
        self.main_thread.start()

    def wait_for_main_service(self):
        assert self.running == True
        self.main_thread.join()
        self.running = False

    def add_aux_service(self, service):
        self.aux_services.append(service)
        thread = AppServiceThread(service)
        self.aux_threads.append(thread)
        if self.running:
            thread.start()

    def wait_for_aux_services(self):
        assert self.running == False
        time.sleep(1)
        for thread in threading.enumerate():
            if (thread.name != "MainThread"):
                print("Thread still running: ", thread.name)
        for aux_thread in self.aux_threads:
            aux_thread.join()

    def send_aux_message(self, msg):
        for aux_service in self.aux_services:
            aux_service.deliver_message(msg)

def wrap_runnable_in_thread(runnable):
    def wrapper():
        try:
            print(runnable.__class__.__name__, "running.")
            runnable.run()
        except Exception as e:
            print("EXCEPTION: " + str(e))
            traceback.print_exc(file=sys.stdout)
        finally:
            print(runnable.__class__.__name__, "exiting.")
    return Thread(target=wrapper, name=f"wrapped({runnable.__class__.__name__})")
