"""
high_level_request.py : utilities for the ServerInterface class
    
    Contains the CourseData class, which pre-processes some data for the
    ServerInterface class to process a list of statements of a given course.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 07 2021 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the d∃∀duction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    d∃∀duction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

# TODO:
#  Smart choice of method (from_previous_state or not):
#           - Calcul du temp de requete
#           - excessive memory consumption detected at 'expression replacer' (potential solution: increase memory consumption threshold)
#           - timeout atteint
#   startcoex :  --> Copier fichier dans usr_lean_exercises_dir

# FIXME:
#  (bof) hypo_analyses = trier par nb
#  A quoi sert await self.lean_server.running_monitor.wait_ready()
#  Tester from_state_method !!!

# (OK?)  Négation d'une implication : C++ object already deleted ????
# (OK?) Remettre les tests de lignes pour les erreurs : OK ---> tester !

# TODO:
#  Adapter le prooftree: on a maintenant tous les goals, avec contexte.
#  Focus sur la fenetre de choix dans startcoex ??

from typing import Dict, List
import logging
from copy import deepcopy

from deaduction.pylib.editing import LeanFile
from deaduction.pylib.coursedata import Course
from deaduction.pylib.proof_state.proof_state import ProofState
from deaduction.pylib.actions import get_effective_code_numbers


################################
# HighLevelServerRequest class #
################################
class HighLevelServerRequest:
    """
    A class to store high level info for a Lean request, and gradually
    complete the response.
    There are 3 types of requests:
    - course data request, to get initial proof states of a course's statements.
    - exercise request, to get the first proof state of a new exercise,
    - the usual proof step request.
    
    The proof_step parameter is provided only for the proof step or 
    exercise types. The course_data, resp. exercise parameters are provided 
    only for the corresponding types.

    The task parameter contains the task from which the request comes from.
    It allows to cancel the request reception when the task is cancelled.
    """
    seq_num = -1
    log = logging.getLogger("HighLevelServerRequest")
    lean_code = None  # Set by subclasses
    request_type = None
    proof_received_event = None
    targets_received = False
    effective_code_received = False

    def __init__(self, task=None):
        self.task = task

    def file_contents(self):
        """
        To be defined in each subclass.
        """
        pass

    def store_hypo_analysis(self, analysis, line):
        pass

    def store_targets_analysis(self, analysis, line):
        pass

    def is_complete(self) -> bool:
        return False

    def init_proof_received_event(self, event):
        self.proof_received_event = event

    def set_proof_received(self):
        if self.proof_received_event:
            self.proof_received_event.set()

    def set_seq_num(self, seq_num):
        self.seq_num = seq_num

    def targets_from_targets_analysis(self, targets_analysis: str) -> [str]:
        """
        Turn the string targets_analysis into a list of strings, one for each
        target.        
        """
        if targets_analysis:
            self.targets_received = True
        targets = targets_analysis.split("¿¿¿")
        # Put back "¿¿¿" and remove '\n' :
        targets = ['¿¿¿' + item.replace('\n', '') for item in targets]
        targets.pop(0)  # Removing title line ("targets:")
        return targets

    def check_seq_num(self, analysis: str) -> bool:
        """
        given analysis = "context #xxx:", check that xxx is equal to
        self.seq_num. Also works for targets.
        """
        sharp = analysis.find('#')
        colon = analysis.find(':')
        if sharp != -1 and colon > sharp:
            nb = analysis[sharp+1:colon].strip()
            nb_ = int(nb)
            test = (nb_ == self.seq_num)
            if not test:
                self.log.warning(f"Bad analysis seq num {nb}")
            return test

    @staticmethod
    def decorator_check_seq_num(func):
        """
        given analysis = "context #xxx:", check that xxx is equal to
        self.seq_num. Also works for targets.
        """
        def func_with_check(self, analysis, line=None):
            sharp = analysis.find('#')
            colon = analysis.find(':')
            if sharp == -1 or colon <= sharp:
                self.log.warning(f"Bad analysis string {analysis}")
                return

            nb = analysis[sharp+1:colon].strip()
            nb_ = int(nb)
            test = (nb_ == self.seq_num)
            if not test:
                self.log.warning(f"Bad analysis seq num {nb}")
                return

            # Test succeeded: execute function
            func(self, analysis, line)

        return func_with_check


class InitialProofStateRequest(HighLevelServerRequest):
    """
    A request to get initial proof states for a course's statements.
    Note that this request is not cancellable.
    """
    def __init__(self, task, course: Course, statements: [] = None):
        super().__init__(task=task)
        self.course = course
        self.statements = statements if statements else course.statements

        # The following dictionaries provide access to a given statement
        # from the line where hypo_analysis / targets_analysis is called.
        self.statement_from_hypo_line = dict()
        self.statement_from_targets_line = dict()
        # Analyses will be stored here:
        self.analysis_from_hypo_line: Dict[int, List[str]] = dict()
        self.analysis_from_targets_line: Dict[int, List[str]] = dict()

        self.request_type = 'IPS'

    @property
    def expected_analyses_nb(self):
        return len(self.statements)

    def file_contents(self):
        """
        Starting with course's file content,
        add "hypo/target analysis" at relevant places, once for each
        statement to be processed.
        """
        lines        = self.course.file_content.splitlines()
        hypo_tactic    = "    hypo_analysis2 {},"
        targets_tactic = "    targets_analysis2 {},"

        shift = 0  # Shift due to line insertion/deletion
        counter = -1
        for statement in self.statements:
            counter += 1
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
            # Insert seq_num and statement nb
            # tag = str(self.seq_num) + '.' + str(counter)
            tag = str(self.seq_num)
            lines.insert(begin_line, hypo_tactic.format(tag))
            lines.insert(begin_line+1, targets_tactic.format(tag))
            self.statement_from_hypo_line[begin_line+1] = statement
            self.statement_from_targets_line[begin_line+2] = statement
            # No shift if end_line = begin_line + 3
            shift += 3 - (end_line - begin_line)
            # self.log.debug(f"Shift: {shift}")
            # Construct lean file

        file_contents = "\n".join(lines)
        # print(file_contents)
        return file_contents

    ####################
    # response methods #
    ####################

    def __get_ips_for_hypo_line(self, hypo_line) -> bool:
        """
        Warning: target line is supposed to be hypo_line +1.
        """
        hypo = self.analysis_from_hypo_line.get(hypo_line)
        target = self.analysis_from_targets_line.get(hypo_line+1)
        if hypo and target:
            statement = self.statement_from_hypo_line.get(hypo_line)
            if not statement:
                self.log.warning(f"No statement at line {hypo_line}!!")
            elif not statement.initial_proof_state:
                self.log.debug("Getting proof state...")
                ps = ProofState.from_lean_data(hypo, target, to_prove=False)
                self.log.debug(" --> done")
                statement.initial_proof_state = ps
                # print(statement.statement_to_text)
                return True
        return False

    @HighLevelServerRequest.decorator_check_seq_num
    def store_hypo_analysis(self, analysis, line=None):
        if line in self.statement_from_hypo_line.keys():
            self.log.debug(f"Line {line} found")
            self.analysis_from_hypo_line[line] = [analysis]
            self.log.debug(f"Analysis stored")
        else:
            self.log.warning("Bad line in hypo_analysis")
        self.__get_ips_for_hypo_line(line)

    @HighLevelServerRequest.decorator_check_seq_num
    def store_targets_analysis(self, analysis, line=None):
        if line in self.statement_from_targets_line.keys():
            target = self.targets_from_targets_analysis(analysis)
            self.analysis_from_targets_line[line] = target
        else:
            self.log.warning("Bad line in targets_analysis")
        self.__get_ips_for_hypo_line(line - 1)

    def is_complete(self) -> bool:
        nb = self.expected_analyses_nb
        hypo_test = len(self.analysis_from_hypo_line) == nb
        targets_test = len(self.analysis_from_targets_line) == nb
        return hypo_test and targets_test


class ProofStepRequest(HighLevelServerRequest):
    """
    A request to get the new proof state from an action, as encode in a
    ProofStep instance.
    """

    def __init__(self, task, proof_step=None, exercise=None, lean_file=None,
                 from_previous_proof_state_method=False):
        super().__init__(task=task)
        self.task = task
        self.request_type = 'ProofStep'
        self.proof_step = proof_step
        self.exercise = exercise
        self.lean_file = lean_file
        self.hypo_analyses: [str] = []
        self.targets_analyses: [str] = []
        self.effective_code_received = False

        self.code_string = ""
        self.decorated_code = None  # will be decorated_code
        self.compute_code_string()
        self.effective_code = (deepcopy(self.decorated_code)
                               if self.decorated_code else None)
        self.__from_previous_state_method = from_previous_proof_state_method

    @property
    def from_previous_state_method(self):
        return self.__from_previous_state_method

    @from_previous_state_method.setter
    def from_previous_state_method(self, yes=True):
        self.__from_previous_state_method = yes

    def compute_code_string(self):
        lean_code = self.proof_step.lean_code
        self.decorated_code, code_string = lean_code.to_decorated_code()
        code_string = code_string.strip()

        if not code_string.endswith(","):
            code_string += ","
        if not code_string.endswith("\n"):
            code_string += "\n"

        self.code_string = code_string
        self.log.debug("Code sent:" + code_string)

    ##########################################
    # Compute contents for from state method #
    ##########################################
    def __lean_import_course_preamble(self) -> str:
        file_name = self.exercise.course.course_file_name
        return f"import {file_name}\n"

    @staticmethod
    def __lean_classical_logic() -> str:
        return "local attribute[instance] classical.prop_decidable\n"

    def analysis_code2(self) -> str:
        """
        NB: self.seq_num must be up to date!
        """
        nb = self.seq_num
        code = f"    targets_analysis2 {nb},\n" \
               f"    all_goals {{hypo_analysis2 {nb}}},\n"
        return  code

    def __begin_end_code(self, code_string: str) -> str:
        code_string = code_string.strip()
        if not code_string.endswith(","):
            code_string += ","

        if not code_string.endswith("\n"):
            code_string += "\n"

        code = "begin\n" \
               + code_string \
               + self.analysis_code2() \
               + "end\n"
        return code

    def __file_contents_from_previous_state(self, goal, code_string):
        """
        Set the file content from goal and code. e.g.
        import ...
        namespace ...
        open ...
        example (X: Type) : true :=
        begin
            <some code>
        end
        """
        exercise = self.exercise
        file_content = f"-- Seq num {self.seq_num}\n" \
            + self.__lean_import_course_preamble() \
            + self.__lean_classical_logic() \
            + "section course\n" \
            + exercise.open_namespace_str() \
            + exercise.open_read_only_namespace_str() \
            + goal.to_lean_example() \
            + self.__begin_end_code(code_string) \
            + exercise.close_namespace_str() \
            + "end course\n"
        return file_content

    # Compute content for Lean file #
    def set_seq_num(self, seq_num):
        self.seq_num = seq_num
        if self.lean_file:
            self.lean_file.add_seq_num(self.seq_num)
            self.set_lean_file_afterword()
            self.lean_file.cursor_move_to(0)
            self.lean_file.cursor_save()

    def lean_file_afterword(self) -> str:
        # Construct short end of file by closing all open namespaces
        statement = self.exercise
        end_of_file = "end\n"
        end_of_file += statement.close_namespace_str()
        end_of_file += "end course"
        lean_file_afterword = self.analysis_code2() + end_of_file
        return lean_file_afterword

    def set_lean_file_afterword(self):
        """
        Set the lean file afterword, with the right seq_num.
        """
        if self.lean_file:
            self.lean_file.afterword = self.lean_file_afterword()

    def file_contents(self):
        if self.from_previous_state_method:
            goal = self.proof_step.proof_state.goals[0]
            contents = self.__file_contents_from_previous_state(goal,
                                                                self.code_string)
            self.log.info('Using from state method for Lean server')
            print(contents)
            return contents
        else:
            return self.lean_file.contents

    ####################
    # response methods #
    ####################
    @HighLevelServerRequest.decorator_check_seq_num
    def store_hypo_analysis(self, analysis, line=None):
        self.hypo_analyses.append(analysis)

    @HighLevelServerRequest.decorator_check_seq_num
    def store_targets_analysis(self, analysis, line=None):
        targets = self.targets_from_targets_analysis(analysis)
        self.targets_analyses = targets

    def process_effective_code(self, txt):
        for txt_line in txt.splitlines():
            if not txt_line.startswith("EFFECTIVE CODE"):
                # Message could be "EFFECTIVE LEAN CODE"
                # TODO: treat these messages
                continue
            self.log.info(f"Got {txt_line}")
            node_nb, code_nb = get_effective_code_numbers(txt_line)
            # Modify __tmp_effective_code by selecting the effective
            #  or_else alternative according to codes
            self.effective_code, found = \
                self.effective_code.select_or_else(node_nb, code_nb)
            if found:
                self.log.debug("Selecting effective code -->")
                self.log.debug(self.effective_code)
                self.effective_code_received = True
                self.proof_step.effective_code = self.effective_code

    def is_complete(self) -> bool:
        """
        Check if all requested pieces of info has been retrieved:
        - targets and hypo analysis (coherent number)
        - effective_code.
        """
        analysis_complete = (self.targets_received and
                             len(self.hypo_analyses) ==
                             len(self.targets_analyses))
        effective_code_complete = (not self.effective_code or not
                                   self.effective_code.has_or_else())
        # Debug
        if analysis_complete:
            print(f"# targets = {len(self.targets_analyses)}")

        return analysis_complete and effective_code_complete


class ExerciseRequest(ProofStepRequest):
    """

    """
    expected_nb_hypos = 1

    def __init__(self, task, proof_step, exercise=None):
        super().__init__(task, proof_step, exercise)
        self.request_type = 'Exercise'
        self.__compute_lean_file()

    def compute_code_string(self):
        pass

    def __compute_lean_file(self):
        """
        Create a lean file from exercise. Concretely, this consists in
        - separating the part of the file before the proof into a preamble,
        - add the tactics "hypo_analysis, targets_analysis"
        - remove all statements after the proof.

        If exercise.negate_statement, then the statement is replaced by its
        negation.

        Then a lean file is instantiated.
        """

        statement = self.exercise
        file_content = statement.course.file_content
        lines        = file_content.splitlines()
        begin_line   = statement.lean_begin_line_number

        # Replace statement by negation if required
        if (hasattr(statement, 'negate_statement')
                and statement.negate_statement):
            lemma_line = statement.lean_line - 1
            negated_goal = statement.negated_goal()
            new_core_content = negated_goal.to_lean_example()
            lean_file_preamble = "\n".join(lines[:lemma_line]) \
                                    + "\n" + new_core_content \
                                    + "begin\n"
            # Debug
            # core = lines[lemma_line] + "\n" + new_core_content + "begin\n"
            # print(core)

        else:
            # Construct lean file
            lean_file_preamble = "\n".join(lines[:begin_line]) + "\n"

        afterword = self.lean_file_afterword()
        lean_file = LeanFile(file_name=statement.lean_name,
                                preamble=lean_file_preamble,
                                afterword=afterword)
        # Ensure file is different at each new request:
        # (avoid "file unchanged" response)
        # lean_file.add_seq_num(self.seq_num)
        #
        lean_file.cursor_move_to(0)
        lean_file.cursor_save()

        self.lean_file = lean_file

    def file_contents(self):
        return self.lean_file.contents

