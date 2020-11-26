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
import logging

from deaduction.config import EXERCISE
from deaduction.pylib.coursedata.exercise_classes import Exercise
from deaduction.pylib.mathobj.proof_state import ProofState
from deaduction.pylib.lean.response import Message
from deaduction.pylib.editing import LeanFile
from deaduction.pylib.lean.request import SyncRequest
from deaduction.pylib.lean.server import LeanServer

import deaduction.pylib.server.exceptions as exceptions

from PySide2.QtCore import Signal, QObject

from gettext import gettext as _

############################################
# Lean magic messages
############################################
LEAN_UNRESOLVED_TEXT = "tactic failed, there are unsolved goals"
LEAN_NOGOALS_TEXT    = "tactic failed, there are no goals to be solved"
LEAN_USES_SORRY      = " uses sorry"


############################################
# ServerInterface class
############################################
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

    proof_no_goals     = Signal()

    lean_file_changed  = Signal()

    ############################################
    # Init, and state control
    ############################################
    def __init__(self, nursery):
        super().__init__()

        self.log = logging.getLogger("ServerInterface")

        # Lean attributes
        self.lean_file: LeanFile      = None
        self.lean_server: LeanServer  = LeanServer(nursery)
        self.nursery: trio.Nursery    = nursery

        # Set server callbacks
        self.lean_server.on_message_callback = self.__on_lean_message
        self.lean_server.running_monitor.on_state_change_callback = \
            self.__on_lean_state_change

        # Current exercise
        self.exercise_current         = None

        # Current proof state + Event s
        self.__proof_state_valid      = trio.Event()
        self.__proof_receive_done     = trio.Event()
        self.__proof_receive_error    = trio.Event() # Set if request failed

        self.__tmp_hypo_analysis      = ""
        self.__tmp_targets_analysis   = ""
        self.__tmp_effective_code     = ""

        self.proof_state              = None

        # Errors memory channels
        self.error_send, self.error_recv = \
            trio.open_memory_channel(max_buffer_size=1024)

    async def start(self):
        await self.lean_server.start()

    def stop(self):
        self.lean_server.stop()

    ############################################
    # Callbacks from lean server
    ############################################
    def __check_receive_state(self):
        if self.__tmp_targets_analysis and self.__tmp_hypo_analysis:
            self.__proof_receive_done.set()

    def __on_lean_message(self, msg: Message):
        """
        Treatment of relevant Lean messages.
        NB: only the first message starting with
            - "EFFECTIVE CODE",
            - "context:" or
            - "target:"
        is accepted for each request sent.

        :param msg:
        :return:
        """
        txt = msg.text
        line = msg.pos_line
        severity = msg.severity

        if severity == Message.Severity.error:
            self.log.error(f"Lean error at line {msg.pos_line}: {txt}")
            self.__filter_error(msg)  # Record error ?

        elif severity == Message.Severity.warning:
            if not txt.endswith(LEAN_USES_SORRY):
                self.log.warning(f"Lean warning at line {msg.pos_line}: {txt}")

        elif txt.startswith("context:") \
                and line == self.lean_file.last_line_of_inner_content + 1\
                and not self.__tmp_hypo_analysis:
            self.log.info("Got new context")
            self.__tmp_hypo_analysis = txt

            self.__proof_state_valid = trio.Event()  # Invalidate proof state
            self.__check_receive_state()

        elif txt.startswith("targets:") \
                and line == self.lean_file.last_line_of_inner_content + 2\
                and not self.__tmp_targets_analysis:
            self.log.info("Got new targets")
            self.__tmp_targets_analysis = txt

            self.__proof_state_valid = trio.Event()  # Invalidate proof state
            self.__check_receive_state()

        elif txt.startswith("EFFECTIVE CODE")\
                and line == self.lean_file.last_line_of_inner_content:
            if self.__tmp_effective_code:
                self.log.warning("(effective code received twice)")
            else:
                self.log.info(f"Got {txt} at line {line}")
                # find text after "EFFECTIVE CODE xxx : "
                pos = txt.find(":") + 2
                self.__tmp_effective_code = txt[pos:]
                self.history_replace(self.__tmp_effective_code)

    def __on_lean_state_change(self, is_running: bool):
        self.log.info(f"New lean state: {is_running}")
        self.is_running = is_running

    ############################################
    # Message filtering
    ############################################
    def __filter_error(self, msg: Message):
        # Filter message text, record if not ignored message
        if msg.text.startswith(LEAN_NOGOALS_TEXT):
            if hasattr(self.proof_no_goals, "emit"):
                self.proof_no_goals.emit()
                self.__proof_receive_done.set()  # Done receiving

        elif msg.text.startswith(LEAN_UNRESOLVED_TEXT):
            pass
        # ignore messages that do not concern current proof
        elif msg.pos_line < self.lean_file.first_line_of_last_change \
                or msg.pos_line > self.lean_file.last_line_of_inner_content:
            pass
        else:
            self.error_send.send_nowait(msg)
            self.__proof_receive_done.set()  # Done receiving

    ############################################
    # Update
    ############################################
    async def __update(self):
        first_line_of_change = self.lean_file.first_line_of_last_change
        self.log.debug(f"Updating, checking errors from line "
                       f"{first_line_of_change}, and context at "
                       f"line {self.lean_file.last_line_of_inner_content + 1}")

        self.lean_file_changed.emit()  # will update the lean text editor

        if hasattr(self.update_started, "emit"):
            self.update_started.emit()

        req = SyncRequest(file_name=self.lean_file.file_name,
                          content=self.lean_file.contents)

        # Invalidate events
        self.__proof_receive_done   = trio.Event()
        self.__tmp_hypo_analysis    = ""
        self.__tmp_targets_analysis = ""
        self.__tmp_effective_code   = ""

        resp = await self.lean_server.send(req)
        if resp.message == "file invalidated":

            await self.__proof_receive_done.wait()

            self.log.debug(_("Proof State received"))
            # next line removed by FLR
            # await self.lean_server.running_monitor.wait_ready()

            self.log.debug(_("After request"))

            # Construct new proof state from temp strings
            if not self.__proof_state_valid.is_set():
                self.proof_state = ProofState.from_lean_data(
                    self.__tmp_hypo_analysis, self.__tmp_targets_analysis)
                # store proof_state for history
                self.log.debug("storing ProofState")
                self.lean_file.state_info_attach(ProofState=self.proof_state)

                self.__proof_state_valid.set()


                # Emit signal only if from qt context (avoid AttributeError)
                if hasattr(self.proof_state_change, "emit"):
                    self.proof_state_change.emit(self.proof_state)

            if hasattr(self.update_ended, "emit"):
                self.update_ended.emit()

        # Emit exceptions ?
        errlist = []
        try:
            while True:
                errlist.append(self.error_recv.receive_nowait())
        except trio.WouldBlock:
            pass

        if errlist:
            raise exceptions.FailedRequestError(errlist)

    ############################################
    # Exercise initialisation
    ############################################
    def __file_from_exercise(self, exercise):
        """
        Create a virtual file from exercise. Concretely, this consists in
        - separating the part of the file before the proof into a preamble,
        - add the tactics instruction "hypo_analysis, targets_analysis"
        - remove all statements after the proof.

        If exercise.negate_statement, then the statement is replaced by its
        negation.

        Then a virtual file is instanciated.

        :param exercise: Exercise
        """
        file_content = exercise.course.file_content
        lines        = file_content.splitlines()
        begin_line   = exercise.lean_begin_line_number

        # construct short end of file by closing all open namespaces
        end_of_file = "end\n"
        namespaces = exercise.ugly_hierarchy()
        while namespaces:
            namespace = namespaces.pop()
            end_of_file += "end " + namespace + "\n"
        end_of_file += "end course"

        # replace statement by negation if required
        if exercise.negate_statement:
            lean_core_statement = exercise.lean_core_statement
            negation = " not( " + lean_core_statement + " )"
            lemma_line = exercise.lean_line - 1
            rough_core_content = "\n".join(lines[lemma_line:begin_line]) + "\n"
            # self.log.debug(rough_core_content.find(lean_core_statement))
            new_core_content = rough_core_content.replace(
                                    lean_core_statement, negation)
            # self.log.debug(f"New core content:{new_core_content}")
            # self.log.debug(f"Lean_core_statement:{lean_core_statement}")
            virtual_file_preamble = "\n".join(lines[:lemma_line]) \
                                    + "\n" + new_core_content
        else:
            # Construct virtual file
            virtual_file_preamble = "\n".join(lines[:begin_line]) + "\n"

        virtual_file_afterword = "hypo_analysis,\n" \
                                 "targets_analysis,\n" \
                                 + end_of_file

        virtual_file = LeanFile(file_name=exercise.lean_name,
                                preamble=virtual_file_preamble,
                                afterword=virtual_file_afterword)

        virtual_file.cursor_move_to(0)
        virtual_file.cursor_save()

        return virtual_file

    async def exercise_set(self, exercise: Exercise):
        """
        Initialise the virtual_file from exercise

        :param exercise:        The exercise to be set
        :return:                virtual_file
        """

        self.log.info(f"Set exercise to: "
                      f"{exercise.lean_name} -> {exercise.pretty_name}")

        self.exercise_current = exercise
        vf = self.__file_from_exercise(self.exercise_current)

        self.lean_file = vf

        await self.__update()

    ############################################
    # History
    ############################################
    async def history_undo(self):
        EXERCISE.last_action = 'undo'
        self.lean_file.undo()
        await self.__update()

    async def history_redo(self):
        self.lean_file.redo()
        await self.__update()

    def history_replace(self, effective_code):
        """
        Replace last entry in the lean_file by effective_code
        without calling Lean
        effective_code is assumed to be equivalent, from the Lean viewpoint,
        to last code entry
        NB: this method does NOT call self.__update().
        Indeed, it is designed to replace a piece of code by another piece
        which is assumed to be equivalent from Lean's viewpoint.

        :param effective_code: str
        """
        effective_code = effective_code.strip()
        if not effective_code.endswith(","):
            effective_code += ","
        if not effective_code.endswith("\n"):
            effective_code += "\n"

        lean_file = self.lean_file
        label = lean_file.history[lean_file.target_idx].label
        self.lean_file.undo()
        self.lean_file.insert(label=label, add_txt=effective_code)
        self.lean_file_changed.emit()  # will update the lean text editor

    ############################################
    # Code management
    ############################################
    async def code_insert(self, label: str, code: str):
        """
        Inserts code in the Lean virtual file.
        """

        code = code.strip()

        if not code.endswith(","):
            code += ","

        if not code.endswith("\n"):
            code += "\n"

        # if code.find("EFFECTIVE CODE") == -1:  # not used
        #     self.__tmp_effective_code = "IRRELEVANT"

        self.lean_file.insert(label=label, add_txt=code)
        await self.__update()

    async def code_set(self, label: str, code: str):
        """
        Sets the code for the current exercise
        """

        if not code.endswith(","):
            code += ","

        if not code.endswith("\n"):
            code += "\n"

        self.lean_file.state_add(label, code)
        await self.__update()