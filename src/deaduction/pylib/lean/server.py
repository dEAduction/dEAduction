"""
####################################
# server.py : Lean server handling #
####################################

Author(s)      : - Patrick Massot <patrick.massot@math.cnrs.fr>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>

Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : July 2020

Copyright (c) 2020 the dEAduction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    d∃∀duction is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with d∃∀duction. If not, see <https://www.gnu.org/licenses/>.
"""

import math
import trio
import traceback

import logging

from subprocess import PIPE
from queue      import Queue

from .          import request
from .          import response

import json

class LeanServer:
    ############################################
    # Utilities
    ############################################
    class Request_Store:
        """
        Utility class used to store requests
        """

        def __init__( self, max_nums: int ):
            self.send,self.recv = None,None # Memory channels
            self.max_nums:int   = max_nums
            self.pending_reqs   = [None] * max_nums
            self.results        = [None] * max_nums

        def set( self, num, result ):
            done = self.pending_reqs[num]
            if done is None: raise RuntimeError(f"No pending req for seq_num = {num}")
            self.results[num] = result
            done.set()

        async def release(self, num):
            await self.send.send(num)

            r = self.results[num]

            self.pending_reqs[num] = None
            self.results[num]      = None

            return r

        async def store(self):
            """
            Intialize a trio event and picks a seq_number. Returns
            a tuple of both objects
            """
            seq_num                    = await self.recv.receive()
            done_event                 = trio.Event()

            self.pending_reqs[seq_num] = done_event

            return seq_num, done_event

        async def open(self):
            self.send,self.recv = trio.open_memory_channel(
                max_buffer_size = self.max_nums
            )

            # Init available numbers
            for i in range(self.max_nums): await self.release(i)

    class Running_Monitor:
        """
        Class used to monitor lean server runnig state
        """

        def __init__( self, max_listeners=4, log=None ):
            self.max_listeners = max_listeners

            self.ready_send,self.ready_recv = trio.open_memory_channel(
                max_buffer_size = self.max_listeners
            )

            self.active_send,self.active_recv = trio.open_memory_channel(
                max_buffer_size = self.max_listeners
            )

            self.log = log

            self.on_state_change_callback = lambda x:None

        async def open(self): pass

        async def wait_ready(self):
            event = trio.Event()
            await self.ready_send.send(event)
            await event.wait()

        async def wait_active(self):
            event = trio.Event()
            await self.active_send.send(event)
            await event.wait()

        def update(self, is_running: bool):
            self.log.debug(f"Updating lean running state : {is_running}")
            self.on_state_change_callback(is_running)

            recv = self.active_recv if is_running else self.ready_recv
            while True:
                try:
                    event = recv.receive_nowait()
                    event.set()

                except trio.WouldBlock:break # Memory channel is empty

    ############################################
    # Class functions definitions
    ############################################
    def __init__( self, nursery, max_reqs:int=1024 ):
        self.log                       = logging.getLogger("lean")
        self.nursery                   = nursery

        self.process                   = None
        self.buffer                    = ""

        self.pending_reqs              = LeanServer.Request_Store  (max_reqs    )
        self.running_monitor           = LeanServer.Running_Monitor(log=self.log)

        self.on_message_callback       = lambda x: None

        self.tasks:List[response.Task] = []

    ############################################
    # Protected utilities
    ############################################
    def _check_process(self):
        if not self.process : raise RuntimeError("Lean server not active")

    ############################################
    # Response process utilities
    ############################################
    def _process_response(self, data_str:str):
        data       = json.loads(data_str)
        resp       = data["response"]
        parsed_msg = response.from_dict(data)

        # Check for specific messages types
        if isinstance(parsed_msg, response.CommandResponse) or \
           isinstance(parsed_msg, response.ErrorResponse  ):
               seq_num = parsed_msg.seq_num
               self.pending_reqs.set(seq_num,parsed_msg)

        elif isinstance(parsed_msg, response.CurrentTasksResponse):
            self.running_monitor.update(parsed_msg.is_running)
            self.tasks = parsed_msg.tasks

            for tsk in self.tasks:
                self.log.info(f"Lean Task: {tsk.file_name} at line {tsk.pos_line} and col {tsk.pos_col} : {tsk.desc}")

        elif isinstance(parsed_msg, response.AllMessagesResponse):
            for msg in parsed_msg.msgs:
                self.log.info(f"{msg.severity} at {msg.file_name}:{msg.pos_line}:{msg.pos_col} : {msg.text}")
                self.on_message_callback(msg)
        else:
            self.log.warning(f"Ignored message : {msg}")

    ############################################
    # Start / receiver tasks
    ############################################
    async def start(self):
        await self.running_monitor.open()
        await self.pending_reqs.open()

        self.process = await trio.open_process(
            ["lean","--json","--server"], stdin=PIPE, stdout=PIPE
        )
        self.log.info("Started server")

        self.nursery.start_soon(self.receiver)

    def stop(self):
        if self.process: self.process.terminate()

    async def receiver(self):
        self._check_process()

        async for data in self.process.stdout:
            sstr         = data.decode("utf-8")
            self.buffer += sstr

            idx = self.buffer.find("\n")
            while idx >= 0:
                line        = self.buffer[:idx]
                self.buffer = self.buffer[idx+1:]

                self.log.debug(f"Rx: {line}")
                try   : self._process_response(line)
                except: 
                    # TODO # Better error managment
                    self.log.error(traceback.format_exc())

                idx = self.buffer.find("\n")

    ############################################
    # Send utilities
    ############################################
    async def send(self, req, timeout=10000):
        self._check_process()
        seq_num,ev  = await self.pending_reqs.store()
        req.seq_num  = seq_num

        jss         = req.to_json()
        self.log.debug(f"Tx : {jss}")

        try:
            with trio.move_on_after(30):
                await self.process.stdin.send_all((str(jss)+"\n").encode("utf-8"))
                await ev.wait()

                return await self.pending_reqs.release(seq_num)

        except trio.Cancelled as exc:
            raise RuntimeError(f"Timeout while sending message {rq}")
