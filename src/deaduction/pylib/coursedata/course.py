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

from deaduction.pylib.utils.filesystem import check_dir
import deaduction.pylib.config.dirs as      cdirs
# import deaduction.pylib.config.vars as      cvars
import deaduction.pylib.logger as           logger
from deaduction.pylib.utils import (        load_object, save_object)

# from deaduction.pylib.mathobj import MathObject
# from deaduction.pylib.coursedata.settings_parser import vars_from_metadata
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
    The attributes are:
    - the content of the corresponding Lean file,
    - the course metadata (e.g. authors, institution, etc.)
    - the "outline" of the course, an ordered dict describing namespaces
    - a list of all statements, Python object containing all information
    related to a Lean statement. This includes the exercises.
    """
    file_content:           str
    metadata:               Dict[str, str]
    outline:                OrderedDict
    opened_namespace_lines: Dict
    statements:             List[Statement]
    # relative_course_path:   Path = None
    abs_course_path:   Path = None
    # Relative_course_path, path relative to the home directory, is added after
    # instantiation.

    __history_course      = None

    # Outline description:
    #   keys = lean complete namespaces,
    #   values = corresponding plain language namespace
    #   e. g. section_dict["set_theory.unions_and_intersections"] =
    #   "Unions and intersections"

    @property
    def relative_course_path(self):
        return cdirs.relative_to_home(self.abs_course_path)

    @property
    def course_file_name(self):
        if self.relative_course_path:
            name = self.relative_course_path.stem
            return name

    def lean_import_course_preamble(self) -> str:
        return f"import {self.course_file_name}\n"

    @property
    def history_file_path(self):
        """
        Return path to history file for this exercise, relative to home.
        """

        rel_path = cdirs.relative_to_home(self.abs_history_file_path)
        # print(f"History path:{rel_path}")
        return rel_path

    @property
    def abs_history_file_path(self):
        filename = 'history_' \
                   + self.course_file_name.replace('.', '_') \
                   + '.lean'

        check_dir(cdirs.history, create=True)
        abs_path = cdirs.history / filename
        # print(f"Abs history path:{abs_path}")
        return abs_path

    def history_course(self):
        """
        Return Course instance created from history version of course,
        if a history versions exists.
        """

        if not self.__history_course:
            self.set_history_course()
        return self.__history_course

    def set_history_course(self):
        abs_path = self.abs_history_file_path
        self.__history_course = (Course.from_file(abs_path)
                                 if abs_path.exists() else None)

    def original_version_in_history_file(self, exercise: Exercise) -> Exercise:
        """
        Return Exercise identical to exercise but in history file.
        """

        history_course = self.history_course()
        if history_course:
            for other in history_course.exercises:
                if other.is_copy_of(exercise):
                    return other

            log.warning(f"No copy of original exercise {exercise.pretty_name}"
                        f"found in history file")

    def saved_exercises_in_history_course(self, max_nb=100) -> list[Exercise]:
        """
        Provide list of exercises saved in history course. For each exercise,
        only the max last versions are provided.
        """

        history_course = self.history_course()
        if not history_course:
            return []

        # exercises = [exo for exo in history_course.exercises
        #              if exo.history_date() and exo.refined_auto_steps]
        # # debug
        # for exo in hstr_course.exercises:
        #     if exo.history_date():
        #         continue

        # last_exercises = [ex for ex in exercises
        #                   if ex.history_number() >
        #                   ex.nb_versions_saved_in_history_course() - max_nb]

        last_exercises = []
        for exo in self.exercises:
            for history_exo in self.history_versions_from_exercise(exo):
                if (history_exo.history_number() >
                        exo.nb_versions_saved_in_history_course() - max_nb):
                    last_exercises.append(history_exo)

        return last_exercises

    def history_versions_from_exercise(self, exercise: Exercise):
        """
        Return the versions of exercise as saved in self.history_course().
        Beware that this may NOT make use of
        the saved_exercises_in_history_course() method.
        """
        history_course = self.history_course()
        if not history_course:
            return []

        # saved_exercises = self.saved_exercises_in_history_course()
        saved_exercises = [exo for exo in history_course.exercises
                           if exo.history_date() and exo.refined_auto_steps]
        exercises = [history_exo for history_exo in saved_exercises
                     if history_exo.is_history_version_of(exercise)]
        return exercises

    def delete_all_saved_proofs_of_exercise(self, exercise: Exercise):
        """
        This method will delete all history versions of the given exercise in
        the history file. Do not call without warning usr.
        """
        saved_versions = self.history_versions_from_exercise(exercise)
        while saved_versions:
            nb = len(saved_versions)
            saved_version = saved_versions[-1]
            assert isinstance(saved_version, Exercise)
            saved_version.delete_in_history_file()
            # Reset history course, since the line number of the remaining
            # exercises may have changed
            self.set_history_course()
            saved_versions = self.history_versions_from_exercise(exercise)
            if len(saved_versions) != nb - 1:
                log.warning("Deleting failed!")
                break

    def delete_history_file(self):
        """
        This method delete the history file. Do not call without warning usr!
        """
        file = self.abs_history_file_path
        try:
            file.unlink()
        except FileNotFoundError:
            log.warning("History file not found")

    def is_history_file(self):
        return self.course_file_name.startswith('history_')

    def exercises_including_saved_version(self, max_nb=100):
        """
        Return a list containing self's exercises and all saved versions
        (or at least as many as max_nb per exercise).
        """
        original_exercises = self.exercises
        saved_exercises = self.saved_exercises_in_history_course(max_nb=max_nb)
        log.debug(f"Found {len(saved_exercises)} saved exercises")
        if not saved_exercises:
            return self.exercises

        mixed_exercises = []
        saved_index = 0

        for exercise in original_exercises:
            mixed_exercises.append(exercise)
            while saved_index < len(saved_exercises) \
                    and saved_exercises[saved_index].\
                    is_history_version_of(exercise):
                saved_exercise = saved_exercises[saved_index]
                mixed_exercises.append(saved_exercise)
                saved_exercise.original_exercise = exercise
                saved_index += 1

        missing = (len(original_exercises) + len(saved_exercises)
                   - len(mixed_exercises))
        if missing > 0:
            log.warning(f"Missed {missing} saved exercises")

        return mixed_exercises

    # ----- Some metadata ----- #
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

    def restricted_calculator_definitions(self) -> []:
        """
        Return None if does not appear in metadata.
        """
        restricted_defs = self.metadata.get('restricted_calculator_definitions')
        if restricted_defs:
            if isinstance(restricted_defs, str):
                restricted_defs = restricted_defs.split()
        return restricted_defs

    def more_calculator_definitions(self) -> []:
        """
        Return None if does not appear in metadata.
        """
        defs = self.metadata.get('more_calculator_definitions')
        if defs:
            if isinstance(defs, str):
                defs = defs.split()
        return defs

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

    def all_exercises_text(self, text_format='utf8'):
        """
        Return the detailed statements of all exercises.
        """

        txt = ""
        ex_counter = 0
        for exercise in self.exercises:
            ex_counter += 1
            txt += _(f"Exercise {ex_counter}: ") + exercise.pretty_name
            txt += '\n'
            txt += exercise.statement_to_text(text_format)
            txt += '\n\n'
        return txt

    @property
    def abs_text_file_path(self):
        filename = 'all_statements_' \
                   + self.course_file_name.replace('.', '_') \
                   + '.txt'

        check_dir(cdirs.text_files, create=True)
        abs_path = cdirs.text_files / filename
        # print(f"Abs history path:{abs_path}")
        return abs_path

    def save_all_exercises_text(self, text_format='utf8'):
        """
        Save the text of all exercises in a file, if the file does not
        already exist.
        """

        path = self.abs_text_file_path
        content = self.all_exercises_text(text_format)
        # 'x' = fails if file already exists
        try:
            with open(path, mode='wt', encoding='utf-8') as output:
                log.info("Saving all statements to file" + " " + str(path))
                output.write(content)
        except FileExistsError:  # Should not happen, mode = 'w'
            log.debug("(File already exists:" + " " + str(path) + ")")

    @property
    def incomplete_statements(self):
        return [st for st in self.statements if not st.initial_proof_state]

    @property
    def initial_proofs_complete(self):
        return not self.incomplete_statements

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
            if isinstance(value, str):
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

    # def update_cvars_from_metadata(self):
    #     metadata_settings = self.metadata.get('settings')
    #     if metadata_settings:
    #         more_vars = vars_from_metadata(metadata_settings)
    #         if more_vars:
    #             cvars.update(more_vars)

    @classmethod
    def from_file(cls, abs_course_path: Path):
        """
        Instantiate a Course object from the provided file.

        :param abs_course_path: path fora Lean file. WARNING: this should be
        an absolute path.

        :return:                a Course instance
        """

        # course_filetype = course_path.suffix
        # if not course_path.exists():
        #     course_path = cdirs.home / course_path
        # if course_filetype == '.lean':
        log.info(f"Parsing file {str(abs_course_path)}")
        file_content = abs_course_path.read_text(encoding='utf-8')
        course = Course.from_file_content(file_content)
        if not course:
            return
        # elif course_filetype == '.pkl':  # Obsolete
        #     with course_path.open(mode='rb') as input_:
        #         course = load_object(input_)
        # else:
        #     return

        # course.filetype = course_filetype
        # course_path = course_path.resolve()
        # home = cdirs.home.resolve()
        # relative_course_path = Path(os.path.relpath(course_path,
        #                                             start=home))
        # course.relative_course_path = cdirs.relative_to_home(abs_course_path)
        course.abs_course_path = abs_course_path

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

        # Avoid a bug in the parser: line comments are supposed to end with a
        # CR ('\n')
        if not file_content.endswith("\n"):
            file_content += "\n"

        statements = []
        outline = OrderedDict()
        opened_namespace_lines = {}
        begin_counter = 0
        # Will be False between statement event and begin_proof event:
        begin_found = True

        ########################
        # Parsimonious's magic #
        ########################
        # Transform the file content into a list of events
        # and a dict of metadata.

        # FIXME: handle parsimonius exception if this is not a Deaduction file
        course_tree = parser_course.lean_course_grammar.parse(file_content)
        visitor = parser_course.LeanCourseVisitor()
        course_history, course_metadata = visitor.visit(course_tree)
        # Meaningless here (and --> crash since dict is not hashable!)
        if '_raw_metadata' in course_metadata:
            course_metadata.pop('_raw_metadata')
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

            elif event_name == "open_open":
                name = event_content['name']
                if name not in opened_namespace_lines:
                    opened_namespace_lines[name] = line_counter

            # elif event_name == "begin_metadata":
            #     # Exercise metadata are before begin_proof event
            #     if not begin_found and statements:
            #         info = statements[-1].info
            #         info['begin_metadata_line'] = line_counter

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
                        if field_name not in \
                                Exercise.non_pertinent_course_metadata:
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
                     opened_namespace_lines=opened_namespace_lines,
                     statements=statements)

        # Add reference to course in statements, and test data for coherence
        counter_exercises = 0
        counter = 0
        for st in statements:
            counter += 1
            if isinstance(st, Exercise):
                counter_exercises += 1
            st.course = course  # This makes __repr__() very slow
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
