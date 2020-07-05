import threading
from   queue import Queue
from   subprocess import Popen,PIPE,STDOUT
import json
import traceback
import signal

import time

class Lean_Server:
    def __init__( self ):
        self.proc     = None    # Process handle object
        self.t_worker = None    # Worker thread object

        self.tx_queue = Queue() # Message transmission queue
        self.rx_queue = Queue() # Message reception    queue

        self.started  = threading.Event()
        self.has_resp = threading.Event()

    def start(self):
        self.t_worker = threading.Thread(target=self.worker)
        self.t_worker.start()

    def stop( self ):
        if self.proc :
            self.proc.send_signal(signal.SIGINT)

    def worker( self ):
        print("Starting worker...")
        self.proc = Popen(["lean","--server","--json"],stdout=PIPE,stdin=PIPE,stderr=STDOUT,universal_newlines=True,shell=False)
        self.started.set()

        for line in self.proc.stdout :
            try:
                data = json.loads(line)
                self.rx_queue.put(data)
                self.has_resp.set()

            except json.JSONDecodeError as e:
                traceback.print_exc()

        self.proc.wait()
        self.rx_queue.put(None)
        print("Worker end")
        self.started.clear()

    def send( self, msg ):
            if self.proc is not None:
                print("sending : %s" % msg)
                data = json.dumps(dict(msg)) + "\n"
                self.proc.stdin.write(data)
                self.proc.stdin.flush()

if __name__ == "__main__":
    ss = Lean_Server()
    ss.start()
    ss.started.wait()

    with open("examples/template.lean") as fhandle:
        data = fhandle.read()
        ss.send({"seq_num":0,"command":"sync","content":data,"file_name":"examples/template.lean"})

        ss.has_resp.wait()
        while not ss.rx_queue.empty():
            resp = ss.rx_queue.get()
            print(resp)
        ss.has_resp.clear()

    ss.stop()
