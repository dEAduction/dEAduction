"""
########################################
# course.py : provide the class Course #
########################################

    Provide the class Course,
    and an instantiation method for Course object
    by parsing a lean file.


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

from collections import                     OrderedDict
from dataclasses import                     dataclass
from pathlib import                         Path
from typing import                          List, Dict
import pickle
import os
import logging

import deaduction.pylib.logger as           logger
from deaduction.pylib.coursedata import (   Exercise,
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
    - the course metadata (e.g. authors, institution, etc.)
    - the "outline" of the course, an ordered dict describing namespaces
    - a list of all statements, Python object containing all information
    related to a Lean statement.
    """
    file_content:           str
    metadata:               Dict[str, str]
    outline:                OrderedDict
    statements:             List[Statement]
    relative_course_path:   Path = None
    # Relative_course_path is added after instantiation.

    # Outline description:
    #   keys = lean complete namespaces,
    #   values = corresponding plain language namespace
    #   e. g. section_dict["set_theory.unions_and_intersections"] =
    #   "Unions and intersections"
    # Statements is a list of all Statements, including exercises

    @property
    def title(self) -> str:
        """
        Return title if a title exists in metadata,
        else make a title from course_path
        """
        if 'title' in self.metadata:
            title = self.metadata['title']
        else:  # Make a title from the course_path
            string_title = str(self.relative_course_path.stem)
            title = string_title.replace("_", " ").title()
        return title

    @property
    def subtitle(self) -> str:
        """
        Return subtitle if a subtitle exists in metadata,
        else return "no subtitle"
        """
        if 'subtitle' in self.metadata:
            return self.metadata['subtitle']
        else:
            return "no subtitle"

    @property
    def description(self) -> str:
        """
        Return description if exists in metadata,
        else return "no description"
        """
        if 'description' in self.metadata:
            return self.metadata['description']
        else:
            return "no description"

    def print_metadata(self):
        for field_name, field_content in self.metadata.items():
            print(f"{field_name}: {field_content}")

    @property
    def exercises(self) -> List[Exercise]:
        """
        Extract all the exercises from the statements list.
        """
        statements = self.statements
        exercises = [item for item in statements
                     if isinstance(item, Exercise)]
        return exercises

    @classmethod
    def from_file(cls, course_path: Path):
        """
        Instantiate a Course object from the provided file.

        :param course_path:     path for file, either a'.lean' or a '.pkl' file
        :return:                a Course instance
        """

        course_filetype = course_path.suffix

        if course_filetype == '.lean':
            log.info(f"Parsing file {str(course_path.resolve())}")
            file_content = course_path.read_text()
            course = Course.from_file_content(file_content)
            course_path = course_path.resolve()
            relative_course_path = Path(os.path.relpath(course_path))
            course.relative_course_path = relative_course_path
        elif course_filetype == '.pkl':
            with course_path.open(mode='rb') as input:
                course = pickle.load(input)

        course.filetype = course_filetype
        return course

    @classmethod
    def from_file_content(cls, file_content: str):
        """
        Instantiate a Course object by parsing file_content.
        Data fields to be parsed must start with "/- dEAduction"
        and end with "-/": see the course rules in parser_course and the
        comments in the same file for more details.

        The file content is first transformed by the parser into a the
        "course_history", a list of events. Each event is a tuple (name,
        data) where data is a dictionary. The course history is some sort of
        idealized version of the file, retaining only the dEAduction
        pertinent information. Specifically, it is a list that contains the
        following type of events:

    - opening and closing of namespaces,
    - statements (definitions, theorems, exercises) and their metadata
    - beginning and ends of proofs,
    - end_of_line (indispensable to determine positions of proofs in the file).

    Specific examples of  events:

    - ('open_namespace', {'name': 'generalites', 'pretty_name': 'Généralités'})
    - ('close_namespace', {'name': 'generalites'})
    - ('definition', {'lean_name': 'definition.inclusion',
                      'lean_variables': '{A B : set X}',
                      'lean_core_statement': 'A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B',
                      'pretty_name': 'Inclusion'})
    - ('exercise', {'pretty_name': 'Union avec une intersection',
                    'description': "L'union est distributive par rapport à
                        l'intersection",
                    'available_definitions': '$UNTIL_NOW
                                        -union_quelconque_ensembles
                                        -intersection_quelconque_ensembles',
                    'lean_name': 'exercise.inter_distributive_union',
                    'lean_variables': '',
                    'lean_core_statement': 'A ∪ (B ∩ C)  = (A ∪ B) ∩ (A ∪ C)'})
    - ('begin_proof', None)
    - ('end_proof', None)
    - ('end_of_line', None)  (most events are of this type!)

        :param file_content:    str, to be parsed
        :return:                a Course instance.
        """

        statements = []
        outline = {}
        begin_counter = 0
        begin_found = True
        ########################
        # Parsimonious's magic #
        ########################
        # Transform the file content into a list of events
        # and a dict of metadata.
        course_tree = parser_course.lean_course_grammar.parse(file_content)
        visitor = parser_course.LeanCourseVisitor()
        course_history, course_metadata = visitor.visit(course_tree)
        # log.debug(f"course history: {course_history}")
        log.info(f"Course metadata: {course_metadata}")

        ##########################
        # Parsing course_history #
        ##########################
        line_counter = 1
        namespace = []
        for event_name, event_content in course_history:
            if event_name == "end_of_line":
                line_counter += 1
                # log.debug(f"Parsing line {line_counter}")

            elif event_name == "open_namespace":
                namespace.append(event_content["name"])
                outline[whole(namespace)] = event_content["pretty_name"]
                # log.debug(f"namespace {whole(namespace)}")
            elif event_name == "close_namespace":
                name = event_content["name"]
                if namespace and name == namespace[-1]:
                    # log.debug(f"closing namespace {name}")
                    namespace.pop()
                else:
                    pass
                    # log.debug(f"(just closing section(?) {name})")

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
                # Change lean_name into the complete lean_name, taking
                # namespaces into account:
                if namespace:
                    metadata["lean_name"] = whole(namespace) + "." \
                                            + metadata["lean_name"]

                if event_name == "exercise":
                    # Add values from course_metadata only if NOT already in
                    # exercise metadata,
                    # so that global option like OpenQuestion may be modified
                    # locally in the exercise's metadata
                    for field_name in course_metadata:
                        metadata.setdefault(field_name,
                                            course_metadata[field_name])
                    # Creating Exercise!
                    exercise = Exercise.from_parser_data(metadata, statements)
                    statements.append(exercise)
                elif event_name == "definition":
                    # Creating definition
                    definition = Definition.from_parser_data(**metadata)
                    statements.append(definition)
                elif event_name == "theorem":
                    # Creating Theorem
                    theorem = Theorem.from_parser_data(**metadata)
                    statements.append(theorem)

            # Add begin_proof and end_proof attributes in the least
            # created statement, since this info was available at creation time
            elif event_name == "begin_proof":
                st = statements[-1]
                st.lean_begin_line_number = line_counter
                begin_counter += 1
                begin_found = True
            elif event_name == "end_proof":
                st = statements[-1]
                st.lean_end_line_number = line_counter

            continue

        #######################
        # Creating the course #
        #######################
        course = cls(file_content=file_content,
                     metadata=course_metadata,
                     outline=outline,
                     statements=statements)

        # Add reference to course in statements, and test data for coherence
        counter_exercises = 0
        counter = 0
        for st in statements:
            counter += 1
            if isinstance(st, Exercise):
                counter_exercises += 1
            st.course = course  # This makes printing raw exercises slow
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

    def statement_from_name(self, name: str) -> Statement:
        """
        Return the first Statement whose Lean name ends with name.
        """
        # Try Lean names
        statements = [st for st in self.statements if st.has_name(name)]
        if statements:
            return statements[0]
        # Try pretty names
        statements = [st for st in self.statements if st.has_pretty_name(name)]
        if statements:
            return statements[0]


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
