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
from copy import deepcopy

# from deaduction.config import EXERCISE
from deaduction.pylib.coursedata.exercise_classes import Exercise
from deaduction.pylib.mathobj.proof_state import ProofState
from deaduction.pylib.lean.response import Message
from deaduction.pylib.editing import LeanFile
from deaduction.pylib.lean.request import SyncRequest
from deaduction.pylib.lean.server import LeanServer
from deaduction.pylib.lean.installation import LeanEnvironment
from deaduction.pylib.actions import CodeForLean, get_effective_code_numbers

import deaduction.pylib.config.site_installation as inst
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

    update_started              = Signal()
    update_ended                = Signal()

    proof_no_goals              = Signal()

    lean_file_changed           = Signal()

    # Signal emitted when all effective codes have been received,
    # so that history_replace is called
    effective_code_received     = Signal(CodeForLean)

    ############################################
    # Init, and state control
    ############################################
    def __init__(self, nursery):
        super().__init__()

        self.log = logging.getLogger("ServerInterface")

        # Lean environment
        self.lean_env: LeanEnvironment = LeanEnvironment(inst)
        # Lean attributes
        self.lean_file: LeanFile       = None
        self.lean_server: LeanServer   = LeanServer(nursery, self.lean_env)
        self.nursery: trio.Nursery     = nursery

        # Set server callbacks
        self.lean_server.on_message_callback = self.__on_lean_message
        self.lean_server.running_monitor.on_state_change_callback = \
            self.__on_lean_state_change

        # Current exercise
        self.exercise_current          = None

        # Current proof state + Events
        self.file_invalidated          = trio.Event()
        self.__proof_state_valid       = trio.Event()

        # __proof_receive_done is set when enough information have been
        # received, i.e. either we have context and target and all effective
        # codes, OR an error message.
        self.__proof_receive_done      = trio.Event()
        # self.__proof_receive_error     = trio.Event()  # Set if request
        # failed

        self.__tmp_hypo_analysis       = ""
        self.__tmp_targets_analysis    = ""

        # When some CodeForLean iss sent to the __update method, it will be
        # duplicated and stored in __tmp_effective_code. This attribute will
        # be progressively modified into an effective code which is devoid
        # of or_else combinator, according to the "EFFECTIVE CODE" messages
        # sent by Lean.
        self.__tmp_effective_code      = CodeForLean.empty_code()
        self.proof_state               = None

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
    def __check_receive_state(self):
        """
        Check if every awaited piece of information has been received:
        i.e. target and hypo analysis, and all effective codes to replace
        the or_else instructions. After the signal __proof_receive_done is
        set, the __update method will stop listening to Lean, and start
        updating Proofstate.
        """
        if self.__tmp_targets_analysis \
                and self.__tmp_hypo_analysis \
                and not self.__tmp_effective_code.has_or_else():
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

        elif txt.startswith("EFFECTIVE CODE") \
            and line == self.lean_file.last_line_of_inner_content \
                and self.__tmp_effective_code.has_or_else():
            # txt may contain several lines
            for txt_line in txt.splitlines():
                if not txt_line.startswith("EFFECTIVE CODE"):
                    # Message could be "EFFECTIVE LEAN CODE"
                    # TODO: treat these messages
                    continue
                self.log.info(f"Got {txt_line}")
                node_nb, code_nb = get_effective_code_numbers(txt_line)
                # Modify __tmp_effective_code by selecting the effective
                # or_else alternative according to codes
                self.__tmp_effective_code, found = \
                    self.__tmp_effective_code.select_or_else(node_nb, code_nb)
                if found:
                    self.log.debug("(selecting effective code)")

            # Test if some there remain some or_else combinators
            if not self.__tmp_effective_code.has_or_else():
                # Done with effective codes, history_replace will be called
                self.log.debug("No more effective code to receive")
                if hasattr(self.effective_code_received, 'emit'):
                    self.effective_code_received.emit(self.__tmp_effective_code)
                self.__check_receive_state()

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
    async def __update(self, lean_code=None):
        """
        Call Lean server to update the proof_state.
        """

        first_line_of_change = self.lean_file.first_line_of_last_change
        self.log.debug(f"Updating, checking errors from line "
                       f"{first_line_of_change}, and context at "
                       f"line {self.lean_file.last_line_of_inner_content + 1}")

        if lean_code:
            self.__tmp_effective_code = deepcopy(lean_code)
        else:
            self.__tmp_effective_code = CodeForLean.empty_code()

        self.lean_file_changed.emit()  # will update the lean text editor

        if hasattr(self.update_started, "emit"):
            self.update_started.emit()

        req = SyncRequest(file_name=self.lean_file.file_name,
                          content=self.lean_file.contents)

        # Invalidate events
        self.file_invalidated           = trio.Event()
        self.__proof_receive_done       = trio.Event()
        self.__tmp_hypo_analysis        = ""
        self.__tmp_targets_analysis     = ""

        resp = await self.lean_server.send(req)

        if resp.message == "file invalidated":
            self.file_invalidated.set()

            #########################################
            # Waiting for all pieces of information #
            #########################################
            await self.__proof_receive_done.wait()

            self.log.debug(_("Proof State received"))
            # Next line removed by FLR
            # await self.lean_server.running_monitor.wait_ready()

            self.log.debug(_("After request"))

            # If data for new proof state have been received
            if not self.__proof_state_valid.is_set():
                # Construct new proof state
                self.proof_state = ProofState.from_lean_data(
                    self.__tmp_hypo_analysis, self.__tmp_targets_analysis)

                # Store proof_state for history
                self.log.debug("storing ProofState")
                self.lean_file.state_info_attach(ProofState=self.proof_state)

                self.__proof_state_valid.set()

                # Emit signal only if from qt context (avoid AttributeError)
                if hasattr(self.proof_state_change, "emit"):
                    self.proof_state_change.emit(self.proof_state)

            if hasattr(self.update_ended, "emit"):
                self.update_ended.emit()

        # Emit exceptions ?
        error_list = []
        try:
            while True:
                error_list.append(self.error_recv.receive_nowait())
        except trio.WouldBlock:
            pass

        if error_list:
            raise exceptions.FailedRequestError(error_list, lean_code)

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

        Then a virtual file is instantiated.

        :param exercise: Exercise
        """
        file_content = exercise.course.file_content
        lines        = file_content.splitlines()
        begin_line   = exercise.lean_begin_line_number

        # Construct short end of file by closing all open namespaces
        end_of_file = "end\n"
        namespaces = exercise.ugly_hierarchy()
        while namespaces:
            namespace = namespaces.pop()
            end_of_file += "end " + namespace + "\n"
        end_of_file += "end course"

        # Replace statement by negation if required
        if (hasattr(exercise, 'negate_statement')
                and exercise.negate_statement):
            lean_core_statement = exercise.lean_core_statement
            negation = " not( " + lean_core_statement + " )"
            lemma_line = exercise.lean_line - 1
            rough_core_content = "\n".join(lines[lemma_line:begin_line]) + "\n"
            new_core_content = rough_core_content.replace(
                                    lean_core_statement, negation)
            virtual_file_preamble = "\n".join(lines[:lemma_line]) \
                                    + "\n" + new_core_content
        else:
            # Construct virtual file
            virtual_file_preamble = "\n".join(lines[:begin_line]) + "\n"

        virtual_file_afterword = "hypo_analysis,\n" \
                                 "targets_analysis,\n" \
                                 + end_of_file

        # FIXME: the following is a trick to ensure that the begin_line of
        #  distinct exercises are sufficiently far apart, so that deaduction
        #  cannot mistake Lean's responses to a previous exercise for the
        #  awaited responses.
        # Add 100 lines per exercise number in the preamble
        virtual_file_preamble += "\n" * 100 * exercise.exercise_number
        # self.log.debug(f"File preamble: {virtual_file_preamble}")
        virtual_file = LeanFile(file_name=exercise.lean_name,
                                preamble=virtual_file_preamble,
                                afterword=virtual_file_afterword)

        virtual_file.cursor_move_to(0)
        virtual_file.cursor_save()

        return virtual_file

    async def exercise_set(self, exercise: Exercise):
        """
        Initialise the virtual_file from exercise.

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
        """
        Go one step forward in history in the lean_file.
        """
        self.lean_file.undo()
        await self.__update()

    async def history_redo(self):
        """
        Go one step backward in history in the lean_file.
        """
        self.lean_file.redo()
        await self.__update()

    async def history_rewind(self):
        """
        Go to beginning of history in the lean_file.
        """
        self.lean_file.rewind()
        await self.__update()

    def history_replace(self, code):
        """
        Replace last entry in the lean_file by code without calling Lean.
        WARNING: code should be an effective code whhich is equivalent,
        from the Lean viewpoint, to last code entry.
        NB: this method does NOT call self.__update().

        :param code: CodeForLean
        """
        if code:
            # Formatting
            code_string = code.to_raw_string(exclude_no_meta_vars=True)
            code_string = code_string.strip()
            if not code_string.endswith(","):
                code_string += ","
            if not code_string.endswith("\n"):
                code_string += "\n"

            lean_file = self.lean_file
            label = lean_file.history[lean_file.target_idx].label
            self.lean_file.undo()
            self.lean_file.insert(label=label, add_txt=code_string)
            self.lean_file_changed.emit()  # Will update the lean text editor

    ############################################
    # Code management
    ############################################
    async def code_insert(self, label: str, lean_code: CodeForLean):
        """
        Inserts code in the Lean virtual file.
        """

        # Add "no meta vars" + "effective code nb"
        # and keep track of node_counters
        lean_code, code_string = lean_code.to_decorated_string()
        code_string = code_string.strip()
        if not code_string.endswith(","):
            code_string += ","

        if not code_string.endswith("\n"):
            code_string += "\n"

        self.log.info("CodeForLean: ")
        self.log.info(lean_code)
        self.log.info("Code sent to Lean: " + code_string)

        self.lean_file.insert(label=label, add_txt=code_string)

        await self.__update(lean_code)

    async def code_set(self, label: str, code: str):
        """
        Sets the code for the current exercise.
        """
        self.log.info("Code sent to Lean: " + code)
        if not code.endswith(","):
            code += ","

        if not code.endswith("\n"):
            code += "\n"

        self.lean_file.state_add(label, code)
        await self.__update()
