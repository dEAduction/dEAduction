"""
# ServerInterface.py : #ShortDescription #
    
    (#optionalLongDescription)

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 07 2020 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

This file is part of dEAduction.

    dEAduction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    dEAduction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

import trio

from deaduction.pylib.coursedata.exercise_classes import Exercise
from deaduction.pylib.proof_state.proof_state import ProofState
from deaduction.pylib.lean.response import Message
from pathlib import Path
from deaduction.pylib.editing import LeanFile
from deaduction.pylib.lean.request import SyncRequest
from deaduction.pylib.lean.server import LeanServer

from PySide2.QtCore import Signal, QObject

import logging


class ServerInterface(QObject):
    target_change = Signal()  # TODO : parameters
    context_change = Signal()  # TODO : parameters

    #  received by self.target_change.emit(...)

    def __init__(self, nursery):
        self.log = logging.getLogger("ServerInterface")

        self.lean_file: LeanFile = None
        self.lean_server: LeanServer = LeanServer(nursery)
        self.nursery: trio.Nursery = nursery

        # Set server callbacks
        self.lean_server.on_message_callback = self.__on_lean_message
        self.lean_server.running_monitor.on_state_change_callback = \
            self.__on_lean_state_change

    async def start(self):
        await self.lean_server.start()

    def stop(self):
        self.lean_server.stop()

    ###########################
    # Exercise initialisation #
    ###########################
    def exercise_set(self, exercise: Exercise):
        """
        initialise the lean_file from exercise
        :param exercise:
        :return:lean_file
        """
        file_content = exercise.course.file_content
        lines = file_content.splitlines()
        begin_line = exercise.lean_begin_line_number
        virtual_file_preamble = "\n".join(lines[:begin_line]) + "\n"
        virtual_file_afterword = "hypo_analysis,\n" \
                                 + "goals_analysis,\n" + "end"
        txt = virtual_file_preamble + virtual_file_afterword

        virtual_file = LeanFile(txt=txt, current_pos=begin_line + 1)
        return virtual_file

    ###########
    # history #
    ###########
    async def history_undo(self):
        self.lean_file.undo()
        await self.__update()

    async def history_redo(self):
        self.lean_file.redo()
        await self.__update()

    #####################
    # Lean instructions #
    #####################
    async def code_insert(self, label: str, code: str):
        """

        todo: ne pas oublier de mettre le but courant dans lean_file quand
        il est calculé : lean_file.info_attach(goal=self.current_goal)
        :param label:
        :param code:
        :return:
        """
        self.new_code = True
        self.lean_file.insert(lbl=label, add_txt=code)
        await self.__update()

    #####################
    # process Lean info #
    #####################

    def __process_lean_context(self, txt):
        """
        Processes the data received from the hypo_analysis tactic
        """
        self.new_hypo = True
        self.hypo_analysis = txt
        if self.new_targets:
            self.__process_lean_goal()

    def __process_lean_targets(self, txt):
        """
        Process the data received from the targets_analysis tactic.
        """
        self.new_targets = True
        self.targets_analysis = txt
        if self.new_hypo:
            self.__process_lean_goal()

    def __process_lean_goal(self):
        """
        process the data when both context_analysis and targets_analysis
        have been received
        """
        self.log.info("Processing new goal from Lean analysis")
        self.proof_state = ProofState.from_lean_data(self.hypo_analysis,
                                                     self.targets_analysis)
        self.new_hypo = False
        self.new_targets = False
        self.new_code = False

    def __on_lean_message(self, msg: Message):
        txt = msg.text
        severity = msg.severity
        if severity == "error":
        # TODO: does not work
            self.log.warning(f"Lean error: {txt}")
        elif txt.startswith("context:"):
            self.log.info("Got new context")
            self.__process_lean_context(txt)
        elif txt.startswith("targets:"):
            self.log.info("Got new targets")
            self.__process_lean_targets(txt)

    def __on_lean_state_change(self, is_running: bool):
        self.log.info(f"New lean state: {is_running}")

    async def __update(self):
        req = SyncRequest(file_name=self.lean_file.file_name,
                          content=self.lean_file.contents)
        await self.lean_server.send(req)
        await self.lean_server.running_monitor.wait_ready()

    async def lean_file_init(self, path: Path, line: int):
        path = Path(path)
        filename = str(Path.name)
        text = path.read_text()
        self.hypo_counter = 0
        self.goals_counter = 0
        self.lean_file = LeanFile(file_name=filename, init_txt=text)
        self.lean_file.cursor_move_to(line)
        self.lean_file.cursor_save()
        await self.__update()


if __name__ == "__main__":
    import deaduction.pylib.logger as logger

    logger.configure()


    async def main():
        async with trio.open_nursery() as nursery:
            server = ServerInterface(nursery)

            await server.start()
            await server.lean_file_init(Path("src/exercises_test.lean"), 00)





            server.stop()
            await server.lean_server.exited.wait()


    trio.run(main)
