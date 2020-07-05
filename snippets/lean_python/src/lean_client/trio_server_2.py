import math
import trio
import traceback

from   subprocess import PIPE

from   queue import Queue

from commands import (
    Request,
    SyncRequest
)

import json

class Lean_Server:
    ############################################
    # Utilities classes
    ############################################
    class Num_Picker:
        """
        Utility class used to retrieve seq_num numbers
        """
        def __init__( self, max_nums:int=1024 ):
            self.send,self.recv = None,None
            self.max_nums:int   = max_nums

        async def release(self,num):
            await self.send.send(num)

        async def pick(self):
            return await self.recv.receive()

        async def open(self):
            self.send,self.recv = trio.open_memory_channel(
                max_buffer_size=self.max_nums
            )

            # Init available numbers
            for i in range(self.max_nums) : await self.release(i)

    class Running_Monitor:
        """
        Class used to monitor lean server running state
        """
        def __init__( self, max_size=1024 ):
            self.max_size                   = max_size
            self.ready_send,self.ready_recv = trio.open_memory_channel(
                max_buffer_size=max_size
            )

            self.active_send,self.active_recv = trio.open_memory_channel(
                max_buffer_size=max_size
            )

        async def wait_ready(self):
            ev = trio.Event()
            self.ready_send.send(ev)

            await ev

        async def wait_active(self):
            ev = trio.Event()
            self.active_send.send(ev)
            
            await ev

        def update(self, is_running:bool):
            print(f"is_running: {is_running}")
            recv = self.active_recv if is_running else self.ready_recv # Which objects to notify ?
            while True:
                try:
                    ev = recv.receive_nowait()
                    ev.set()
                except trio.WouldBlock:break # Memory channel is empty

    ###########################################

    def __init__( self, nursery ):
        self.nursery = nursery

        self.process                = None
        self.buffer                 = ""

        self.num_picker             = Lean_Server.Num_Picker()
        self.running_monitor        = Lean_Server.Running_Monitor()

    ############################################
    # Protected utilities
    ############################################
    def _check_process(self):
        if not self.process : raise RuntimeError("Lean server not active")

    ############################################
    # Response process utilities
    ############################################
    def _process_response(self,resp:str):
        """
        Processes response data

        :param resp: Response data to process
        """

        dd = json.loads(resp) # TODO # Process JSON parse errors ?

        # Checks for specific fields
        if "is_running" in dd : self.running_monitor.update(dd["is_running"])

    ###########################################
    # Start / Receiver tasks
    ###########################################
    async def start( self ):
        # Init available seq_numbers memory channels
        await self.num_picker.open()

        self.process = await trio.open_process(
            ["lean","--json","--server"], stdin=PIPE, stdout=PIPE
        )
        print("Started server")

        self.nursery.start_soon(self.receiver)

    async def receiver(self):
        self._check_process()

        async for data in self.process.stdout:
            sstr         = data.decode("utf-8")
            self.buffer += sstr

            idx = self.buffer.find("\n")
            while idx >= 0:
                line        = self.buffer[:idx]
                self.buffer = self.buffer[idx+1:]

                print(f"Rx : {line}")
                try    : self._process_response(line)
                except :
                    # TODO # Better error managment
                    traceback.print_exc()
                
                idx         = self.buffer.find("\n")

    ############################################
    # Send utilities
    ############################################
    async def send(self, rq) -> None:
        self._check_process()
        seq_num     = await self.num_picker.pick()
        rq.seq_num  = seq_num

        jss         = rq.to_json()
        print(jss)

        await self.process.stdin.send_all((str(jss)+"\n").encode("utf-8"))

def read_lean_template():
    nb_line    = 0
    sorry_line = 0

    txt     = ""
    with open("examples/template.lean") as fhandle:
        for line in fhandle:
            nb_line += 1
            if line == "sorry":
                sorry_line = nb_line
                txt += "{}\n"

            else:
                txt += line + "\n"

    return sorry_line, txt

async def main():
    async with trio.open_nursery() as nursery:
        srv = Lean_Server( nursery )
        await srv.start()

        st,template = read_lean_template()
        rq = SyncRequest(file_name="template.lean",content=template)

        await srv.send(rq)

if __name__=="__main__":
    trio.run(main)
