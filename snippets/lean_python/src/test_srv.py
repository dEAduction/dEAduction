import deaduction.pylib.logger as logger
from   lean.server import Lean_Server
import logging
import trio

import lean.request

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
        srv = Lean_Server(nursery)
        await srv.start()

        st,template = read_lean_template()
        rq = lean.request.SyncRequest(file_name="superfichier",content=template)

        res = await srv.send(rq)
        log.info(f"Result is : {res}")

        await srv.running_monitor.wait_ready()

        log.info("SERVEUR IS RADIS !")

if __name__=="__main__":
    trio.run(main)
