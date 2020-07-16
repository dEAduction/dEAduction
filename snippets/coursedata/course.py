"""
# course.py : provide the class Course
    
    Provide the class Course,
    and an instantiation method for Course object
    by getting informations from a lean file


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

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
from collections import OrderedDict
import deaduction.pylib.logger as logger
import logging

from exercise import Exercise, Definition, Theorem


# from deaduction.pylib.actions import Action todo: uncomment

@dataclass
class Course:
    definitions: List[Definition]
    exercises: List[Exercise]
    outline: OrderedDict  # todo: typing OrderedDict
    # keys = lean complete namespaces,
    # values = corresponding plain language namespace
    # e. g. section_dict["set_theory.unions_and_intersections"] =
    # "Unions and intersections"
    theorems: List[Theorem]

    @classmethod
    def from_directory(cls, course_dir_path: Path):
        """
        instantiate a Course object by parsing every lean files
        in course_dir_path
        data fields to be parsed must start with "/- dEAduction"
        and end with "-/"

        :param course_dir_path: name of directory
        """
        # TODO: enable multiple exercises files ?
        log = logging.getLogger("Course initialisation")
        exercises = []
        definitions = []
        theorems = []
        outline = {}
        # parse every file in directory
        for file in course_dir_path.iterdir():
            file_content = file.read_text()
            lines = file_content.splitlines()
            global_parsing = ""
            # possible values = "namespace", "statement", "exercise"
            data_parsing = ""
            # possible values = "", "field name", "<field name>"
            line_counter = 0
            data = {"Section": None, "Tools->Logic": None,
                    "Tools->Definitions": None, "Tools->Theorems": None,
                    "Tools->Magic": None, "Tools->ProofTechniques": None,
                    "ExpectedVarsNumber": None, "text_book_identifier": None,
                    "current_namespaces": []}
            log.info(f"Parsing file {file}")
            for line in lines:
                line_counter += 1
                log.debug(f"Parsing line {line_counter}")
                log.debug(f"global_parsing: {global_parsing}, data_parsing: "
                          f"{data_parsing}")
                # data_parsing starts after a field_name_parsing
                # and goes on till the indentation stops
                if line.startswith("/- dEAduction"):
                    data_parsing = "field name"
                    # next line will be a field name
                    continue
                elif data_parsing not in ["", "field name"]:
                    data_parsing= data_parse(line, data, data_parsing)
                    log.debug(
                        f"data: {[(key, data[key]) for key in data.keys()]}")
                # note that previous lines may result in data_parsing="field name"
                # next line IS NOT elif
                if data_parsing == "field name":
                    data_parsing = line.strip()
                    log.info(f"get field name {data_parsing}")
                    data[data_parsing] = ""
                    continue
                elif line.endswith("-/"):
                    # end of data_parsing
                    log.info(f"Field content: {data[data_parsing]}")
                    data_parsing = ""
                    if global_parsing != "":
                        end_global_parsing(data, definitions, exercises,
                                           global_parsing, line_counter,
                                           outline, theorems)
                        global_parsing = ""
                    continue
                else:
                    # treatment of namespaces
                    global_parsing = namespace_parse(data, definitions,
                                    exercises, global_parsing, line,
                                    line_counter, outline, theorems)
                    # treatment of exercises
                    global_parsing = statement_parse(data, definitions,
                                    exercises, global_parsing, line,
                                    line_counter, outline, theorems)
        # Creating the course
        return cls(definitions, exercises, outline, theorems)


def data_parse(line, data, data_parsing):
    """
    """
    log = logging.getLogger("Course initialisation")
    ind = indent(line)
    if ind != 0 and indent(line) != 4:
        log.warning("indentation error")
    if ind != 0:  # fill the field
        if data[data_parsing] != "":
            data[data_parsing] += " "
        data[data_parsing] += line.strip()
        if data[data_parsing].endswith("-/"):
            data[data_parsing] = data[data_parsing][:-2]
    elif ind == 0 and not line.endswith("-/"):
        # end of field, search for next field
        log.info(f"Field content: {data[data_parsing]}")
        data_parsing = "field name"
    log.debug(f"data: {[(key, data[key]) for key in data.keys()]}")
    return data_parsing

def end_global_parsing(data, definitions, exercises, global_parsing,
                       line_counter, outline, theorems):
    log = logging.getLogger("Course initialisation")
    if global_parsing == "namespace":
        whole_namespace = ".".join(data["current_namespaces"])
        if whole_namespace not in outline.keys():
            if data["Section"] == None:
                # compute plain name from Lean name
                data["Section"] = \
                data["current_namespaces"][-1].replace("_", " ").capitalize()
        if data["Section"] is not None:
            outline[whole_namespace] = data["Section"]
        log.info(f"Namespace {whole_namespace},text: {data['Section']}")
        data["Section"] = None
    elif global_parsing == "statement":
        log.warning("unable to detect end of statement (':=')")
    elif global_parsing == "StatementMetadata":
        # creation of the Statement
        if data["lean_name"].startswith("exercise"):
            data["lean_line_number"] = line_counter
            log.info(f"creating exercise from data {data}")
            exercise = Exercise.from_parser_data(data)
            exercises.append(exercise)
        elif data["lean_name"].startswith("definition"):
            log.info(f"creating definition from data {data}")
            definition = Definition.from_parser_data(data)
            definitions.append(definition)
        elif data["lean_name"].startswith("theorem"):
            log.info(f"creating theorem from data {data}")
            theorem = Theorem.from_parser_data(data)
            theorems.append(theorem)


def namespace_parse(data, definitions, exercises, global_parsing, line,
                    line_counter, outline, theorems):
    # namespace_parsing starts at "namespace",
    # ends at first "-/" or "lemma exercise."
    log = logging.getLogger("Course initialisation")
    if line.startswith("namespace"):
        end_global_parsing(data, definitions, exercises,
                           global_parsing, line_counter,
                           outline, theorems)
        global_parsing = "namespace"
        namespace = line.split()[1]
        data["current_namespaces"].append(namespace)
        whole_namespace = ".".join(data["current_namespaces"])
        log.info(f"Parsing namespace {whole_namespace}")
        #outline[whole_namespace] = ""
    elif line.startswith("end") and len(line.split()) > 1:
        if line.split()[1] == data["current_namespaces"][-1]:
            # closing namespace
            data["current_namespaces"].pop()
    return global_parsing


def statement_parse(data, definitions, exercises, global_parsing, line,
                    line_counter, outline, theorems):
    # statement_parsing starts at "lemma exercise.", ends at ":="
    # then exercise_parsing starts, and it ends at "-/"
    log = logging.getLogger("Course initialisation")
    if line.startswith("lemma exercise.") \
            or line.startswith("lemma definition.") \
            or line.startswith("lemma theorem."):
        if global_parsing != "":
            end_global_parsing(data, definitions, exercises,
                               global_parsing, line_counter,
                               outline, theorems)
        global_parsing = "statement"
        words = line.split()
        data["lean_name"] = words[1]
        log.info(f"Parsing statement {data['lean_name']}")
        line = " ".join(words[2:])  # suppress the lemma declaration
        data["lean_variables"], _, line = line.rpartition(" : ")
        # todo: not very robust, to be improved
        data["lean_statement"] = ""
        data["PrettyName"] = None
        data["Description"] = None
        # By default the other fields are as for the previous exercise
    if global_parsing == "statement":
        data["lean_statement"] += line.strip()
        if line.strip().endswith(":="):
            log.info("parsing statement data")
            data["lean_statement"] = data["lean_statement"][:-2]
            global_parsing = "StatementMetadata"
    return global_parsing


def indent(line: str) -> int:
    """
    Compute the number of space at the beginning of line
    """
    i = 0
    while line[i] == " ":
        i += 1
    return i


if __name__ == "__main__":
    logger.configure()

    course_dir_path = Path(
        '/Users/leroux/Documents/PROGRAMMATION/LEAN/LEAN_TRAVAIL/dEAduction'
        '-lean/src/snippets/test')
    #    ex_file = 'exercises_test.lean'
    my_course = Course.from_directory(course_dir_path)
    print("My course:")
    print("List of exercises:")
    for exo in my_course.exercises:
        print(f"Exercice {exo.pretty_name}")
        for key in exo.__dict__.keys():
            print(f"    {key}: {exo.__dict__[key]}")
    print('Sections:')
    for key in my_course.outline.keys():
        print(f"    {key}: {my_course.outline[key]}")
