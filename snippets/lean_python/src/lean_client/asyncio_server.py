import asyncio
import signal
from   subprocess import PIPE,STDOUT
import time

import commands

import json

import signal

class Lean_Protocol(asyncio.Protocol):
    def __init__( self ):
        self.buffer = str()
        
        # Futures
        self.exit_future = asyncio.Future( loop=asyncio.get_running_loop() )

    def process_exited(self):
        self.exit_future.set_result(True)

    def pipe_data_received(self,fd,data):
        """
        Called when data has been received on stdin pipe.
        """
        ss           = data.decode("utf-8")
        self.buffer += ss

        idx = self.buffer.find("\n")
        while idx >= 0:
            line        = self.buffer[:idx]
            self.buffer = self.buffer[idx+1:]

            print(f"Rx : {line}")

            idx = self.buffer.find("\n")

    def pipe_connection_lost(self,fd,exc):
        pass

class Lean_Server:
    def __init__( self ):
        self.transport = None
        self.protocol  = None
        #self.started   = asyncio.Future(loop=asyncio.get_running_loop())

        self.stdin     = None
        self.stdout    = None

    async def start(self):
        loop = asyncio.get_running_loop()
        
        self.transport,self.protocol = await loop.subprocess_exec(
            Lean_Protocol,
            "lean","--server","--json",
            stdout=PIPE,stdin=PIPE,stderr=STDOUT
        )

        self.stdin    = self.transport.get_pipe_transport(0)
        self.stdout   = self.transport.get_pipe_transport(1)

    def tx(self,data):
        #jss = json.dumps(data) + "\n"
        jss = data

        print(f"Tx : {str(jss)}")
        self.stdin.write((jss+"\n").encode("utf-8"))

    def stop(self):
        self.transport.close()

    async def wait(self):
        await self.protocol.exit_future

    async def close(self):
        self.transport.close() # close stdout,stdin pipes

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

srv = None
async def main():
    global srv
    st,template = read_lean_template()
    srv = Lean_Server()

    await srv.start()

    rq  = commands.SyncRequest(file_name="template.lean", content=template)
    srv.tx(rq.to_json())

    await srv.wait()


#def shutdown(signum,frame):
#    print("Received Ctrl+C, stopping server")
#    srv.stop()
#
#signal.signal(signal.SIGINT, shutdown)

try:
    asyncio.run(main())
    print("After main")

except KeyboardInterrupt:
    print("Keyboard interrupt !")

#loop = asyncio.get_event_loop()
#task = asyncio.gather( main() )
#
#loop.run_until_complete(task)
#
#finally:
#    loop.close()
