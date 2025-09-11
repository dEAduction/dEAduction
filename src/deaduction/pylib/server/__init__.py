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
from time import time
from typing import Optional, Dict

# from deaduction.pylib.utils.nice_display_tree import nice_display_tree
from deaduction.pylib.coursedata.exercise_classes import Exercise
from deaduction.pylib.proof_state.proof_state import ProofState
from deaduction.pylib.lean.response import Message
from deaduction.pylib.editing import LeanFile
from deaduction.pylib.lean.request import SyncRequest
from deaduction.pylib.lean.server import LeanServer
from deaduction.pylib.lean.installation import LeanEnvironment
from deaduction.pylib.actions import CodeForLean
from deaduction.pylib.coursedata import Course
from deaduction.pylib.proof_state import LeanResponse

import deaduction.pylib.config.site_installation as inst
import deaduction.pylib.config.vars as cvars
import deaduction.pylib.server.exceptions as exceptions
from deaduction.pylib.server.high_level_request import (HighLevelServerRequest,
                                                        InitialProofStateRequest,
                                                        ProofStepRequest,
                                                        LeanCodeProofStepRequest,
                                                        ExerciseRequest)

from deaduction.pylib.config.request_method import from_previous_state_method

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
    Status is one of "", "in_queue", "launched", "answered",
    "cancellation_required", "cancelled", "done".
    duration should measure the whole duration of the task, as seen from the
    ServerQueue. That begins with the computation of the HighLevelRequest and
    ends with the reception of all pieces of data from the Lean server
    (end of ServerInterface.__get_response_for_request), including the case
    of an error, or until cancellation.
    """

    def __init__(self, fct: callable, kwargs: dict):
        self.fct = fct
        self.kwargs = kwargs
        self.status = ""

        self.cancel_fct = self.kwargs.get('cancel_fct')
        if self.cancel_fct:
            self.kwargs.pop('cancel_fct')

        self.on_top = self.kwargs.get('on_top')
        if self.on_top is not None:
            self.kwargs.pop('on_top')

        self.pertinent_duration = self.kwargs.get('pertinent_duration', True)
        if 'pertinent_duration' in self.kwargs:
            self.kwargs.pop('pertinent_duration')

        self.start_time = None
        self.end_time = None

    @property
    def duration(self):
        start = self.start_time
        end = self.end_time
        duration = end-start if end and start else None
        return duration


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
        self.task_durations: [int] = []

        # Trio Event, initialized when a new queue starts,
        # and set when it ends.
        self.queue_ended            = None
        self.lean_server_running    = None  # Set by ServerInterface

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
            self.log.debug(f"Launching task")
            # continue_ = input("Launching task?")
            self.nursery.start_soon(self.task_with_timeout, task)
            self.current_task = task
            task.status = 'launched'
        else:
            self.is_busy = False
            self.current_task = None
            self.queue_ended.set()
            self.log.debug(f"No more tasks")

    async def task_with_timeout(self, task: Task):
        """
        Execute function fct with timeout TIMEOUT, and number of trials
        NB_TRIALS.

        The tuple args will be unpacked and used as arguments for fct.

        When execution is complete, the next task in ServerQueue is launched
        by calling the next_task() method.

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
            # The following try block is here because of some error occurring
            # sometimes when cancelling trio.
            # try:
            with trio.move_on_after(self.actual_timeout) \
                    as self.cancel_scope:
                # Await Lean Server starts!
                if not self.lean_server_running.is_set():
                    await self.lean_server_running.wait()
                ################
                # Process task #
                task.start_time = time()
                await task.fct(task, **task.kwargs)
                task.end_time = time()
                print(f"task duration: {task.duration}")
                if task.pertinent_duration:
                    self.task_durations.append(task.duration)
                    # print(f"task durations: {self.task_durations}")
                ################
            if self.cancel_scope.cancelled_caught:
                self.log.debug("Cancelling current task")
                if task.status == "cancellation_required":
                    error_type = 7
                else:
                    self.log.warning(f"No answer within "
                                     f"{self.actual_timeout}s (trial {nb})")
                    error_type = 3
                    self.actual_timeout = 2 * self.actual_timeout
                no_more_trials = (nb == self.NB_TRIALS
                                  or task.status == "cancellation_required")
                if no_more_trials:
                    # Task definitively  cancelled!
                    # Emit lean_response signal with timeout error
                    lean_response = LeanResponse(error_type=error_type)
                    self.timeout_signal.emit(lean_response)
                    break
                else:  # Task will be tried again
                    if task.cancel_fct:
                        task.cancel_fct()
                        task.status = 'cancelled'
            else:
                break
            # except TypeError as e:
            #     self.log.debug("TypeError while cancelling trio")
            #     self.log.debug(e)
            #     error_type = 0
            #     if task.status == "cancellation_required":
            #         error_type = 7
            #     else:
            #         self.log.warning(f"No answer within "
            #                          f"{self.actual_timeout}s (trial {nb})")
            #         error_type = 3
            #         self.actual_timeout = 2 * self.actual_timeout
            #     no_more_trials = (nb == self.NB_TRIALS
            #                       or task.status == "cancellation_required")
            #     if no_more_trials:
            #         # Task definitively  cancelled!
            #         # Emit lean_response signal with timeout error
            #         lean_response = LeanResponse(error_type=error_type)
            #         self.timeout_signal.emit(lean_response)
            #         break
            #     else:  # Task will be tried again
            #         if task.cancel_fct:
            #             task.cancel_fct()
            #             task.status = 'cancelled'
            #
            # except Exception as e:
            #     self.log.debug(e)
            #     raise

        # Launch next task when done!
        task.status = 'done'
        self.next_task()

    def cancel_task(self, task):
        if self.current_task is task and self.cancel_scope:
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
        # self.__desirable_lean_rqst_fpps_method(force_normal=True)

        # Set server callbacks
        self.lean_server.on_message_callback = self.__on_lean_message
        self.lean_server.running_monitor.on_state_change_callback = \
            self.__on_lean_state_change

        # Current exercise (when processing one exercise)
        self.lean_file: Optional[LeanFile] = None
        self.__exercise_current            = None
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

        # Errors memory channels
        self.error_send, self.error_recv = \
            trio.open_memory_channel(max_buffer_size=1024)

        # ServerQueue
        self.server_queue = ServerQueue(nursery=nursery,
                                        timeout_signal=self.lean_response)
        self.server_queue.lean_server_running = self.lean_server_running

    async def start(self):
        """
        Asynchronously start the Lean server.
        """
        self.request_seq_num           = -1
        await self.lean_server.start()
        self.file_invalidated.set()  # No file at starting
        self.lean_server_running.set()

    async def secured_stop(self):
        """
        Stop the Lean server, but only after all pending tasks of the
        ServerQueue have been completed.
        """
        # Wait for ServerQueue to end all tasks
        if not self.server_queue.queue_ended.is_set():
            await self.server_queue.queue_ended.wait()
        self.stop()

    def stop(self):
        """
        Stop the Lean server.
        """
        self.server_queue.started = False
        self.lean_server_running = trio.Event()
        self.server_queue.lean_server_running = self.lean_server_running
        self.lean_server.stop()
        # Reset task durations
        self.server_queue.task_durations = []

    def add_task(self, task: Task):
        self.server_queue.add_task(task)

    def cancel_pending_request(self, task):
        """
        Cancel the (presumably single) request corresponding to given task.
        """
        for seq_num, rqst in self.pending_requests.items():
            if rqst.task is task:
                self.log.debug(f"Cancelling request #{seq_num}")
                self.pending_requests.pop(seq_num)
                break

    def cancel_task(self, task):
        task.status = "cancellation_required"
        self.server_queue.cancel_task(task)
        self.cancel_pending_request(task)

    def __desirable_lean_rqst_fpps_method(self, force_normal=False):
        """
        This method suggests which Lean request method will be used for next
        request (in the current exercise). It updates the cvars
        corresponding entry, so that the action module knows about it when
        it computes the next CodeForLean.
        The suggestion is only followed if cvars parameter
        Lean_request_method = "automatic".
        If not, the cvars.Lean_request_method prevails. The method
        from_previous_state_method() provides the actual method used.
        """
        # TODO: smarter decision...
        fpps = False
        if not force_normal:
            costly_instructions = ["compute_n"]
            nb = 0
            for s in costly_instructions:
                if self.lean_file.inner_contents.find(s) != -1:
                    self.log.debug("compute_n found")
                    nb += 1
            if nb > 0:
                fpps = True
                if not cvars.get('others.desirable_lean_rqst_fpps_method'):
                    self.log.info("Switching to from previous proof state "
                                  "method.")

        cvars.set('others.desirable_lean_rqst_fpps_method', fpps)

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
        if txt.find("uses sorry") == -1:
            self.log.debug(f"Lean msg for seq num {msg.seq_num} at line {line}:")
            self.log.debug(txt)

        self.__add_time_to_cancel_scope()

        if msg.seq_num in self.pending_requests:
            request = self.pending_requests[msg.seq_num]
        else:
            self.log.debug(f"ignoring msg from seq_num {msg.seq_num}")
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

    async def __get_response_for_request(self, request=None):
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
            # if self.is_running:
            #     pass

            self.__add_pending_request(request)
            self.log.debug(f"Request seq_num: {self.request_seq_num}")
            # try:
            #     self.log.info(f"Inner contents:{request.lean_file.inner_contents}")
            # except:
            #     pass
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
        if not self.pending_requests.get(self.request_seq_num):
            # Request has been cancelled
            self.log.info(f"Ignoring server's response for request "
                          f"{self.request_seq_num} (task has been cancelled)")
            return

        self.pending_requests.pop(self.request_seq_num)

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

        # Lean succeeded but with failed success msg
        if hasattr(request, "proof_step") and request.proof_step.success_msg:
            if request.proof_step.success_msg.lower().startswith(_("error")):
                # print(f"Success/error msg! {request.proof_step.success_msg}")
                # print(f"error msg: {request.proof_step.error_msg}")
                request.proof_step.error_msg = request.proof_step.success_msg
                error_type = 11

        # (4) Send information
        if isinstance(request, InitialProofStateRequest):
            self.initial_proof_state_set.emit()
            self.log.debug("Initial proof states request ended")

        if isinstance(request, ProofStepRequest):
            analyses = (request.hypo_analyses, request.targets_analyses)

            # Replace code by effective code in the Lean file
            # NOT if the last step was a replacement!
            if not request.proof_step.replaced_code:
                self.history_replace(request.effective_code)

            lean_response = LeanResponse(proof_step=request.proof_step,
                                         analyses=analyses,
                                         error_type=error_type,
                                         error_list=error_list,
                                         from_previous_state=request.from_previous_state_method)
            self.lean_response.emit(lean_response)

        self.log.debug(f"End of request #{str(resp.seq_num)}")
        # Timeout TODO: move this at the end
        # FIXME: useful??
        with trio.move_on_after(1):
            await self.lean_server.running_monitor.wait_ready()

    async def set_exercise(self, task, proof_step, exercise: Exercise):
        """
        Initialise the lean_file from exercise, and call Lean.
        """

        self.log.info(f"Set exercise to: "
                      f"{exercise.lean_name} -> {exercise.pretty_name}")
        self.__exercise_current = exercise

        if exercise.negate_statement and not exercise.initial_proof_state:
            self.log.warning("No for initial proof state to negate goal: "
                             "cancelling")
            self.cancel_task(task)

        request = ExerciseRequest(task=task,
                                  proof_step=proof_step,
                                  exercise=exercise)
        self.lean_file = request.lean_file
        # self.log.debug("Lean file content:")
        # self.log.debug(self.lean_file.contents)

        await self.__get_response_for_request(request=request)

        # Method for next request = normal
        self.__desirable_lean_rqst_fpps_method(force_normal=True)
        self.exercise_set.emit()

    # async def code_replace(self, task, label, proof_step):
    #     """
    #     Replace a piece of code in the lean_file.
    #     This is used when instantiating jokers.
    #     """
    #
    #     # FIXME: find info in proof_step.code_for_lean
    #
    #     old = ""
    #     new = ""
    #     self.lean_file.replace(old, new)
    #     request = LeanCodeProofStepRequest(task=task,
    #                                        proof_step=proof_step,
    #                                        exercise=self.__exercise_current,
    #                                        lean_file=self.lean_file)
    #
    #     await self.__get_response_for_request(request=request)

    async def code_insert(self, task, label: str, proof_step):
        """
        Inserts code in the Lean virtual file (or replace it). Build a
        Request for Lean, and call self.__get_response.
        """

        replaced_code = proof_step.lean_code.replaced_code
        if replaced_code:
            fpps_method = False
        else:
            fpps_method = from_previous_state_method()

        request = ProofStepRequest(task=task,
                                   proof_step=proof_step,
                                   exercise=self.__exercise_current,
                                   lean_file=self.lean_file,
                                   from_previous_proof_state_method=fpps_method)

        code_str = request.code_string

        if replaced_code:
            self.log.debug("Replacing text in Lean file")
            # ecs = replaced_code.effective_code_sent
            # cs = replaced_code.code_sent
            old_text = replaced_code.raw_code()
            replace_text: bool = self.lean_file.replace(old=old_text,
                                                         new=code_str)
            if not replace_text:
                self.log.warning(f"Replaced code not found:\n {old_text}"
                                 f"\nin code:\n{self.lean_file.inner_contents}")
        else:
            self.lean_file.insert(label=label, add_txt=request.code_string)

        await self.__get_response_for_request(request=request)

        self.__desirable_lean_rqst_fpps_method()

    async def code_set(self, task, label: str, code: str,
                       proof_step):
        """
        Sets the code for the current exercise. This is supposed to be called
        when user sets code using the Lean console, but this functionality
        is not activated right now because it f... up the history.
        """

        # Ensure code ends with ",\n"
        code = code.strip('\n ')
        if not code.endswith(","):
            code += ","
        code += "\n"

        self.log.info("Code sent to Lean: " + code)

        # New entry in the LeanFile
        self.lean_file.set_code(code)

        request = LeanCodeProofStepRequest(task=task,
                                           proof_step=proof_step,
                                           exercise=self.__exercise_current,
                                           lean_file=self.lean_file)

        await self.__get_response_for_request(request=request)

    def history_replace(self, code: CodeForLean):
        """
        Replace last entry in the lean_file by code without calling Lean.
        WARNING: code should be an effective code which is equivalent,
        from the Lean viewpoint, to last code entry.
        NB: this method does NOT call self.__update().

        :param code: CodeForLean
        """
        if code:
            code_string = code.raw_code()
            self.lean_file.history_replace(code_string)
            # Update the lean text editor:
            self.lean_file_changed.emit(self.lean_file.inner_contents)

    #####################################################################
    # Methods for getting initial proof states of a bunch of statements #
    #####################################################################

    async def __get_initial_proof_states(self, task, course, statements):
        """
        Call Lean server to get the initial proof states of statements
        as stored in course_data.
        """

        self.log.info('Asking Lean for initial proof states')
        request = InitialProofStateRequest(task=task,
                                           course=course,
                                           statements=statements)
        await self.__get_response_for_request(request)

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
            task = Task(fct=self.__get_initial_proof_states,
                        kwargs={'course': course,
                                'statements': statements,
                                'on_top': on_top,
                                'pertinent_duration': False})
            self.server_queue.add_task(task)

        else:

            self.log.debug(f"{len(statements)} statements to process...")
            # Split statements
            self.set_statements(course, statements[:self.MAX_CAPACITY],
                                on_top=on_top)
            self.set_statements(course, statements[self.MAX_CAPACITY:],
                                on_top=on_top)

