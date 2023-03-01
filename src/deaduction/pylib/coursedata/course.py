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
import os
import logging
from sys import version_info
# if version_info[1] < 8:
#     import pickle5 as pickle
# else:
#     import pickle

import deaduction.pylib.config.dirs as      cdirs
import deaduction.pylib.logger as           logger
from deaduction.pylib.utils import (        load_object, save_object)

from deaduction.pylib.mathobj import MathObject
from deaduction.pylib.coursedata import (   Exercise,
                                            Definition,
                                            Theorem,
                                            Statement)

import deaduction.pylib.coursedata.parser_course as parser_course
from .course_metadata_translations import metadata_nice_text

log = logging.getLogger(__name__)
global _


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
    related to a Lean statement. This includes the exercises.
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

    @property
    def course_file_name(self):
        if self.relative_course_path:
            name = self.relative_course_path.stem
            return name

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
        # else:
            # return _("no subtitle")

    @property
    def description(self) -> str:
        """
        Return description if exists in metadata,
        else return "no description"
        """
        if 'description' in self.metadata:
            return self.metadata['description']
        else:
            return _("no description")

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

    @property
    def initial_proofs_complete(self):
        return None not in [st.initial_proof_state for st in self.statements]

    @property
    def nice_metadata(self) -> dict:
        """
        Produce a "nice" metadata dict by replacing
        - keys by their translation if they appear in metadata_nice_text,
        - values by replacing '_' by space and words by their translations.
        """
        nice_dict = {}
        for key in self.metadata:
            alt_key = metadata_nice_text[key] if key in metadata_nice_text \
                                              else key
            value = self.metadata[key]
            if value in metadata_nice_text:
                alt_value = metadata_nice_text[value]
            else:
                words = value.strip().split(' ')
                alt_words = []
                except_ = False
                for word in words:
                    if word.startswith("-"):
                        word = word[1:]
                        except_ = True
                    word = metadata_nice_text[word] if word in metadata_nice_text \
                        else word
                    alt_words.append(word)
                if except_:
                    alt_words.insert(1, _('except'))
                alt_value = ' '.join(alt_words)
            nice_dict[alt_key] = alt_value

        return nice_dict

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
            file_content = course_path.read_text(encoding='utf-8')
            course = Course.from_file_content(file_content)
        elif course_filetype == '.pkl':
            with course_path.open(mode='rb') as input_:
                course = load_object(input_)

        course.filetype = course_filetype
        course_path = course_path.resolve()
        relative_course_path = Path(os.path.relpath(course_path))
        course.relative_course_path = relative_course_path
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
                    # so that global option like OpenQuestion or
                    # AvailableDefinitions
                    # may be modified locally in the exercise's metadata
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

    @property
    def ips_path(self):
        return  cdirs.all_courses_ipf_dir / \
                self.relative_course_path.with_suffix('.pkl').name

    @property
    def course_hash(self):
        # Fixme: hash does not work here?!
        #  so we use the whole  file_content
        return self.file_content

    def load_initial_proof_states(self):
        """
        Search ips from a .pkl file in the self.ips_path directory,
        and assign them as attributes of the corresponding statements.

        To achieve this we Load a dictionary with
            keys    = course_hash
            values  = list of initial proof states of all course's
            statements
        This allows to check that the ips correspond to the actual Lean file
        content, and in particular to distinguish between several Lean files
        sharing the same name but distinct file content.
        """
        courses_ips_dic: dict = load_object(self.ips_path)
        if courses_ips_dic:
            ips_list = courses_ips_dic.get(self.course_hash)
        else:
            ips_list = None

        # ips_list = self.load_initial_proof_states()
        if ips_list:
            log.debug(f"Set initial proof states for "
                      f"{self.relative_course_path}")
            # NB: self.statements and ips_list
            #  should have same length
            for st, ips in zip(self.statements, ips_list):
                st.initial_proof_state = ips

    def save_initial_proof_states(self):
        """
        Save course's statements' initial proof states to a .pkl file in
        cdirs.all_courses_ipf_dir/<course_name>
        """

        courses_ips_dic: dict = load_object(self.ips_path)
        if not courses_ips_dic:
            # Create a new dict
            courses_ips_dic = dict()
        course_hash = self.course_hash
        initial_proof_states = [st.initial_proof_state
                                for st in self.statements]
        to_be_saved = False  # Save only if there is something new
        if course_hash not in courses_ips_dic:
            to_be_saved = True
        else:
            old_ips_list = courses_ips_dic[course_hash]
            for ips_old, ips_new in zip(old_ips_list, initial_proof_states):
                if ips_new and not ips_old:
                    to_be_saved = True
                    break

        if to_be_saved:
            log.debug(f"Saving initial proof states in {self.ips_path}")
            courses_ips_dic[course_hash] = initial_proof_states
            save_object(courses_ips_dic, self.ips_path)


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
