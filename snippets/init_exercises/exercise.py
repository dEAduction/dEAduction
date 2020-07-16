"""
# exercise.py : provide the class Exercise
    
    Provides the classes Statement, Definition, Theorem, Exercise

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

    todo: change statements from string to Action instances
"""

from dataclasses import dataclass
from typing import List, Dict
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

    @classmethod
    def from_parser_data(cls, data: dict):
        """
        Create a Statement from the raw data obtained by the parser

        :param data: a dictionary whose keys =
        fields parsed by the from_directory function
        """
        log = logging.getLogger("Course initialisation")
        whole_namespace = ".".join(data["current_namespaces"])
        data["lean_name"] = whole_namespace + "." + data["lean_name"]
        if "PrettyName" not in data.keys():
            data["PrettyName"] = data["lean_statement"].replace("_", " ")
            # automatic pretty_name if not provided
        return cls(data["Description"] , data["lean_name"], data["lean_statement"],
                   data["lean_variables"], data["PrettyName"],
                   data["text_book_identifier"])

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
        fields parsed by the from_directory function
        TODO: change definitions into Definitions object
        """
        log = logging.getLogger("Course initialisation")
        whole_namespace = ".".join(data["current_namespaces"])
        data["lean_name"] = whole_namespace + "." + data["lean_name"]
        if "PrettyName" not in data.keys():
            data["PrettyName"] = data["lean_statement"].replace("_", " ")
            # automatic pretty_name if not provided
        expected_vars_number = {}
        for equality in data["ExpectedVarsNumber"].split(", "):
            key, _, value = equality.partition("=")
            expected_vars_number[key] = int(value)
        # treatment of Macros and variables
        post_data = {}
        for field in ["Tools->Logic", "Tools->Definitions",
            "Tools->ProofTechniques", "Tools->Theorems", "Tools->Magic"]:
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
                    item = item [1:]
                    if item in list_3:
                        list_3.remove(item)
                    else:
                        log.warning(f"Cannot remove item {item} from list")
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
                   data["text_book_identifier"],
                   post_data["Tools->Definitions"], post_data["Tools->Logic"],
                   post_data["Tools->Magic"],
                   post_data["Tools->ProofTechniques"],
                   post_data["Tools->Theorems"],
                   expected_vars_number,
                   data["lean_line_number"])

if __name__ == "__main__":
    pass