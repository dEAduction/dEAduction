"""
# server_course_data.py : <#ShortDescription> #
    
    <#optionalLongDescription>

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

from deaduction.pylib.coursedata        import Course


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
        self.file_contents = self.set_file_contents()

    def set_file_contents(self):
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

        file_contents = "\n".join(lines)
        return file_contents


