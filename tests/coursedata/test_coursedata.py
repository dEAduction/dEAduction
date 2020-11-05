"""
# test_coursedata.py : test coursedata files #

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 11 2020 (creation)
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

from deaduction.pylib.coursedata.exercise_classes import (Exercise, Definition,
                                                          Theorem, Statement)
from deaduction.pylib.coursedata import Course, parser_course


def test_course_parser(course, file_content):
    """Test lean_course_grammar from parser_course.py"""
    course_tree = parser_course.lean_course_grammar.parse(file_content)
    visitor = parser_course.LeanCourseVisitor()
    course_history, course_metadata = visitor.visit(course_tree)
    print(f"course history:\n{course_history}")
    # assert course_history ==


def test_statements_creation(file_content, statements):
    """Test Course.from_file_content method"""
    course = Course.from_file_content(file_content)
    assert len(statements) == len(course.statements)
    for st in course.statements:
        XXX = st.pretty_hierarchy(course.outline)
    for (stpkl, st) in zip(statements, course.statements):
        assert stpkl.pretty_name == st.pretty_name
        if type(stpkl) == Exercise:
            assert stpkl.available_logic == st.available_logic