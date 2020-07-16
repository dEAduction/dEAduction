"""
# init_course.py: extract exercises from a lean file
    
    This files provides the two classes Course and Exercise,
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

#from deaduction.pylib.actions import Action todo: uncomment


@dataclass
class Statement:
    description:    str # "L'union est distributive par rapport à
                        # l'intersection"
    # todo en faire une property pour le cas où non rempli
    lean_name:              str  # 'exercise.inter_distributive_union'
    lean_statement:         str  # 'A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)'
    lean_variables:         str  # '(X : Type) (A : set X)'
    pretty_name:            str  # 'Union d'intersections'
    text_book_identifier:   str


@dataclass
class Definition(Statement):
    pass


@dataclass
class Theorem(Statement):
    pass


@dataclass
class Exercise(Theorem):
    available_definitions:      List[Definition]
    available_logic:            list # todo: List[Action]
    available_magic:            list #List[Action]  # []
    available_proof_techniques: list #List[Action]
    available_theorems:         List[Theorem] # to be filled only when
    # beginning the proof of the exercise
    expected_vars_number:       Dict[str, int]  # {'X': 3, 'A': 1, 'B': 1}
    lean_line_number:           int

#    logic_buttons_complete_list = ["forall", "exists", "implies", "iff",
#                                   "AND", "OR", "NOT",
#                                   "p_absurd", "p_contrapose",
#                                   "p_cases", "p_choice"]

    # magic_buttons_complete_list = TODO

    @classmethod
    def from_parser_data(cls, data: dict):
        """
        Create an Exercise from the raw data obtained by the parser

        :param data: a dictionary whose keys =
        fields parsed by the course_from_lean_file function
        """
        log = logging.getLogger("Course initialisation")
        expected_vars_number = {}
        whole_namespace = ".".join(data["current_namespaces"])
        data["lean_name"] = whole_namespace + "." + data["lean_name"]
        for equality in data["ExpectedVarsNumber"].split(", "):
            key, _, value = equality.partition("=")
            expected_vars_number[key] = int(value)
        if "PrettyName" not in data.keys():
            data["PrettyName"] = data["lean_statement"].replace("_", " ")
            # automatic pretty_name if not provided

        # treatment of Macros and variables
        post_data = {}
        for field in ["Tools->Logic", "Tools->Definitions",
                      "Tools->Theorems", "Tools->Magic"]:
            log.debug(f"processing data in {field}, {data[field]}")
            if data[field] == None:
                post_data[field] = None
                continue
            list_1 = data[field].split()
            list_2 = []
            # first step, replace macros
            for item in list_1:
                if item in ["LOGIC_COMPLETE", "$LOGIC_COMPLETE"]:
                    list_2 = Exercise.logic_buttons_complete_list + list_2
                    continue
                if item in ["ALL", "$ALL"]:
                    list_2.insert(0, "ALL")
                    continue
                if item.startswith("$"):
                    macro_list = data[item].split(", ")
                    list_2.extend(macro_list)
                    continue
                if item.endswith(","):
                    item = item[:-1]
                if item.startswith("+"):
                    item = item[1:]
                list_2.append(item)
            # second step, remove the minus
            log.debug(f"list 2: {list_2}")
            list_3 = []
            for item in list_2:
                if item.startswith("-"):
                    list_3.remove(item[1:])
                    continue
                list_3.append(item)
            log.debug(f"list 3: {list_3}")
            post_data[field] = list_3
        # todo: logic check
#        for item in post_data["Tools->Logic"]:
#            if item not in :
#                log.warning(f"unknown logic button {item}")

        return cls(data["Description"] , data["lean_name"], data["lean_statement"],
                   data["lean_variables"], data["PrettyName"],
                   post_data["Tools->Definitions"], post_data["Tools->Logic"],
                   post_data["Tools->Magic"], [], post_data["Tools->Theorems"],
                   expected_vars_number,
                   data["lean_line_number"])


@dataclass
class Course:
    exercises:  List[Exercise]
    outline:    OrderedDict  # keys = lean complete namespaces,
    # values = corresponding plain language namespace
    # e. g. section_dict["set_theory.unions_and_intersections"] =
    # "Unions and intersections"

    @classmethod
    def from_directory(cls, course_dir_path: Path):
        """
        instantiate a Course object by parsing lean files

        :param course_dir_path: name of directory
        """
        # TODO: enable multiple exercises files ?
        log = logging.getLogger("Course initialisation")
        exercises_list = []
        sections_dict = {}
        sections_list = []
        exercises_path = course_path / 'exercises' / exercises_file

        file_content = exercises_path.read_text()
        lines = file_content.splitlines()
        global_parsing = ""
        # possible values = "namespace", "statement", "exercise"
        data_parsing = ""
        # possible values = "", "field name", "<field name>"
        line_counter = 0
        data = {"Section": None, "Tools->Logic": None,
                "Tools->Definitions": None, "Tools->Theorems": None,
                "Tools->Magic": None, "ExpectedVarsNumber": None,
                "current_namespaces": []}
        log.info(f"Parsing file {exercises_file}")
        for line in lines:
            line_counter += 1
            log.debug(f"Parsing line {line_counter}")

            # filling data, data_parsing starts after a field_name_parsing
            # and goes on till the indentation stops
            if line.startswith("/- dEAduction"):
                data_parsing = "field name"  # next line will be a field name,
                continue
            if data_parsing not in ["", "field name"]:
                data_parsing, global_parsing = data_parse(line, data,
                                                          data_parsing,
                                                          global_parsing,
                                                          sections_dict)
                log.debug(f"data: {[(key, data[key]) for key in data.keys()]}")
            # note that previous lines may result in data_parsing="field name"
            # next line IS NOT elif
            if data_parsing == "field name":
                data_parsing = line.strip()
                log.info(f"get field name {data_parsing}")
                data[data_parsing] = ""
                continue
            # treatment of namespaces
            # namespace_parsing starts at "namespace",
            # ends at first "-/" or "lemma exercise."
            if line.startswith("namespace"):
                global_parsing = "namespace"
                namespace = line.split()[1]
                data["current_namespaces"].append(namespace)
                whole_namespace = ".".join(data["current_namespaces"])
                log.info(f"Parsing namespace {whole_namespace}")
                sections_list.append(whole_namespace)
                continue
            elif line.startswith("end") and len(line.split()) > 1:
                if line.split()[1] == data["current_namespaces"][-1]:
                    # closing namespace
                    data["current_namespaces"].pop()
                continue

            # treatment of exercises
            # statement_parsing starts at "lemma exercise.", ends at ":="
            # then exercise_parsing starts, and it ends at "begin"
            if line.startswith("lemma exercise."):
                log.info(f"Parsing exercise n°{len(exercises_list)}")
                global_parsing = "statement"
                words = line.split()
                data["lean_name"] = words[1]
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
                    log.info("parsing exercise data")
                    data["lean_statement"] = data["lean_statement"][:-2]
                    global_parsing = "exercise"
            elif global_parsing == "exercise" and line.startswith("begin"):
                global_parsing = ""
                # creation of an exercise
                data["lean_line_number"] = line_counter
                log.info(f"creating exercise from data {data}")
                exercise = Exercise.from_parser_data(data)
                exercises_list.append(exercise)

        # Creating the course
        return cls(exercises_list, sections_dict, sections_list)


def data_parse(line, data, data_parsing, global_parsing, sections_dict):
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
    if line.endswith("-/"):  # end of data_parsing
        log.info(f"Field content: {data[data_parsing]}")
        data_parsing = ""
        if global_parsing == "namespace":
            if data["Section"] == None:  # compute plain name from Lean name
                data["Section"] = \
                    data["current_namespaces"][-1].replace("_", " ")
            whole_namespace = ".".join(data["current_namespaces"])
            sections_dict[whole_namespace] = data["Section"]
            log.info(f"Namespace {whole_namespace},text: {data['Section']}")
            data["Section"] = None
    elif ind == 0:  # end of field, search for next field
        log.info(f"Field content: {data[data_parsing]}")
        data_parsing = "field name"
    log.debug(f"data: {[(key, data[key]) for key in data.keys()]}")
    return data_parsing, global_parsing


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

    path = Path(
        '/Users/leroux/Documents/PROGRAMMATION/LEAN/LEAN_TRAVAIL/dEAduction-lean/src/snippets')
    ex_file = 'exercises_test.lean'
    my_course = Course.from_lean_file(path, ex_file)
    print("My course:")
    print("List of exercises:")
    for exo in my_course.exercises_list:
        print(f"Exercice {exo.pretty_name}")
        for key in exo.__dict__.keys():
            print(f"    {key}: {exo.__dict__[key]}")
    print('Sections:')
    for key in my_course.sections_dict.keys():
        print(f"    {key}: {my_course.sections_dict[key]}")
