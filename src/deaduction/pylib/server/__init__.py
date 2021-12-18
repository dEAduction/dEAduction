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
from typing import Optional

# from deaduction.pylib.utils.nice_display_tree import nice_display_tree
from deaduction.pylib.coursedata.exercise_classes import Exercise, Statement
from deaduction.pylib.proof_state.proof_state import ProofState
from deaduction.pylib.lean.response import Message
from deaduction.pylib.editing import LeanFile
from deaduction.pylib.lean.request import SyncRequest
from deaduction.pylib.lean.server import LeanServer
from deaduction.pylib.lean.installation import LeanEnvironment
from deaduction.pylib.actions import CodeForLean, get_effective_code_numbers
from deaduction.pylib.coursedata import Course
from deaduction.pylib.proof_tree import LeanResponse


import deaduction.pylib.config.site_installation as inst
import deaduction.pylib.server.exceptions as exceptions
from deaduction.pylib.server.utils import CourseData

from PySide2.QtCore import Signal, QObject

############################################
# Lean magic messages
############################################
LEAN_UNRESOLVED_TEXT = "tactic failed, there are unsolved goals"
LEAN_NOGOALS_TEXT    = "tactic failed, there are no goals to be solved"
LEAN_USES_SORRY      = " uses sorry"

global _


#####################
# ServerQueue class #
#####################
class ServerQueue(list):
    """
    This class stores a list of pending task for Lean server, and launches the
    first task in the list when the previous task is done.
    The "next_task" method is also responsible for the timeout: if the task
    is not done within TIMEOUT, then the request is sent another time with
    doubled timeout, and again until NB_TRIALS is reached.
    A cancellation method can be applied when a task is cancelled.
    """

    TIMEOUT = 10  # 20 FIXME
    STARTING_TIMEOUT = 20  # 40
    NB_TRIALS = 2  # 3 FIXME

    def __init__(self, nursery, timeout_signal):
        super().__init__()
        self.log = logging.getLogger("ServerQueue")

        # Initial parameters
        self.nursery                               = nursery
        self.timeout_signal                        = timeout_signal

        # Tags
        self.started = False
        self.is_busy = False

        # Cancel scope
        self.cancel_scope: Optional[trio.CancelScope] = None
        self.actual_timeout = self.TIMEOUT

        # Trio Event, initialized when a new queue starts,
        # and set when it ends.
        self.queue_ended            = None

    def add_task(self, fct, *args, cancel_fct=None, on_top=False):
        """
        Add a task to the queue. The task may be added at the end of the
        queue (default), or on top. If queue is not busy, that is, no task
        is currently running, then call next_task so that the added task
        starts immediately.
        """
        if on_top:
            self.append((fct, cancel_fct, args))
            self.log.debug(f"Adding task on top")
        else:
            self.log.debug(f"Adding task")
            self.insert(0, (fct, cancel_fct, args))
        if not self.is_busy:  # Execute task immediately
            self.is_busy = True
            self.queue_ended = trio.Event()
            self.next_task()

    def next_task(self):
        """
        Start first task of the queue, if any.
        """
        if len(self) > 0:
            # Launch first task
            fct, cancel_fct, args = self.pop()
            self.log.debug(f"Launching task")  # : {args}")
            # continue_ = input("Launching task?")  # FIXME: debugging
            self.nursery.start_soon(self.task_with_timeout, fct, cancel_fct,
                                    args)
        else:
            self.is_busy = False
            self.queue_ended.set()
            self.log.debug(f"No more tasks")

    async def process_task(self, fct: callable, *args, timeout=True):
        """
        Wait for the queue to end, and then process fct.
        This allows to await for the end of the task, which is not possible
        if the task is put into the queue.
        This method is deprecated, all tasks should go through add_task().
        """

        if self.queue_ended is not None:
            await self.queue_ended.wait()
        if timeout:
            await self.task_with_timeout(fct, args)
        else:
            await fct(*args)

    async def task_with_timeout(self, fct: callable, cancel_fct, args: tuple):
        """
        Execute function fct with timeout TIMEOUT, and number of trials
        NB_TRIALS.

        The tuple args will be unpacked and used as arguments for fct.

        When execution is complete, the next task in ServerQueue is launched.

        If task is canceled, cancel_fct is called.
        """
        nb = 0
        if not self.started:
            # Set timeout at the very first task
            self.actual_timeout = self.STARTING_TIMEOUT
            self.started = True
        else:
            self.actual_timeout = self.TIMEOUT
        while nb < self.NB_TRIALS:
            nb += 1
            try:
                with trio.move_on_after(self.actual_timeout) \
                        as self.cancel_scope:
                    ################
                    # Process task #
                    await fct(*args)
                    ################
                if self.cancel_scope.cancelled_caught:
                    self.log.warning(f"No answer within "
                                     f"{self.actual_timeout}s (trial {nb})")
                    self.actual_timeout = 2 * self.actual_timeout
                    if nb == self.NB_TRIALS:  # Task definitively  cancelled!
                        # Emit lean_response signal with timeout error
                        self.timeout_signal.emit(None, False, ("", ""), [], 3)
                    else:  # Task will be tried again
                        if cancel_fct:
                            cancel_fct()
                else:
                    break
            except TypeError as e:
                self.log.debug("TypeError while cancelling trio")
                self.log.debug(e)
                self.actual_timeout = 2 * self.actual_timeout
                if nb == self.NB_TRIALS:  # Task definitively  cancelled!
                    # Emit lean_response signal with timeout error
                    self.timeout_signal.emit(None, False, ("", ""), [], 3)
                else:  # Task will be tried again
                    if cancel_fct:
                        cancel_fct()

        # Launch next task when done!
        self.next_task()


#########################
# ServerInterface class #
#########################

class ServerInterface(QObject):
    """
    High level interface to lean server, as handled by the low level
    module lean. Two kind of requests are considered:

        - processing one exercise: the content of self.lean_file is sent to
        Lean, and the data for computing the new proof state is received.

        - processing the initial proof states of a list of statements,
        as stored in self.__course_data.

    In the first case, self.__course_data is assumed to be None.

    The ServerInterface may process only one task at a time.
    The queue is handled by a ServerQueue instance.
    """
    ############################################
    # Qt Signals
    ############################################
    proof_state_change = Signal(ProofState)  # FIXME: suppress
    update_started              = Signal()  # Unused
    update_ended                = Signal()  # Unused

    proof_no_goals              = Signal()  # FIXME: suppress
    failed_request_errors       = Signal()  # FIXME: suppress?

    # Signal sending info from Lean
    # lean_response = Signal(Statement, bool, tuple, list, int)
    lean_response = Signal(LeanResponse)
    # timeout_signal = Signal()

    # For functionality using ipf (tooltips, implicit definitions):
    initial_proof_state_set     = Signal()
    # To store effective code, so that history_replace is called:
    effective_code_received     = Signal(CodeForLean)
    # To update the Lean editor console:
    lean_file_changed           = Signal(str)
    # To launch the Coordinator.server_task:
    exercise_set                = Signal()

    MAX_CAPACITY = 10  # Max number of statements sent in one request

    ############################################
    # Init, and state control
    ############################################
    def __init__(self, nursery):
        super().__init__()
        self.log = logging.getLogger("ServerInterface")

        # Lean environment
        self.lean_env: LeanEnvironment = LeanEnvironment(inst)

        # Lean attributes
        self.lean_server: LeanServer   = LeanServer(nursery, self.lean_env)
        self.nursery: trio.Nursery     = nursery
        self.request_seq_num           = -1

        # Set server callbacks
        self.lean_server.on_message_callback = self.__on_lean_message
        self.lean_server.running_monitor.on_state_change_callback = \
            self.__on_lean_state_change

        # Current exercise (when processing one exercise)
        self.lean_file: Optional[LeanFile] = None
        self.__exercise_current            = None

        # Current course (when processing a bunch of statements for initial
        # proof state)
        self.__course_data             = None

        # Events
        self.lean_server_running       = trio.Event()
        self.file_invalidated          = trio.Event()
        self.__proof_state_valid       = trio.Event()  # FIXME: useless

        # proof_receive_done is set when enough information have been
        # received, i.e. (for exercise processing) either we have context and
        # target and all effective codes, OR an error message
        self.proof_receive_done      = trio.Event()

        self.__tmp_hypo_analysis       = ""
        self.__tmp_targets_analysis    = ""

        # When some CodeForLean is sent to the __update method, it will be
        # duplicated and stored in __tmp_effective_code. This attribute will
        # be progressively modified into an effective code which is devoid
        # of or_else combinator, according to the "EFFECTIVE CODE" messages
        # sent by Lean.
        self.__tmp_effective_code      = CodeForLean.empty_code()
        self.proof_state               = None
        self.no_more_goals             = False
        self.is_running                = False
        self.last_content              = ""  # Content of last LeanFile sent.

        # Errors memory channels
        self.error_send, self.error_recv = \
            trio.open_memory_channel(max_buffer_size=1024)

        # ServerQueue
        self.server_queue = ServerQueue(nursery=nursery,
                                        timeout_signal=self.lean_response)

    @property
    def lean_file_contents(self):
        if self.__course_data:
            return self.__course_data.file_contents
        elif self.lean_file:
            return self.lean_file.contents

    async def start(self):
        """
        Asynchronously start the Lean server.
        """
        await self.lean_server.start()
        self.file_invalidated.set()  # No file at starting
        self.lean_server_running.set()

    def stop(self):
        """
        Stop the Lean server.
        """
        # global SERVER_QUEUE
        # SERVER_QUEUE.started = False
        self.server_queue.started = False
        self.lean_server_running = trio.Event()
        self.lean_server.stop()

    def __add_time_to_cancel_scope(self):
        """
        Reset the deadline of the cancel_scope.
        """
        if self.server_queue.cancel_scope:
            time = self.server_queue.actual_timeout
            self.server_queue.cancel_scope.deadline = (trio.current_time()
                                                       + time)
            # deadline = (self.server_queue.cancel_scope.deadline
            #             - trio.current_time())
            # self.log.debug(f"Cancel scope deadline: {deadline}")

    ############################################
    # Callbacks from lean server
    ############################################
    def __check_receive_state(self):
        """
        Check if every awaited piece of information has been received:
        i.e. target and hypo analysis, and all effective codes to replace
        the or_else instructions. After the signal proof_receive_done is
        set, the __update method will stop listening to Lean, and start
        updating Proofstate.
            (for processing exercise only)
        """
        if self.__tmp_targets_analysis \
                and self.__tmp_hypo_analysis \
                and not self.__tmp_effective_code.has_or_else():
            self.proof_receive_done.set()

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
            (for processing exercise only ; for initial proof states
            processing, this method just call the
            __on_lean_message_for_course method).
        """
        self.__add_time_to_cancel_scope()

        # Filter seq_num
        if msg.seq_num:
            msg_seq_num = msg.seq_num
            req_seq_num = self.request_seq_num
            # self.log.debug(f"Received msg with seq_num {msg_seq_num}")
            if msg.seq_num != req_seq_num :
                self.log.warning(f"Request seq_num is {req_seq_num}: "
                                 f"ignoring msg form seq_num {msg.seq_num}")
                return

        if self.__course_data:
            self.__on_lean_message_for_course(msg)
            return

        txt = msg.text
        # self.log.debug("Lean message: " + txt)
        line = msg.pos_line
        severity = msg.severity

        if severity == Message.Severity.error:
            self.log.error(f"Lean error at line {line}: {txt}")
            self.__filter_error(msg)  # Record error ?

        elif severity == Message.Severity.warning:
            if not txt.endswith(LEAN_USES_SORRY):
                self.log.warning(f"Lean warning at line {line}: {txt}")

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
                #  or_else alternative according to codes
                self.__tmp_effective_code, found = \
                    self.__tmp_effective_code.select_or_else(node_nb, code_nb)
                if found:
                    self.log.debug("(selecting effective code)")

            # Test if there remain some or_else combinators
            if not self.__tmp_effective_code.has_or_else():
                # Done with effective codes, history_replace will be called
                self.log.debug("No more effective code to receive")
                if hasattr(self.effective_code_received, 'emit'):
                    self.effective_code_received.emit(self.__tmp_effective_code)
                self.__check_receive_state()

    def __on_lean_state_change(self, is_running: bool):
        self.__add_time_to_cancel_scope()

        if is_running != self.is_running:
            self.log.info(f"New lean state: {is_running}")
            self.is_running = is_running

    def __check_receive_course_data(self, index):
        """
        Check if context and target has been received
        for the statement corresponding to index.
        If so,
            - set initial proof state for statement,
            - emi signal initial_proof_state_set,
            - check if all statements have been processed, and if so,
            emit signal proof_receive_done
        """
        hypo = self.__course_data.hypo_analysis[index]
        target = self.__course_data.targets_analysis[index]
        if hypo and target:
            statements = self.__course_data.statements
            st = statements[index]
            if not st.initial_proof_state:
                ps = ProofState.from_lean_data(hypo, target)
                st.initial_proof_state = ps
                # Emit signal in case an exercise is waiting for its ips
                self.initial_proof_state_set.emit()

            if None not in [st.initial_proof_state for st in
                            self.__course_data.statements]:
                self.log.debug("All proof states received")
                self.proof_receive_done.set()

    def __on_lean_message_for_course(self, msg: Message):
        """
        Treatment of relevant Lean messages.
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
            if line in self.__course_data.statement_from_hypo_line:
                st = self.__course_data.statement_from_hypo_line[line]
                index = self.__course_data.statements.index(st)
                self.log.info(f"Got new context for statement {st.lean_name}, "
                              f"index = {index}")
                self.__course_data.hypo_analysis[index] = txt
                self.__check_receive_course_data(index)
            else:
                self.log.debug(f"(Context for statement line {line} "
                               f"received but not expected)")
        elif txt.startswith("targets:"):
            if line in self.__course_data.statement_from_targets_line:
                st = self.__course_data.statement_from_targets_line[line]
                index = self.__course_data.statements.index(st)
                self.log.info(f"Got new targets for statement {st.lean_name}, "
                              f"index = {index}")
                self.__course_data.targets_analysis[index] = txt
                self.__check_receive_course_data(index)

            else:
                self.log.debug(f"(Target for statement line {line} received "
                               f"but not expected)")

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
        if msg.text.startswith(LEAN_NOGOALS_TEXT) \
            and msg.pos_line == self.lean_file.last_line_of_inner_content + 1:
            self.no_more_goals = True
            self.proof_receive_done.set()  # Done receiving
            # if hasattr(self.proof_no_goals, "emit"):
            #     self.proof_receive_done.set()  # Done receiving
            #     self.proof_no_goals.emit()
        elif msg.text.startswith(LEAN_UNRESOLVED_TEXT):
            pass
        # Ignore messages that do not concern current proof
        elif msg.pos_line < self.lean_file.first_line_of_last_change \
                or msg.pos_line > self.lean_file.last_line_of_inner_content:
            pass
        else:
            self.error_send.send_nowait(msg)
            self.proof_receive_done.set()  # Done receiving

    ##########################################
    # Update proof state of current exercise #
    ##########################################
    async def __update(self, lean_code=None):
        """
        Call Lean server to update the proof_state.
            (for processing exercise only)
        """
        exercise = self.__exercise_current
        first_line_of_change = self.lean_file.first_line_of_last_change
        self.log.debug(f"Updating, "
                       f"checking errors from line "
                       f"{first_line_of_change}, and context at "
                       f"line {self.lean_file.last_line_of_inner_content + 1}")

        if lean_code:
            self.__tmp_effective_code = deepcopy(lean_code)
        else:
            self.__tmp_effective_code = CodeForLean.empty_code()
        # Update the lean text editor:
        self.lean_file_changed.emit(self.lean_file.inner_contents)

        if hasattr(self.update_started, "emit"):
            self.update_started.emit()

        # Invalidate events
        self.file_invalidated = trio.Event()
        self.proof_receive_done = trio.Event()
        self.__course_data = None
        self.no_more_goals = False
        self.__tmp_hypo_analysis = ""
        self.__tmp_targets_analysis = ""

        resp = None
        # Loop in case Lean's answer is None, which happens...
        while not resp:
            self.request_seq_num += 1
            # self.request_seq_num = req.seq_num  # Always zero!
            self.log.debug(f"Request seq_num: {self.request_seq_num}")
            req = SyncRequest(file_name="deaduction_lean",
                              content=self.lean_file_contents)
            resp = await self.lean_server.send(req)

        if resp.message in ("file invalidated", "file_unchanged"):
            self.log.debug("Response seq_num: "+str(resp.seq_num))
            self.file_invalidated.set()

            #########################################
            # Waiting for all pieces of information #
            #########################################
            await self.proof_receive_done.wait()
            self.server_queue.cancel_scope.shield = True
            # ------ Up to here task may be cancelled by timeout ------ #

            self.log.debug(_("Proof State received"))

            # (Timeout added by FLR) TODO: move this at the end
            with trio.move_on_after(1):
                await self.lean_server.running_monitor.wait_ready()

            self.log.debug(_("After request"))

            if hasattr(self.update_ended, "emit"):
                self.update_ended.emit()

        else:
            self.log.warning(f"Unexpected Lean response: {resp.message}")
        # Emit exceptions ?
        error_list = []
        try:
            while True:
                error_list.append(self.error_recv.receive_nowait())
        except trio.WouldBlock:
            pass

        error_type = 1 if error_list else 0
        effective_code = (None if self.__tmp_effective_code.is_empty()
                          else self.__tmp_effective_code)
        analysis = (self.__tmp_hypo_analysis, self.__tmp_targets_analysis)

        lean_response = LeanResponse(lean_code, effective_code,
                                     self.no_more_goals,
                                     analysis,
                                     error_type)
        # self.lean_response.emit(exercise,
        #                         self.no_more_goals,
        #                         (self.__tmp_hypo_analysis,
        #                          self.__tmp_targets_analysis),
        #                         error_list,
        #                         error_type)

        self.lean_response.emit(lean_response)

    ###########################
    # Exercise initialisation #
    ###########################
    def __file_from_exercise(self, statement):
        """
        Create a virtual file from exercise. Concretely, this consists in
        - separating the part of the file before the proof into a preamble,
        - add the tactics instruction "hypo_analysis, targets_analysis"
        - remove all statements after the proof.

        If exercise.negate_statement, then the statement is replaced by its
        negation.

        Then a virtual file is instantiated.

        :param statement: Statement (most of the time an Exercise)
        """
        file_content = statement.course.file_content
        lines        = file_content.splitlines()
        begin_line   = statement.lean_begin_line_number

        # Construct short end of file by closing all open namespaces
        end_of_file = "end\n"
        namespaces = statement.ugly_hierarchy()
        while namespaces:
            namespace = namespaces.pop()
            end_of_file += "end " + namespace + "\n"
        end_of_file += "end course"

        # Replace statement by negation if required
        if (hasattr(statement, 'negate_statement')
                and statement.negate_statement):
            lean_core_statement = statement.lean_core_statement
            negation = " not( " + lean_core_statement + " )"
            lemma_line = statement.lean_line - 1
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

        virtual_file = LeanFile(file_name=statement.lean_name,
                                preamble=virtual_file_preamble,
                                afterword=virtual_file_afterword)
        # Ensure file is different at each new request:
        # (avoid "file unchanged" response)
        virtual_file.add_seq_num(self.request_seq_num)

        virtual_file.cursor_move_to(0)
        virtual_file.cursor_save()
        return virtual_file

    async def set_exercise(self, exercise: Exercise, on_top=True):
        """
        Initialise the virtual_file from exercise.

        :param exercise:        The exercise to be set
        :return:                virtual_file
        """

        self.log.info(f"Set exercise to: "
                      f"{exercise.lean_name} -> {exercise.pretty_name}")
        self.__exercise_current = exercise
        self.lean_file = self.__file_from_exercise(exercise)

        await self.__update()
        if hasattr(self, "exercise_set"):
            self.exercise_set.emit()

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

    async def history_goto(self, history_nb):
        """
        Move to a psecific place in the history of the Lean file.
        """
        self.lean_file.goto(history_nb)
        await self.__update()

    async def history_delete(self):
        """
        Delete last step of history in the lean_file. Called when FailedRequest
        Error.
        """
        self.lean_file.delete()
        await self.__update()

    def history_replace(self, code: CodeForLean):
        """
        Replace last entry in the lean_file by code without calling Lean.
        WARNING: code should be an effective code which is equivalent,
        from the Lean viewpoint, to last code entry.
        NB: this method does NOT call self.__update().

        :param code: CodeForLean
        """
        if code:
            # Formatting
            code_string = code.to_code(exclude_no_meta_vars=True)
            code_string = code_string.strip()
            if not code_string.endswith(","):
                code_string += ","
            if not code_string.endswith("\n"):
                code_string += "\n"

            lean_file = self.lean_file
            label = lean_file.history[lean_file.target_idx].label
            self.lean_file.undo()
            self.lean_file.insert(label=label, add_txt=code_string)
            # Update the lean text editor:
            self.lean_file_changed.emit(self.lean_file.inner_contents)

    ############################################
    # Code management
    ############################################
    async def code_insert(self, label: str, lean_code: CodeForLean):
        """
        Inserts code in the Lean virtual file.
        """

        # Add "no meta vars" + "effective code nb"
        # and keep track of node_counters
        lean_code, code_string = lean_code.to_decorated_code()
        code_string = code_string.strip()
        if not code_string.endswith(","):
            code_string += ","

        if not code_string.endswith("\n"):
            code_string += "\n"

        self.log.info("CodeForLean: " + lean_code.to_code())
        self.log.info(lean_code)
        # self.log.info("Code sent to Lean: " + code_string)
        # print("Code sent to Lean:")
        # nice_display_tree(code_string)

        self.lean_file.insert(label=label, add_txt=code_string)

        # Ensure content is not identical to last sent (void "no change")
        content = self.lean_file.inner_contents  # Without preamble
        if content == self.last_content:
            self.lean_file.add_seq_num(self.request_seq_num)
        self.last_content = self.lean_file.inner_contents
        
        await self.__update(lean_code)

    # @task_for_server_queue
    async def code_set(self, label: str, code: str):
        """
        Sets the code for the current exercise. This is suposed to be called
        when user sets code using the Lean console, but this functionality
        is not activated right now because it f... up the history.
        """
        self.log.info("Code sent to Lean: " + code)
        if not code.endswith(","):
            code += ","

        if not code.endswith("\n"):
            code += "\n"

        self.lean_file.state_add(label, code)
        await self.__update()

    #####################################################################
    # Methods for getting initial proof states of a bunch of statements #
    #####################################################################
    # @task_for_server_queue
    async def __get_initial_proof_states(self, course_data: CourseData):
        """
        Call Lean server to get the initial proof states of statements
        as stored in course_data.
        """
        # file_name = str(self.__course_data.course.relative_course_path)
        self.__course_data = course_data

        # Invalidate events
        self.file_invalidated           = trio.Event()
        self.proof_receive_done       = trio.Event()

        # Ask Lean server and wait for answer
        self.request_seq_num += 1
        self.log.debug(f"Request seq_num: {self.request_seq_num}")
        req = SyncRequest(file_name="deaduction_lean",
                          content=self.lean_file_contents)
        resp = await self.lean_server.send(req)

        if resp.message == "file invalidated":
            self.file_invalidated.set()

            # ───────── Waiting for all pieces of information ──────── #
            await self.proof_receive_done.wait()

            # self.log.debug(_("All proof states received"))

            if hasattr(self.update_ended, "emit"):
                self.update_ended.emit()

        # Check for next task
        # SERVER_QUEUE.next_task(self.nursery)

    def set_statements(self, course: Course, statements: [] = None,
                       on_top=False):
        """
        This methods takes a list of statements and split it into lists of
        length ≤ self.MAX_CAPACITY before calling
        self.get_initial_proof_states. This is a recursive method.
        """

        statements = list(statements)  # Just in case statements is enumerator
        if statements is None:
            statements = course.statements

        if len(statements) <= self.MAX_CAPACITY:
            self.log.debug(f"Set {len(statements)} statements")
            self.server_queue.add_task(self.__get_initial_proof_states,
                                       CourseData(course, statements),
                                       on_top=on_top)
        else:
            self.log.debug(f"{len(statements)} statements to process...")
            # Split statements
            self.set_statements(course, statements[:self.MAX_CAPACITY],
                                on_top=on_top)
            self.set_statements(course, statements[self.MAX_CAPACITY:],
                                on_top=on_top)

