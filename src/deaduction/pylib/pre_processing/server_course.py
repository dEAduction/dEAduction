"""
###########################################################
# server_course.py: Lean server to process a whole course #
###########################################################

Author(s):      - Frédéric Le Roux <frederic.le-roux@imj-prg.fr>

Maintainers(s): - Frédéric Le Roux <frederic.le-roux@imj-prg.fr>

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

from deaduction.pylib.coursedata        import Course
from deaduction.pylib.proof_state.proof_state import ProofState
from deaduction.pylib.lean.response import Message
from deaduction.pylib.lean.request import SyncRequest
from deaduction.pylib.lean.server import LeanServer
from deaduction.pylib.lean.installation import LeanEnvironment

import deaduction.pylib.config.site_installation as inst

from PySide2.QtCore import Signal, QObject

from gettext import gettext as _


############################################
# Lean magic messages
############################################
LEAN_UNRESOLVED_TEXT = "tactic failed, there are unsolved goals"
LEAN_NOGOALS_TEXT    = "tactic failed, there are no goals to be solved"
LEAN_USES_SORRY      = " uses sorry"


####################
# CourseData class #
####################
class CourseData:
    """
    A container class for the data related to a list of statements to get
    their initial proof state. these data will be passed to ServerInterface
    (as a ServerInterface attribute).
    """

    def __init__(self, course: Course, statements: [] = None):
        self.course = course
        if not statements:
            self.statements = course.statements
        else:
            self.statements = statements

        # self.log.info({f"Getting proof states for course {course.title}"})
        # self.log.info({f"{len(self.statements)} statements"})

        self.hypo_analysis   = [None] * len(self.statements)
        self.targets_analysis = [None] * len(self.statements)
        self.statement_from_hypo_line = dict()
        self.statement_from_targets_line = dict()

        self.pf_counter = 0

    def file_content(self):
        lines        = self.course.file_content.splitlines()
        hypo_tactic    = "    hypo_analysis,"
        targets_tactic = "    targets_analysis,"

        shift = 0  # Shift due to line insertion/deletion
        for statement in self.statements:
            # self.log.debug(f"Statement n° {self.statements.index(
            # statement)}")
            begin_line   = statement.lean_begin_line_number + shift
            end_line     = statement.lean_end_line_number + shift
            # self.log.debug(f"{len(lines)} lines")
            # self.log.debug(f"begin, end =  {begin_line, end_line}")
            proof_lines = list(range(begin_line, end_line-1))
            # self.log.debug(proof_lines)
            proof_lines.reverse()
            for index in proof_lines:
                lines.pop(index)
            lines.insert(begin_line, hypo_tactic)
            lines.insert(begin_line+1, targets_tactic)
            self.statement_from_hypo_line[begin_line+1] = statement
            self.statement_from_targets_line[begin_line+2] = statement
            # No shift if end_line = begin_line + 3
            shift += 3 - (end_line - begin_line)
            # self.log.debug(f"Shift: {shift}")
            # Construct virtual file

        file_content = "\n".join(lines)
        return file_content


############################################
# ServerInterface class
############################################
class ServerInterfaceAllStatements(QObject):
    """
    High level interface to lean server.
    """
    ############################################
    # Qt Signals
    ############################################
    proof_state_change = Signal(ProofState)

    update_started              = Signal()
    update_ended                = Signal()

    #    proof_no_goals              = Signal()

    # Signal emitted when all effective codes have been received,
    # so that history_replace is called
    # effective_code_received     = Signal(CodeForLean)

    ############################################
    # Init, and state control
    ############################################
    def __init__(self, nursery):
        super().__init__()

        self.log = logging.getLogger("ServerInterfaceAllStatements")

        # Lean environment
        self.lean_env: LeanEnvironment = LeanEnvironment(inst)
        # Lean attributes
        self.lean_file_content: str    = ""
        self.lean_server: LeanServer   = LeanServer(nursery, self.lean_env)
        self.nursery: trio.Nursery     = nursery

        # Set server callbacks
        self.lean_server.on_message_callback = self.__on_lean_message
        self.lean_server.running_monitor.on_state_change_callback = \
            self.__on_lean_state_change

        # Course data
        self.__course_data = None

        # Current proof state + Events
        self.file_invalidated          = trio.Event()
        # self.__proof_state_valid       = trio.Event()

        # __proof_receive_done is set when enough information have been
        # received, i.e. either we have context and target and all effective
        # codes, OR an error message.
        self.__proof_receive_done      = trio.Event()
        # self.__proof_receive_error     = trio.Event()  # Set if request
        # failed

        # When some CodeForLean iss sent to the __update method, it will be
        # duplicated and stored in __tmp_effective_code. This attribute will
        # be progressively modified into an effective code which is devoid
        # of or_else combinator, according to the "EFFECTIVE CODE" messages
        # sent by Lean.

        # Errors memory channels
        self.error_send, self.error_recv = \
            trio.open_memory_channel(max_buffer_size=1024)

    async def start(self):
        """
        Asynchronously start the Lean server.
        """
        await self.lean_server.start()

    def stop(self):
        """
        Stop the Lean server.
        """
        self.lean_server.stop()

    ############################################
    # Callbacks from lean server
    ############################################
    def __check_receive_course_data(self, index):
        """
        Check if every awaited piece of information has been received:
        """
        hypo = self.__course_data.hypo_analysis[index]
        target = self.__course_data.targets_analysis[index]
        if hypo and target:
            statements = self.__course_data.statements
            st = statements[index]
            if not st.initial_proof_state:
                ps = ProofState.from_lean_data(hypo, target)
                st.initial_proof_state = ps
                self.__course_data.pf_counter += 1

            # TODO: check all statements
            if self.__course_data.pf_counter == len(statements):
                self.__proof_receive_done.set()

    def __on_lean_message(self, msg: Message):
        """
        Treatment of relevant Lean messages. Note that the text may contain
        several lines. Error messages are treated via the __filter_error
        method. Other relevant messages are
        - message providing the new context,
        - message providing the new target,
        - messages providing the successful effective codes that will be
        used to replace the "or else" sequences of instructions.
        After relevant messages, the __check_receive_state method is called
        to check if all awaited messages have been received.
        """

        txt = msg.text
        # self.log.debug("Lean message: " + txt)
        line = msg.pos_line
        severity = msg.severity

        if severity == Message.Severity.error:
            self.log.error(f"Lean error at line {msg.pos_line}: {txt}")
            self.__filter_error(msg)  # Record error ?

        elif severity == Message.Severity.warning:
            if not txt.endswith(LEAN_USES_SORRY):
                self.log.warning(f"Lean warning at line {msg.pos_line}: {txt}")

        elif txt.startswith("context:"):
            st = self.__course_data.statement_from_hypo_line[line]
            index = self.__course_data.statements.index(st)
            self.log.info(f"Got new context for statmnt {st.lean_name}, "
                          f"index = {index}")
            self.__course_data.__hypo_analysis[index] = txt

            self.__check_receive_course_data(index)

        elif txt.startswith("targets:"):
            st = self.__course_data.statement_from_targets_line[line]
            index = self.__course_data.statements.index(st)
            self.log.info(f"Got new targets for statmnt {st.lean_name}, "
                          f"index = {index}")
            self.__course_data.targets_analysis[index] = txt

            self.__check_receive_course_data(index)

    def __on_lean_state_change(self, is_running: bool):
        self.log.info(f"New lean state: {is_running}")
        self.is_running = is_running

    ############################################
    # Message filtering
    ############################################
    def __filter_error(self, msg: Message):
        """
        Filter error messages from Lean,
        - according to position (i.e. ignore messages that do not correspond
         to the new part of the virtual file),
        - ignore "proof uses sorry" messages.
        """
        # Filter message text, record if not ignored message
        if msg.text.startswith(LEAN_NOGOALS_TEXT):
            if hasattr(self.proof_no_goals, "emit"):
                self.proof_no_goals.emit()
                self.__proof_receive_done.set()  # Done receiving
        elif msg.text.startswith(LEAN_UNRESOLVED_TEXT):
            pass
        # Ignore messages that do not concern current proof
        elif msg.pos_line < self.lean_file.first_line_of_last_change \
                or msg.pos_line > self.lean_file.last_line_of_inner_content:
            pass
        else:
            self.error_send.send_nowait(msg)
            self.__proof_receive_done.set()  # Done receiving

    ############################################
    # Update
    ############################################
    async def get_proof_states(self):
        """
        Call Lean server to update the proof_state.
        """
        file_name = str(self.course.relative_course_path)
        req = SyncRequest(file_name=file_name,
                          content=self.lean_file_content)

        # Invalidate events
        self.file_invalidated           = trio.Event()
        self.__proof_receive_done       = trio.Event()

        resp = await self.lean_server.send(req)

        if resp.message == "file invalidated":
            self.file_invalidated.set()

            #########################################
            # Waiting for all pieces of information #
            #########################################
            await self.__proof_receive_done.wait()

            self.log.debug(_("All proof states received"))
            # Next line removed by FLR
            # await self.lean_server.running_monitor.wait_ready()

            if hasattr(self.update_ended, "emit"):
                self.update_ended.emit()

        # Emit exceptions ? TODO: adapt
        # error_list = []
        # try:
        #     while True:
        #         error_list.append(self.error_recv.receive_nowait())
        # except trio.WouldBlock:
        #     pass
        #
        # if error_list:
        #     raise exceptions.FailedRequestError(error_list)

    ########################################
    # Course and statements initialisation #
    ########################################
    async def set_statements(self, course: Course, statements: [] = None):
        self.__course_data = CourseData(course, statements)
        self.lean_file_content = self.course_data.file_content()

        await self.get_proof_states()

