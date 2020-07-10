"""
# init_course.py : extract exercises from a lean file
    
    This files provides the two classes Course and Exercise,
    and an instantiation method for Course object by getting informations from a lean file

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
import deaduction.pylib.logger as logger
import logging

log = logging.getLogger("my logger")


@dataclass
class Exercise:
    lean_name: str
    lean_statement: str
    line_number: int
    title: str
    description: str
    logic: list
    definitions: list
    theorems: list
    magic: list
    expected_number_var: dict  # expected number of variables of each mathematical type
    # e.g expected_number_var["X"] = 2

    logic_buttons_complete_list = ["∀", "∃", "→", "↔", "ET", "OU", "NON",
                                   "Preuve par l'absurde", "Preuve par contraposée", "Preuve par cas", "Choix"]

    # magic_buttons_complete_list = TODO

    @classmethod
    def from_parser_data(cls, data: dict):
        """
        Create an Exercise from the raw data obtained by the parser

        :param data: a dictionary whose keys = fields parsed by the course_from_lean_file function
        """
        data["lean_statement"] = data["lean_statement"][:-2].strip()  # removing the final " :="
        expected_variables = {}
        for equality in data["ExpectedVariables"].split(", "):
            key, _, value = equality.partition("=")
            expected_variables[key] = int(value)
        if "Title" in data.keys():
            title = data["Title"]
        else:
            title = data["lean_statement"].replace("_", " ")  # automatic title if not provided

        # treatment of Macros and variables
        post_data = {}
        for field in ["Tools->Logic", "Tools->Definitions", "Tools->Theorems", "Tools->Magic"]:
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
        # logic check
        for item in post_data["Tools->Logic"]:
            if item not in Exercise.logic_buttons_complete_list:
                log.warning(f"unknown logic button {item}")

        return cls(data["lean_name"], data["lean_statement"], data["line_number"], title, data["Description"],
                   post_data["Tools->Logic"], post_data["Tools->Definitions"], post_data["Tools->Theorems"],
                   post_data["Tools->Magic"],
                   expected_variables)


@dataclass
class Course:
    exercises_list: list

    @classmethod
    def course_from_lean_file(cls, course_path, exercises_file):
        """
        instantiate a Course object by parsing lean files

        :param course_path: name of directory
        :param exercises_file: name of file
        """
        # TODO: enable multiple exercises files ?
        macros_dict = {}
        exercises_list = []
        sections_dict = {}  # keys = lean namespaces, values = corresponding plain language namespace
        sections_list = []  # successive whole namespaces
        exercises_path = course_path / 'exercises' / exercises_file

        file_content = exercises_path.read_text()
        lines = file_content.splitlines()
        namespace_parsing = False
        statement_parsing = False
        exercise_parsing = False
        field_name_parsing = False
        data_parsing = False
        current_field = None
        current_namespaces = []  # the whole hierarchy of namespaces
        line_counter = 0
        data = {"Section": None, "Tools->Logic": None, "Tools->Definitions": None, "Tools->Theorems": None,
                "Tools->Magic": None, "ExpectedVariables": None}
        log.info(f"Parsing file {exercises_file}")
        for line in lines:
            line_counter += 1
            log.debug(f"Parsing line {line_counter}")

            # filling data, data_parsing starts after a field_name_parsing and goes on till the indentation stops
            if line.startswith("/- dEAduction"):
                statement_parsing = False
                field_name_parsing = True  # next line will be a field name, and field_name_parsing will end
                continue
            if data_parsing:
                if line.startswith(" " * 4):
                    if line.startswith(" " * 5):
                        log.warning("indentation error")
                    else:  # good indentation
                        if data[current_field] != "":
                            data[current_field] += " "
                        data[current_field] += line.strip()
                else:  # end of parsing this field
                    if line.startswith(" "):  # more than 1 but less than 4
                        log.warning("indentation error")
                    else:
                        if data[current_field].endswith("-/"):
                            data[current_field] = data[current_field][:-2]
                        log.info(f"Field content: {data[current_field]}")
                        current_field = None
                        data_parsing = False
                        # this line is a field name, to be caught by next test, except if closing docstring
                        field_name_parsing = True

            # getting field name (keep this AFTER filling data: end of data_parsing = beginning of field_parsing)
            if field_name_parsing:
                if line.endswith("-/"):
                    field_name_parsing = False
                else:  # get new field name
                    current_field = line.strip()
                    log.info(f"get field name {current_field}")
                    data[current_field] = ""
                    field_name_parsing = False
                    data_parsing = True
                continue
            #
            # treatment of namespaces
            # namespace_parsing starts at "namespace", ends at first "-/" or "lemma exercise."
            if line.startswith("namespace"):
                namespace_parsing = True
                namespace = line.split()[1]
                current_namespaces.append(namespace)
                whole_namespace = ".".join(current_namespaces)
                log.info(f"Parsing namespace {whole_namespace}")
                sections_list.append(whole_namespace)
                continue
            if line.startswith("end") and len(line.split()) > 1:
                if line.split()[1] == current_namespaces[-1]:  # closing namespace
                    current_namespaces.pop()
                continue
            if namespace_parsing:
                if line.endswith("-/"):
                    if data["Section"] == None:  # compute plain name from Lean name
                        data["Section"] = current_namespaces[-1].replace("_", " ")
                    sections_dict[".".join(current_namespaces)] = data["Section"]
                    data["section"] = None
                    log.info(f"got namespace {'.'.join(current_namespaces)} plain text: {data['Section']}")
                    # e. g. section_dict["set_theory.unions_and_intersections"] = "Unions and Intersections"
                    namespace_parsing = False

            # treatment of exercises
            # exercise_parsing starts at "lemma exercise.", end at "Begin"
            if line.startswith("lemma exercise."):
                log.info(f"Parsing exercise n°{len(exercises_list)}")
                statement_parsing = True  # ends at first "/- dEAduction"
                namespace_parsing = False
                words = line.split()
                data["lean_name"] = words[1]
                data["lean_statement"] = " ".join(words[2:])
                exercise_parsing = True
                data["Title"] = None
                data["Description"] = None
                # By default the other fields are as for the previous exercise
                continue
            if statement_parsing:
                data["lean_statement"] += line.strip()
                continue
            if exercise_parsing:
                if line.startswith("begin"):
                    exercise_parsing = False
                    # creation of an exercise
                    data["line_number"] = line_counter
                    log.info(f"creating exercise from data {data}")
                    exercise = Exercise.from_parser_data(data)
                    exercises_list.append(exercise)

        # Creating the course
        return cls(exercises_list)


if __name__ == "__main__":
    logger.configure()

    path = Path('/Users/leroux/Documents/PROGRAMMATION/LEAN/LEAN_TRAVAIL/dEAduction-lean/src/snippets')
    ex_file = 'exercises_test.lean'
    my_course = Course.course_from_lean_file(path, ex_file)
    print("My course:")
    for exo in my_course.exercises_list:
        print(f"Exercice {exo.title}")
        for key in exo.__dict__.keys():
            print(f"    {key}: {exo.__dict__[key]}")