import math
import trio
import traceback

import deaduction.pylib.logger as logger
import logging

from   subprocess import PIPE

from   queue import Queue

from commands import (
    Request,
    SyncRequest
)

import commands

import json
import re

MAGIC_STATE_REGEX = re.compile(r'tactic failed, there are unsolved goals\n'
                               r'state:')

class Lean_Server:
    ############################################
    # Utilities classes
    ############################################
    class Request_Object:
        def __init__( self ):
            self.ev   = trio.Event()
            self.data = None

        async def wait( self ):
            await self.ev.wait()
            return self.data

        async def validate( self, data ):
            self.data = data
            self.ev.set()

    class Request_Store:
        """
        Utility class used to store requests
        """
        def __init__( self, max_nums:int ):
            self.send,self.recv = None,None
            self.max_nums:int   = max_nums
            self.pending_reqs   = [None] * max_nums # Array containing requests events
            self.results        = [None] * max_nums # Array containing requests results

        def set(self, num, result ):
            ev = self.pending_reqs[num]
            if ev is None: raise RuntimeError(f"No pending req for seq_num = {num}")

            self.results[num] = result

            ev.set() # Set Event !

        async def release(self, num):
            """
            Release the storage for the given number.
            Returns the result value for the pending req
            """

            await self.send.send(num)     # Wait for number to be available in queue
            r = self.results[num]         # Get result

            self.pending_reqs[num] = None # Free Event storage
            self.results[num]      = None # Free Result storage

            return r

        async def store(self):
            """
            Intialize a trio event and picks a seq_number. Returns
            a tuple of both objects
            """
            seq_num                    = await self.recv.receive()
            ev                         = trio.Event()

            self.pending_reqs[seq_num] = ev

            return seq_num,ev
        
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
        def __init__( self, max_size=1024, log=None ):
            self.max_size                   = max_size
            self.ready_send,self.ready_recv = trio.open_memory_channel(
                max_buffer_size=max_size
            )

            self.active_send,self.active_recv = trio.open_memory_channel(
                max_buffer_size=max_size
            )

            self.log = log

        async def open(self):pass

        async def wait_ready(self):
            ev = trio.Event()
            await self.ready_send.send(ev)

            await ev.wait()

        async def wait_active(self):
            ev = trio.Event()
            await self.active_send.send(ev)
            await ev.wait()

        def update(self, is_running:bool):
            self.log.info(f"is_running: {is_running}")
            recv = self.active_recv if is_running else self.ready_recv # Which objects to notify ?
            while True:
                try:
                    ev = recv.receive_nowait()
                    ev.set()
                except trio.WouldBlock:break # Memory channel is empty

    ###########################################

    def __init__( self, nursery, max_reqs:int=1024 ):
        self.log     = logging.getLogger("lean")

        self.nursery = nursery

        self.process                   = None
        self.buffer                    = ""

        self.pending_reqs              = Lean_Server.Request_Store( max_reqs )
        self.running_monitor           = Lean_Server.Running_Monitor(log=self.log)

        self.tasks:List[commands.Task] = []

        self.state                     = "" # TODO # Structured object representation ?

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

        dd   = json.loads(resp) # TODO # Process JSON parse errors ?
        resp = dd["response"]

        parsed_msg = commands.parse_response(dd)

        # Check for specific messages types
        if isinstance(parsed_msg, commands.CommandResponse) or \
           isinstance(parsed_msg, commands.ErrorResponse):
               seq_num = parsed_msg.request_seq_num
               self.pending_reqs.set(seq_num, parsed_msg)

        elif isinstance(parsed_msg, commands.CurrentTasksResponse):
            self.running_monitor.update(parsed_msg.is_running)
            self.tasks = parsed_msg.tasks

            for tsk in self.tasks:
                self.log.info(f"Task: {tsk.file_name} at line {tsk.pos_line} and col {tsk.pos_col} : {tsk.desc}")

        elif isinstance(parsed_msg, commands.AllMessagesResponse):
            for msg in parsed_msg.msgs:
                if MAGIC_STATE_REGEX.match(msg.text):
                    self.state = MAGIC_STATE_REGEX.sub("",msg.text) 
                    self.log.info(f"New state is : {self.state}")

                else:
                    self.log.info(f"{msg.severity} at {msg.file_name}:{msg.pos_line}:{msg.pos_col} : {msg.text}")
        else: raise ValueError("Unknown message type : {type(parsed_msg)}")

    ###########################################
    # Start / Receiver tasks
    ###########################################
    async def start( self ):
        # Init available seq_numbers memory channels
        await self.running_monitor.open()
        await self.pending_reqs.open()

        self.process = await trio.open_process(
            ["lean","--json","--server"], stdin=PIPE, stdout=PIPE
        )
        self.log.info("Started server")

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

                self.log.debug(f"Rx : {line}")
                try    : self._process_response(line)
                except :
                    # TODO # Better error managment
                    self.log.error(traceback.format_exc())
                
                idx = self.buffer.find("\n") # Find next new line

    ############################################
    # Send utilities
    ############################################
    async def send(self, rq, timeout=10000) -> None:
        self._check_process()
        seq_num,ev  = await self.pending_reqs.store()
        rq.request_seq_num  = seq_num

        jss         = rq.to_json()
        self.log.debug(f"Tx : {jss}")

        try:
            with trio.move_on_after(30):
                await self.process.stdin.send_all((str(jss)+"\n").encode("utf-8"))
                await ev.wait()

                return await self.pending_reqs.release(seq_num)

        except trio.Cancelled as exc:
            raise RuntimeError(f"Timeout while sending message {rq}")

##################################################################################

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
    logger.configure()

    log = logging.getLogger("test lean server")

    async with trio.open_nursery() as nursery:
        srv = Lean_Server( nursery )
        await srv.start()

        st,template = read_lean_template()
        rq = SyncRequest(file_name="superfichier",content=template)

        res = await srv.send(rq)
        log.info(f"Result is : {res}")

        await srv.running_monitor.wait_ready()

        log.info("SERVEUR IS RADIS !")

if __name__=="__main__":
    trio.run(main)
