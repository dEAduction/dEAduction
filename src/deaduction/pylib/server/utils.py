"""
utils.py : utilities for the ServerInterface class
    
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

from typing import Optional, List
import logging

from copy import deepcopy

from deaduction.pylib.coursedata import Course
from deaduction.pylib.actions import CodeForLean, get_effective_code_numbers


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
    """
    
    def __init__(self, seq_num):
        self.seq_num = seq_num
        self.log = logging.getLogger("HighLevelServerRequest")
        self.lean_code = None  # Set by subclasses
        self.request_type = None

    def file_content(self):
        """
        To be defined in each subclass.
        """
        pass

    def add_hypo_analysis(self, analysis, line):
        pass

    def add_targets_analysis(self, analysis, line):
        pass

    def is_complete(self) -> bool:
        return False


class InitialProofStateRequest(HighLevelServerRequest):
    """
    
    """
    def __init__(self, seq_num, course: Course, statements: [] = None):
        super().__init__(seq_num)
        self.course = course
        self.statements = statements if statements else course.statements

        # The following dictionaries provide access to a given statement
        # from the line where hypo_analysis / targets_analysis is called.
        self.statement_from_hypo_line = dict()
        self.statement_from_targets_line = dict()
        # Analyses will be stored here:
        self.analysis_from_hypo_line = dict()
        self.analysis_from_targets_line = dict()

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
        hypo_tactic    = "    hypo_analysis #{},"
        targets_tactic = "    targets_analysis #{},"

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
            tag = str(self.seq_num) + '.' + str(counter)
            lines.insert(begin_line, hypo_tactic.format(tag))
            lines.insert(begin_line+1, targets_tactic.format(tag))
            self.statement_from_hypo_line[begin_line+1] = statement
            self.statement_from_targets_line[begin_line+2] = statement
            # No shift if end_line = begin_line + 3
            shift += 3 - (end_line - begin_line)
            # self.log.debug(f"Shift: {shift}")
            # Construct virtual file

        file_contents = "\n".join(lines)
        # print(file_contents)
        return file_contents

    ####################
    # response methods #
    ####################
    def add_hypo_analysis(self, analysis, line=None):
        if line in self.statement_from_hypo_line.keys():
            self.analysis_from_hypo_line[line] = analysis
        else:
            self.log.warning("Bad line in hypo_analysis")

    def add_targets_analysis(self, analysis, line=None):
        if line in self.statement_from_targets_line.keys():
            self.analysis_from_targets_line[line] = analysis
        else:
            self.log.warning("Bad line in targets_analysis")

    def is_complete(self) -> bool:
        nb = self.expected_analyses_nb
        hypo_test = len(self.analysis_from_hypo_line) == nb
        targets_test = len(self.analysis_from_targets_line) == nb
        return hypo_test and targets_test

    def get_ips_for_hypo_line(self, hypo_line) -> bool:
        """
        Warning: target line is supposed to be hypo_line +1.
        """
        hypo = self.analysis_from_hypo_line[hypo_line]
        target = self.analysis_from_targets_line[hypo_line+1]
        if hypo and target:
            statement = self.statement_from_hypo_line[hypo_line]
            if not statement.initial_proof_state:
                ps = ProofState.from_lean_data(hypo, target, to_prove=False)
                statement.initial_proof_state = ps
                # Emit signal in case an exercise is waiting for its ips
                return True
        return False


class ProofStepRequest(HighLevelServerRequest):
    """
    
    """

    def __init__(self, seq_num, proof_step=None):
        super().__init__(seq_num)
        self.proof_step = proof_step
        self.hypo_analyses: [str] = []
        self.targets_analysis = ""

        if self.lean_code:
            self.effective_code = deepcopy(self.lean_code)

        self.request_type = 'ProofStep'
        # TODO: handle effective_code

    def file_contents(self):
        # TODO
        #  Choose fast method if some computation has been done
        pass

    @property
    def lean_code(self):
        return self.proof_step.lean_code

    ####################
    # response methods #
    ####################
    def add_hypo_analysis(self, analysis, line=None):
        self.hypo_analyses.append(analysis)

    def add_targets_analysis(self, analysis, line=None):
        self.targets_analysis = analysis

    def process_effective_code(self, msg):
        for txt_line in msg.splitlines():
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
                self.log.debug("(selecting effective code)")

    @property
    def expected_nb_hypos(self):
        """
        Return the number of targets, estimated by the number of occurence of
        '¿¿¿' in self.__tmp_targets_analysis.
        NB:     -1 indicates no information,
                0 indicates no more goals.
        """
        return self.targets_analysis.count('¿¿¿')

    def is_complete(self) -> bool:
        """
        Check if all requested pieces of info has been retrieved:
        - targets and hypo analysis (coherent number)
        - effective_code.
        """
        # TODO: add effective code emit
        analysis_complete = len(self.hypo_analyses) == self.expected_nb_hypos
        effective_code_complete = not self.effective_code.has_or_else()
        return analysis_complete and effective_code_complete


class ExerciseRequest(ProofStepRequest):
    """

    """
    expected_nb_hypos = 1

    def __init__(self, seq_num, proof_step, exercise=None):
        super().__init__(seq_num, proof_step)
        self.exercise = exercise
        self.virtual_file = None
        self.request_type = 'Exercise'

        self.compute_virtual_file()

    def compute_virtual_file(self):
        """
        Create a virtual file from exercise. Concretely, this consists in
        - separating the part of the file before the proof into a preamble,
        - add the tactics "hypo_analysis, targets_analysis"
        - remove all statements after the proof.

        If exercise.negate_statement, then the statement is replaced by its
        negation.

        Then a virtual file is instantiated.
        """
        # FIXME: should be str, not LeanFile
        statement = self.exercise
        file_content = statement.course.file_content
        lines        = file_content.splitlines()
        begin_line   = statement.lean_begin_line_number

        # Construct short end of file by closing all open namespaces
        end_of_file = "end\n"
        end_of_file += statement.close_namespace_str()
        # namespaces = statement.ugly_hierarchy()
        # while namespaces:
        #     namespace = namespaces.pop()
        #     end_of_file += "end " + namespace + "\n"
        end_of_file += "end course"

        # Replace statement by negation if required
        if (hasattr(statement, 'negate_statement')
                and statement.negate_statement):
            # lean_core_statement = statement.lean_core_statement
            # negation = " not( " + lean_core_statement + " )"
            lemma_line = statement.lean_line - 1
            # rough_core_content = "\n".join(lines[lemma_line:begin_line]) + "\n"
            # new_core_content = rough_core_content.replace(
            #                         lean_core_statement, negation)
            negated_goal = statement.negated_goal()
            new_core_content = negated_goal.to_lean_example()
            virtual_file_preamble = "\n".join(lines[:lemma_line]) \
                                    + "\n" + new_core_content \
                                    + "begin\n"
            # Debug
            # core = lines[lemma_line] + "\n" + new_core_content + "begin\n"
            # print(core)

        else:
            # Construct virtual file
            virtual_file_preamble = "\n".join(lines[:begin_line]) + "\n"

        # virtual_file_afterword = "hypo_analysis,\n" \
        #                          "targets_analysis,\n" \
        #                          + end_of_file

        virtual_file_afterword = self.__analysis_code() + end_of_file

        virtual_file = LeanFile(file_name=statement.lean_name,
                                preamble=virtual_file_preamble,
                                afterword=virtual_file_afterword)
        # Ensure file is different at each new request:
        # (avoid "file unchanged" response)
        virtual_file.add_seq_num(self.request_seq_num)

        virtual_file.cursor_move_to(0)
        virtual_file.cursor_save()

        self.virtual_file = virtual_file

    def file_contents(self):
        return self.virtual_file.contents
        # """
        # Create a virtual file from exercise. Concretely, this consists in
        # - separating the part of the file before the proof into a preamble,
        # - add the tactics "hypo_analysis, targets_analysis"
        # - remove all statements after the proof.
        #
        # If exercise.negate_statement, then the statement is replaced by its
        # negation.
        #
        # Then a virtual file is instantiated.
        # """
        # # FIXME: should be str, not LeanFile
        # statement = self.exercise
        # file_content = statement.course.file_content
        # lines        = file_content.splitlines()
        # begin_line   = statement.lean_begin_line_number
        #
        # # Construct short end of file by closing all open namespaces
        # end_of_file = "end\n"
        # end_of_file += statement.close_namespace_str()
        # # namespaces = statement.ugly_hierarchy()
        # # while namespaces:
        # #     namespace = namespaces.pop()
        # #     end_of_file += "end " + namespace + "\n"
        # end_of_file += "end course"
        #
        # # Replace statement by negation if required
        # if (hasattr(statement, 'negate_statement')
        #         and statement.negate_statement):
        #     # lean_core_statement = statement.lean_core_statement
        #     # negation = " not( " + lean_core_statement + " )"
        #     lemma_line = statement.lean_line - 1
        #     # rough_core_content = "\n".join(lines[lemma_line:begin_line]) + "\n"
        #     # new_core_content = rough_core_content.replace(
        #     #                         lean_core_statement, negation)
        #     negated_goal = statement.negated_goal()
        #     new_core_content = negated_goal.to_lean_example()
        #     virtual_file_preamble = "\n".join(lines[:lemma_line]) \
        #                             + "\n" + new_core_content \
        #                             + "begin\n"
        #     # Debug
        #     # core = lines[lemma_line] + "\n" + new_core_content + "begin\n"
        #     # print(core)
        #
        # else:
        #     # Construct virtual file
        #     virtual_file_preamble = "\n".join(lines[:begin_line]) + "\n"
        #
        # # virtual_file_afterword = "hypo_analysis,\n" \
        # #                          "targets_analysis,\n" \
        # #                          + end_of_file
        #
        # virtual_file_afterword = self.__analysis_code() + end_of_file
        #
        # virtual_file = LeanFile(file_name=statement.lean_name,
        #                         preamble=virtual_file_preamble,
        #                         afterword=virtual_file_afterword)
        # # Ensure file is different at each new request:
        # # (avoid "file unchanged" response)
        # virtual_file.add_seq_num(self.request_seq_num)
        #
        # virtual_file.cursor_move_to(0)
        # virtual_file.cursor_save()
        # return virtual_file


