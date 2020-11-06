"""
# course.py : provide the class Course
    
    Provide the class Course,
    and an instantiation method for Course object
    by parsing a lean file


Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 07 2020 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

This file is part of dEAduction.

    dEAduction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    dEAduction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
import logging

import deaduction.pylib.logger as logger
from deaduction.pylib.coursedata import (Exercise,
                                         Definition,
                                         Theorem,
                                         Statement)
import deaduction.pylib.coursedata.parser_course as parser_course

log = logging.getLogger(__name__)


@dataclass
class Course:
    """
    This class allows to store all the data related to a given course,
    which is materialised by a Lean file containing a list of definitions,
    theorems and exercises (all being statements introduced by Lean's
    keyword "lemma"), structured into namespaces that corresponds to sections.
    Th attributes are:
    - the content of the corresponding Lean file,
    - metadata (e.g. authors, institution, etc.)
    - the "outline" of the course, an ordered dict describing namespaces
    - a list of all statements
    """
    file_content:           str
    metadata:               Dict[str, str]
    outline:                OrderedDict
    statements:             List[Statement]
    course_path:            Path = None
    # course_path is added after instantiation

    # outline description:
    #   keys = lean complete namespaces,
    #   values = corresponding plain language namespace
    #   e. g. section_dict["set_theory.unions_and_intersections"] =
    #   "Unions and intersections"
    # statements is a list of all Statements, including exercises

    def print_metadata(self):
        for field_name, field_content in self.metadata.items():
            print(f"{field_name}: {field_content}")

    def exercises_list(self):
        """
        extract all the exercises from the statements list
        """
        statements = self.statements
        exercises = [item for item in statements
                     if isinstance(item, Exercise)]
        return exercises

    @classmethod
    def from_file(cls, course_path: Path):
        """
        instantiate a Course object from the provided file

        :param course_path: name of directory
        :return: a Course instance
        """
        log.info(f"Parsing file {str(course_path.resolve())}")
        file_content = course_path.read_text()
        course = Course.from_file_content(file_content)
        course.course_path = course_path
        return course

    @classmethod
    def from_file_content(cls, file_content: str):
        """
        instantiate a Course object by parsing file_content
        data fields to be parsed must start with "/- dEAduction"
        and end with "-/"

        :param file_content: str to be parsed
        :return: a Course instance
        """
        statements = []
        outline = {}
        begin_counter = 0
        begin_found = True
        ########################
        # Parsimonious's magic #
        ########################
        course_tree = parser_course.lean_course_grammar.parse(file_content)
        visitor = parser_course.LeanCourseVisitor()
        course_history, course_metadata = visitor.visit(course_tree)
        log.debug(f"course history: {course_history}")
        log.info(f"Course metadata: {course_metadata}")

        ##########################
        # parsing course_history #
        ##########################
        line_counter = 1
        namespace = []
        for event_name, event_content in course_history:
            if event_name == "end_of_line":
                line_counter += 1
                log.debug(f"Parsing line {line_counter}")

            elif event_name == "open_namespace":
                namespace.append(event_content["name"])
                outline[whole(namespace)] = event_content["pretty_name"]
                log.debug(f"namespace {whole(namespace)}")
            elif event_name == "close_namespace":
                name = event_content["name"]
                if namespace and name == namespace[-1]:
                    log.debug(f"closing namespace {name}")
                    namespace.pop()
                else:
                    log.debug(f"(just closing section(?) {name})")

            ##############
            # statements #
            ##############
            elif event_name in ["exercise", "definition", "theorem"]:
                if not begin_found:
                    log.warning(f"Missing 'begin' for statement"
                                f"{statements[-1].pretty_name}")
                begin_found = False
                metadata = event_content
                metadata["lean_line"] = line_counter
                if namespace:
                    metadata["lean_name"] = whole(namespace) + "." \
                                            + metadata["lean_name"]

            if event_name == "exercise":
                metadata.update(course_metadata)  # add potential macros
                log.info(f"creating exercise from data {metadata}")
                exercise = Exercise.from_parser_data(metadata, statements)
                statements.append(exercise)
            elif event_name == "definition":
                log.info(f"creating definition from data {metadata}")
                definition = Definition.from_parser_data(**metadata)
                statements.append(definition)
            elif event_name == "theorem":
                log.info(f"creating theorem from data {metadata}")
                theorem = Theorem.from_parser_data(**metadata)
                statements.append(theorem)

            elif event_name == "begin_proof":
                st = statements[-1]
                st.lean_begin_line_number = line_counter
                begin_counter += 1
                log.debug(f"Statements {st.pretty_name} begins at line {line_counter}")
                begin_found = True
            elif event_name == "end_proof":
                st = statements[-1]
                st.lean_end_line_number = line_counter

            continue

        # Creating the course
        course = cls(file_content=file_content,
                     metadata=course_metadata,
                     outline=outline,
                     statements=statements)

        # Test data for coherence
        counter_exercises = 0
        counter = 0
        for st in statements:  # add reference to the course
            counter += 1
            # XXX = st.pretty_hierarchy(outline)
            # if not isinstance(st, Statement):
            #    log.warning(f"Dubious statement n°{counter}: {st}")
            if isinstance(st, Exercise):
                counter_exercises += 1
            st.course = course  # this makes printing raw exercises slow
        log.info(f"{len(statements)} statements, including"
                 f" {counter_exercises} exercises found by parser")
        counter_lemma_exercises = file_content.count("lemma exercise.")
        if counter_exercises < counter_lemma_exercises:
            log.warning(f"{counter_lemma_exercises - counter_exercises}"
                        f" exercises have not been parsed, wrong format?")
        if begin_counter < len(statements):
            log.warning(f"Found only {begin_counter} 'begin' for "
                        f"{len(statements)} statements")
        return course


def whole(namespace_list: List[str]):
    whole_namespace = ".".join(namespace_list)
    return whole_namespace


if __name__ == "__main__":
    logger.configure()
    course_file_path1 = Path(
        '../../../../tests/lean_files/short_course/exercises.lean')

    course_file_path2 = Path("../../../../tests/lean_files/courses/\
exercises_theorie_des_ensembles.lean")

    course_file_path3 = Path("../../tests/lean_files/courses/\
exercises_theorie_des_ensembles.lean")

    my_course = Course.from_file(course_file_path3)
    print("My course:")
    print("List of statements:")
    count_ex = 0
    for statement in my_course.statements:
        if isinstance(statement, Exercise):
            count_ex += 1
            print(f"Exercise n°{count_ex}: {statement.pretty_name}")
        elif isinstance(statement, Definition):
            print(f"Definition {statement.pretty_name}")
        elif isinstance(statement, Theorem):
            print(f"Theorem {statement.pretty_name}")
        #for key in statement.__dict__.keys():
        #    print(f"    {key}: {statement.__dict__[key]}")
    print('Sections:')
    for key in my_course.outline.keys():
        print(f"    {key}: {my_course.outline[key]}")
    #print("Statements list :")
    #for item in my_course.statements:
    #    print(item.lean_name)
    # print("Exercises list with statements :")
    # for item in my_course.statements:
    #     if isinstance(item, Exercise):
    #         print(item.lean_name)
    #         for st in item.available_statements:
    #             print("    " + st.lean_name)
