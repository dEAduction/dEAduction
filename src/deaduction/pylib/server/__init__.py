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
from typing import Optional, Dict

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


import deaduction.pylib.config.vars as cvars
import deaduction.pylib.config.site_installation as inst
import deaduction.pylib.server.exceptions as exceptions
from deaduction.pylib.server.high_level_request import (HighLevelServerRequest,
                                                        InitialProofStateRequest,
                                                        ProofStepRequest,
                                                        ExerciseRequest)

from PySide2.QtCore import Signal, QObject

############################################
# Lean magic messages
############################################
LEAN_UNRESOLVED_TEXT = "tactic failed, there are unsolved goals"
LEAN_NOGOALS_TEXT    = "tactic failed, there are no goals to be solved"
LEAN_USES_SORRY      = " uses sorry"

global _


##############
# Task class #
##############
class Task:
    """
    A class to record a task for the server.
    Status is one of "", "in_queue", "launched", "answered", "cancelled",
    "done".
    """

    def __init__(self, fct: callable, kwargs: dict):
        self.fct = fct
        self.kwargs = kwargs
        self.status = ""

    @property
    def cancel_fct(self):
        return self.kwargs.get('cancel_fct')

    @property
    def on_top(self):
        return self.kwargs.get('on_top')


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

        # self.current_task = None

        # Cancel scope
        self.current_task = None
        self.cancel_scope: Optional[trio.CancelScope] = None
        self.actual_timeout = self.TIMEOUT

        # Trio Event, initialized when a new queue starts,
        # and set when it ends.
        self.queue_ended            = None

    def add_task(self, task: Task):
        # fct, *args, cancel_fct=None, on_top=False):
        """
        Add a task to the queue. The task may be added at the end of the
        queue (default), or on top. If queue is not busy, that is, no task
        is currently running, then call next_task so that the added task
        starts immediately.
        """
        task.status = "in_queue"
        if task.on_top:
            self.append(task)
            self.log.debug(f"Adding task on top")
        else:
            self.log.debug(f"Adding task")
            self.insert(0, task)
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
            task = self.pop()
            self.log.debug(f"Launching task")  # : {args}")
            # continue_ = input("Launching task?")  # FIXME: debugging
            self.nursery.start_soon(self.task_with_timeout, task)
            self.current_task = task
            task.status = 'launched'
        else:
            self.is_busy = False
            self.current_task = None
            self.queue_ended.set()
            self.log.debug(f"No more tasks")

    # async def process_task(self, fct: callable, *args, timeout=True):
    #     """
    #     Wait for the queue to end, and then process fct.
    #     This allows to await for the end of the task, which is not possible
    #     if the task is put into the queue.
    #     This method is deprecated, all tasks should go through add_task().
    #     """
    #
    #     if self.queue_ended is not None:
    #         await self.queue_ended.wait()
    #     if timeout:
    #         await self.task_with_timeout(fct, args)
    #     else:
    #         await fct(*args)

    async def task_with_timeout(self, task: Task):
                                # fct: callable, cancel_fct: callable, args: tuple):
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
                    await task.fct(**task.kwargs)
                    ################
                if self.cancel_scope.cancelled_caught:
                    self.current_task = None
                    self.log.warning(f"No answer within "
                                     f"{self.actual_timeout}s (trial {nb})")
                    self.actual_timeout = 2 * self.actual_timeout
                    if nb == self.NB_TRIALS:  # Task definitively  cancelled!
                        # Emit lean_response signal with timeout error
                        lean_response = LeanResponse(error_type=3)
                        self.timeout_signal.emit(lean_response)
                    else:  # Task will be tried again
                        if task.cancel_fct:
                            task.status = 'cancelled'
                            task.cancel_fct()
                else:
                    break
            except TypeError as e:
                self.log.debug("TypeError while cancelling trio")
                self.log.debug(e)
                self.actual_timeout = 2 * self.actual_timeout
                if nb == self.NB_TRIALS:  # Task definitively  cancelled!
                    # Emit lean_response signal with timeout error
                    # FIXME:
                    lean_response = LeanResponse(error_type=3)
                    self.timeout_signal.emit(lean_response)
                else:  # Task will be tried again
                    if task.cancel_fct:
                        task.status = 'cancelled'
                        task.cancel_fct()

        # Launch next task when done!
        task.status = 'done'
        self.next_task()

    def cancel_task(self, task):
        if self.current_task is task and self.cancel_scope:
            self.log.debug("Cancelling current task")
            self.cancel_scope.cancel()


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
    lean_response = Signal(LeanResponse)

    # For functionality using ipf (tooltips, implicit definitions):
    initial_proof_state_set     = Signal()
    # To store effective code, so that history_replace is called:
    effective_code_received     = Signal(CodeForLean)
    # To update the Lean editor console:
    lean_file_changed           = Signal(str)
    # To launch the Coordinator.server_task:
    exercise_set                = Signal()  # Fixme: not used!

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
        self.pending_requests: Dict[int, HighLevelServerRequest] = {}

        # Set server callbacks
        self.lean_server.on_message_callback = self.__on_lean_message
        self.lean_server.running_monitor.on_state_change_callback = \
            self.__on_lean_state_change

        # Current exercise (when processing one exercise)
        self.lean_file: Optional[LeanFile] = None
        self.__exercise_current            = None
        self.__use_fast_method_for_lean_server = False
        self.__previous_proof_state = None

        # Events
        self.lean_server_running       = trio.Event()
        self.file_invalidated          = trio.Event()

        # When some CodeForLean is sent to the __update method, it will be
        # duplicated and stored in __tmp_effective_code. This attribute will
        # be progressively modified into an effective code which is devoid
        # of or_else combinator, according to the "EFFECTIVE CODE" messages
        # sent by Lean.
        # self.__tmp_effective_code      = CodeForLean.empty_code()
        self.is_running                = False
        # self.last_content              = ""  # Content of last LeanFile sent.
        # self.__file_content_from_state_and_tactic = None
        # Errors memory channels
        # FIXME: obsolete?
        self.error_send, self.error_recv = \
            trio.open_memory_channel(max_buffer_size=1024)

        # ServerQueue
        self.server_queue = ServerQueue(nursery=nursery,
                                        timeout_signal=self.lean_response)

    @property
    def use_fast_method_for_lean_server(self):
        return self.__use_fast_method_for_lean_server

    # @property
    # def lean_file_contents(self):
    #     if self.use_fast_method_for_lean_server:
    #         return self.__file_content_from_state_and_tactic
    #     elif self.__course_data:
    #         return self.__course_data.file_contents
    #     elif self.lean_file:
    #         return self.lean_file.contents

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

    def add_task(self, task: Task):
        self.server_queue.add_task(task)

    def cancel_task(self, task):
        self.server_queue.cancel_task(task)

    def __add_time_to_cancel_scope(self):
        """
        Reset the deadline of the cancel_scope.
        """
        if self.server_queue.cancel_scope:
            time = self.server_queue.actual_timeout
            self.server_queue.cancel_scope.deadline = (trio.current_time()
                                                       + time)

    def __on_lean_state_change(self, is_running: bool):
        self.__add_time_to_cancel_scope()

        if is_running != self.is_running:
            self.log.info(f"New lean state: {is_running}")
            self.is_running = is_running

    def __check_request_complete(self, request_seq_num):
        self.log.debug(f"Checking request {request_seq_num}")
        request = self.pending_requests.get(request_seq_num)
        if request:
            if request.is_complete():
                self.log.debug("--> complete")
                request.set_proof_received()
            else:
                self.log.debug("--> not complete")

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

        check_complete = False

        txt = msg.text
        line = msg.pos_line
        self.log.debug(f"Lean msg for seq num {msg.seq_num} at line {line}:")
        self.log.debug(txt)

        self.__add_time_to_cancel_scope()

        if msg.seq_num in self.pending_requests:
            request = self.pending_requests[msg.seq_num]
        else:
            self.log.warning(f"Pending requests seq_num are {self.pending_requests.key()}: "
                             f"ignoring msg form seq_num {msg.seq_num}")
            return

        severity = msg.severity
        # last_line_of_inner_content = self.lean_file.last_line_of_inner_content

        if severity == Message.Severity.error:
            # self.log.error(f"Lean error at line {line}")
            self.__filter_error(msg, request)  # Record error ?

        elif severity == Message.Severity.warning:
            # pass
            if not txt.endswith(LEAN_USES_SORRY):
                self.log.warning(f"Lean warning at line {line}")

        elif txt.startswith("context #"):
            check_complete = True
            # FIXME: check seq_num in txt
            self.log.debug("Storing context")
            request.store_hypo_analysis(txt, line)

        elif txt.startswith("targets #"):
            check_complete = True
            self.log.debug("Storing targets")
            request.store_targets_analysis(txt, line)

        elif txt.startswith("EFFECTIVE CODE"):
            if isinstance(request, ProofStepRequest):
                self.log.debug("Processing effective code")
                request.process_effective_code(txt)
                check_complete = True
            # if request.effective_code_received:
            #     self.history_replace(request.effective_code)
            #     # self.effective_code_received.emit(request.effective_code)
            #     request.effective_code_received = False
        if check_complete:
            self.__check_request_complete(msg.seq_num)

    ############################################
    # Message filtering
    ############################################

    def __filter_error(self, msg: Message, request):
        """
        Filter error messages from Lean,
        - according to position (i.e. ignore messages that do not correspond
         to the new part of the virtual file). This is not relevant if the
         request mode is from previous state method, since all errors are
         relevant.
        - ignore "proof uses sorry" messages.
        """

        # FIXME: two first cases obsolete?
        if not isinstance(request, ProofStepRequest):
            return

        elif msg.text.startswith(LEAN_NOGOALS_TEXT):
            # todo: request complete
            return
        elif msg.text.startswith(LEAN_UNRESOLVED_TEXT):
            return
        elif not request.from_previous_state_method and self.lean_file:
            first_line = self.lean_file.first_line_of_last_change
            last_line = self.lean_file.last_line_of_inner_content
            if not first_line <= msg.pos_line <= last_line:
                self.log.debug("(error msg does not concern this proofstate)")
                return

        self.error_send.send_nowait(msg)
        request.proof_received_event.set()  # Done receiving

    ##########################################
    # Update proof state of current exercise #
    ##########################################
    def __add_pending_request(self, request: HighLevelServerRequest):
        self.request_seq_num += 1
        request.set_seq_num(self.request_seq_num)
        request.init_proof_received_event(trio.Event())
        self.pending_requests[self.request_seq_num] = request
        self.log.debug(f"Add request")
        nb = len(self.pending_requests)
        if nb > 1:
            self.log.warning(f"{nb} requests pending")

    async def __get_response_from_request(self, request=None):
        """
        Call Lean server to update the proof_state.
            (for processing exercise only)
        """

        # (1) Preliminaries
        if isinstance(request, ProofStepRequest):
            # Update the lean text editor:
            self.lean_file_changed.emit(self.lean_file.inner_contents)

        if hasattr(self.update_started, "emit"):
            self.update_started.emit()

        # Invalidate events
        self.file_invalidated = trio.Event()

        resp = None
        error_type = 0

        # (2) Let's send request to Lean
        # Loop in case Lean's answer is None, which happens...
        while not resp:
            # print(request.file_contents())
            # self.request_seq_num += 1

            # FIXME: replace wait_ready at the end by the following,
            #   with a waiting of the running state going to False.
            if self.is_running:
                pass

            self.__add_pending_request(request)
            self.log.debug(f"Request seq_num: {self.request_seq_num}")
            req = SyncRequest(file_name="deaduction_lean",
                              content=request.file_contents())
            resp = await self.lean_server.send(req)
            if not resp:
                self.pending_requests.pop(self.request_seq_num)

        # (3) Several types of response: normal/unchanged/other
        if resp.message == "file invalidated":
            self.log.debug("Response seq_num: "+str(resp.seq_num))
            self.file_invalidated.set()

            #########################################
            # Waiting for all pieces of information #
            #########################################
            await request.proof_received_event.wait()
            self.log.debug(_("Proof State received"))

        elif resp.message == "file_unchanged":
            # (This should never happen, but just in case)
            self.log.warning("File unchanged!")
            error_type = 6

        else:
            self.log.warning(f"Unexpected Lean response: {resp.message}")
            error_type = 10

        # ------ Up to here task may be cancelled by timeout ------ #
        self.server_queue.cancel_scope.shield = True
        self.pending_requests.pop(self.request_seq_num)

        # Timeout TODO: move this at the end
        # FIXME: useful??
        with trio.move_on_after(1):
            await self.lean_server.running_monitor.wait_ready()

        self.log.debug(_("After request"))

        if hasattr(self.update_ended, "emit"):
            self.update_ended.emit()

        # (3) Lean errors?
        error_list = []
        try:
            while True:
                error_list.append(self.error_recv.receive_nowait())
        except trio.WouldBlock:
            pass
        if error_list:
            error_type = 1

        # (4) Send information
        if isinstance(request, InitialProofStateRequest):
            self.initial_proof_state_set.emit()
            self.log.debug("Initial proof states request ended")

        if isinstance(request, ProofStepRequest):
            analyses = (request.hypo_analyses, request.targets_analyses)
            self.history_replace(request.effective_code)
            lean_response = LeanResponse(proof_step=request.proof_step,
                                         analyses=analyses,
                                         error_type=error_type,
                                         error_list=error_list,
                                         from_previous_state=request.from_previous_state_method)
            self.lean_response.emit(lean_response)

        self.log.debug(f"End of request #{str(resp.seq_num)}")

    async def set_exercise(self, proof_step, exercise: Exercise):
        """
        Initialise the lean_file from exercise, and call Lean.

        :param proof_step:      The current proof_step
        :param exercise:        The exercise to be set
        """

        self.log.info(f"Set exercise to: "
                      f"{exercise.lean_name} -> {exercise.pretty_name}")
        self.__exercise_current = exercise

        request = ExerciseRequest(proof_step=proof_step,
                                  exercise=exercise)
        self.lean_file = request.lean_file

        await self.__get_response_from_request(request=request)
        self.exercise_set.emit()

    async def code_insert(self, label: str, proof_step):
        """
        Inserts code in the Lean virtual file.
        """

        request = ProofStepRequest(proof_step=proof_step,
                                   exercise=self.__exercise_current,
                                   lean_file=self.lean_file)

        self.lean_file.insert(label=label, add_txt=request.code_string)

        await self.__get_response_from_request(request=request)

    async def code_set(self, label: str, code: str):
        """
        Sets the code for the current exercise. This is supposed to be called
        when user sets code using the Lean console, but this functionality
        is not activated right now because it f... up the history.
        """
        # FIXME: adapt HighLevelLeanRequest to this case

        self.__use_fast_method_for_lean_server = False
        self.__previous_proof_state = None

        self.log.info("Code sent to Lean: " + code)
        if not code.endswith(","):
            code += ","

        if not code.endswith("\n"):
            code += "\n"

        self.lean_file.state_add(label, code)

        # request = ...
        await self.__get_response_from_request()

    def history_replace(self, code: CodeForLean):
        """
        Replace last entry in the lean_file by code without calling Lean.
        WARNING: code should be an effective code which is equivalent,
        from the Lean viewpoint, to last code entry.
        NB: this method does NOT call self.__update().

        :param code: CodeForLean
        """
        if code:
            # Formatting. We do NOT want the "no_meta_vars" tactic!
            code_string = code.to_code(exclude_no_meta_vars=True,
                                       exclude_skip=True)
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

    #####################################################################
    # Methods for getting initial proof states of a bunch of statements #
    #####################################################################

    async def __get_initial_proof_states(self, course, statements):
        """
        Call Lean server to get the initial proof states of statements
        as stored in course_data.
        """

        self.log.info('Getting initial proof states')
        # Define request
        request = InitialProofStateRequest(course=course,
                                           statements=statements)

        await self.__get_response_from_request(request)

        # # TODO: try to merge this with __get_response_from_request()
        # # Invalidate events
        # self.file_invalidated           = trio.Event()
        #
        # # Sending request
        # self.request_seq_num += 1
        # request.set_seq_num(self.request_seq_num)
        # self.__add_pending_request(request)
        # self.log.debug(f"Request seq_num: {self.request_seq_num}")
        #
        # # Ask Lean server and wait for answer
        # req = SyncRequest(file_name="deaduction_lean",
        #                   content=request.file_contents())
        # resp = await self.lean_server.send(req)
        # print(f"--> {resp.message}")
        # if resp.message == "file invalidated":
        #     self.file_invalidated.set()
        #
        #     # ───────── Waiting for all pieces of information ──────── #
        #     await request.proof_received_event.wait()
        #     self.pending_requests.pop(self.request_seq_num)
        #
        #     print("(proof received)")
        #     # self.log.debug(_("All proof states received"))
        #     self.initial_proof_state_set.emit()
        #     if hasattr(self.update_ended, "emit"):
        #         self.update_ended.emit()

    def set_statements(self, course: Course, statements: [] = None,
                       on_top=False):
        """
        This method takes a list of statements and split it into lists of
        length ≤ self.MAX_CAPACITY before calling
        self.get_initial_proof_states. This is a recursive method.
        """

        statements = list(statements)  # Just in case statements is an iterator
        if statements is None:
            statements = course.statements

        if not statements:
            pass
        elif len(statements) <= self.MAX_CAPACITY:
            self.log.debug(f"Set {len(statements)} statement(s)")
            self.server_queue.add_task(self.__get_initial_proof_states,
                                       course, statements,
                                       on_top=on_top)
        else:
            self.log.debug(f"{len(statements)} statements to process...")
            # Split statements
            self.set_statements(course, statements[:self.MAX_CAPACITY],
                                on_top=on_top)
            self.set_statements(course, statements[self.MAX_CAPACITY:],
                                on_top=on_top)

