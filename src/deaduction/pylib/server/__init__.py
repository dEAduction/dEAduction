"""
#######################################################
# ServerInterface.py : High level interface to server #
#######################################################

Author(s):      - Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
                - Florian Dupeyron <florian.dupeyron@mugcat.fr>

Maintainers(s): - Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
                - Florian Dupeyron <florian.dupeyron@mugcat.fr>

Date: July 2020

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

import trio
from dataclasses import dataclass
from pathlib import Path
import logging

import sys

from deaduction.pylib.coursedata.exercise_classes import Exercise
from deaduction.pylib.mathobj.proof_state         import ProofState
from deaduction.pylib.lean.response               import Message
from deaduction.pylib.editing                     import LeanFile
from deaduction.pylib.lean.request                import SyncRequest
from deaduction.pylib.lean.server                 import LeanServer

from PySide2.QtCore import Signal, QObject

class ServerInterface(QObject):
    """
    High level interface to lean server.
    """
    ############################################
    # Qt Signals
    ############################################
    proof_state_change = Signal(ProofState)

    update_started     = Signal()
    update_ended       = Signal()

    ############################################
    # Init, and state control
    ############################################
    def __init__(self, nursery):
        super().__init__()

        self.log = logging.getLogger("ServerInterface")

        # Lean attributes
        self.lean_file: Lean_File    = None
        self.lean_server: LeanServer = LeanServer(nursery)
        self.nursery: trio.Nursery   = nursery
    
        # Set server callbacks
        self.lean_server.on_message_callback = self.__on_lean_message
        self.lean_server.running_monitor.on_state_change_callback = \
                self.__on_lean_state_change

        # Current exercise
        self.exercise_current        = None

        # Current proof state
        self.__proof_state_valid     = trio.Event()
        self.__tmp_hypo_analysis     = ""
        self.__tmp_targets_analysis  = ""

        self.proof_state             = None

    async def start(self):
        await self.lean_server.start()

    def stop(self):
        self.lean_server.stop()

    ############################################
    # Callbacks from lean server
    ############################################
    def __on_lean_message(self, msg: Message):
        txt      = msg.text
        severity = msg.severity

        print(f"ON LEAN MESSAGE {severity}")

        if severity == Message.Severity.error:
            self.log.error(f"Lean error at line {msg.pos_line}: {txt}")
        elif severity == Message.Severity.warning:
            self.log.warning(f"Lean warning at line {msg.pos_line}: {txt}")

        elif txt.startswith("context:"):
            self.log.info("Got new context")
            self.__tmp_hypo_analysis = txt
            self.__proof_state_valid = trio.Event()

        elif txt.startswith("targets:"):
            self.log.info("Got new targets")
            self.__tmp_targets_analysis = txt
            self.__proof_state_valid = trio.Event()

    def __on_lean_state_change(self, is_running: bool):
        self.log.info(f"New lean state: {is_running}")

    ############################################
    # Update
    ############################################
    async def __update(self):
        if hasattr(self.update_started, "emit"): self.update_started.emit()

        req = SyncRequest(file_name=self.lean_file.file_name,
                          content=self.lean_file.contents)

        await self.lean_server.send(req)
        await self.lean_server.running_monitor.wait_ready()

        # Construct new proof state from temp strings
        if not self.__proof_state_valid.is_set():
            self.proof_state = ProofState.from_lean_data(self.__tmp_hypo_analysis, self.__tmp_targets_analysis)
            self.__proof_state_valid.set()

            # Emit signal only if from qt context (avoid AttributeError)
            if hasattr(self.proof_state_change, "emit"): self.proof_state_change.emit(self.proof_state)

        if hasattr(self.update_ended, "emit"): self.update_ended.emit()

    ############################################
    # Exercise initialisation
    ############################################
    def __file_from_exercise(self, exercise):
        file_content = exercise.course.file_content
        lines        = file_content.splitlines()
        begin_line   = exercise.lean_begin_line_number
        end_line     = exercise.lean_end_line_number

        # Construct virtual file
        virtual_file_preamble = "\n".join(lines[:begin_line]) + "\n"
        virtual_file_afterword = "hypo_analysis,\n"  \
                                 "targets_analysis,\n" \
                                 + "\n".join(lines[(end_line-1):])

        txt = virtual_file_preamble + virtual_file_afterword

        virtual_file = LeanFile(file_name=exercise.lean_name, init_txt=txt)
        virtual_file.cursor_move_to(begin_line+1)
        virtual_file.cursor_save()

        return virtual_file

    async def exercise_set(self, exercise: Exercise):
        """
        initialise the virtual_file from exercise
        :param exercise:
        :return:virtual_file
        """

        self.log.info(f"Set exercise to : {exercise.lean_name} -> {exercise.pretty_name}")

        self.exercise_current = exercise
        vf = self.__file_from_exercise(self.exercise_current)

        self.lean_file = vf

        await self.__update()

    ############################################
    # History
    ############################################
    async def history_undo(self):
        self.lean_file.undo()
        await self.__update()

    async def history_redo(self):
        self.lean_file.redo()
        await self.__update()

    ############################################
    # Code managment
    ############################################
    async def code_insert(self, label: str, code: str):
        """
        Inserts code in the lean virtual file.
        """
    
        self.lean_file.insert(lbl = label, add_txt = code)
        await self.__update()
