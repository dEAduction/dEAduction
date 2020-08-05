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
"""

from dataclasses import dataclass
from collections import OrderedDict
from typing import List, Dict, Any
import logging

import deaduction.pylib.logger as logger
from deaduction.pylib.actions.actiondef import Action
import deaduction.pylib.actions.logic
import deaduction.pylib.actions.proofs
import deaduction.pylib.actions.magic


@dataclass
class Statement:
    description: str     # "L'union est distributive par rapport à
                         # l'intersection"
    lean_line : int      # line number of the lemma declaration in Lean file
    lean_name: str       # 'set_theory.unions_and_intersections.exercise
                         # .union_distributive_inter'
    lean_statement: str  # 'A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)'
    lean_variables: str  # '(X : Type) (A : set X)'
    pretty_name: str     # 'Union d'intersections'
    text_book_identifier: str

    @classmethod
    def from_parser_data(cls, data: dict):
        """
        Create a Statement from the raw data obtained by the parser

        :param data: a dictionary whose keys =
        fields parsed by the from_directory function
        """
        log = logging.getLogger("Course initialisation")
        data.setdefault("text_book_identifier", "NOT IMPLEMENTED")
        data.setdefault("lean_variables", "NOT IMPLEMENTED")
        data.setdefault("Description", "NOT PROVIDED")
        return cls(data["Description"], data["lean_line"], data["lean_name"],
                   data["lean_statement"], data["lean_variables"],
                   data["PrettyName"], data["text_book_identifier"])


    def pretty_hierarchy(self, outline):
        """
        Return the ordered (chapter > section > …) list of sections pretty
        names corresponding to where self is in the lean file. If the
        self.lean_name is 'rings_and_ideals.first_definitions.the_statement',
        return ['Rings and ideals', 'First definitions']. Most of the time
        outline will be present_course.outline, where present_course is the
        instance of Course which initiated self.

        :param outline: A dictionnary in which keys are hierarchy levels (e.g. 
                'rings_and_ideals') and values are their pretty names
                (e.g. 'Rings and ideals').
        :return: The list of sections pretty names.
        """

        pretty_hierarchy = []

        def fkt(rmg_hierarchy):
            if not rmg_hierarchy:
                return
            else:
                pretty_hierarchy.insert(0, outline[rmg_hierarchy])
                # 'a.b.c.d' -> 'a.b.c'
                rmg_hierarchy = '.'.join(rmg_hierarchy.split('.')[:-1])
                fkt(rmg_hierarchy)

        name = '.'.join(self.lean_name.split('.')[:-1])
        fkt(name)

        return pretty_hierarchy



@dataclass
class Definition(Statement):
    pass


@dataclass
class Theorem(Statement):
    pass


@dataclass
class Exercise(Theorem):
    available_logic: List[Action]
    available_magic: List[Action]
    available_proof_techniques: List[Action]
    available_statements: List[Statement]
    expected_vars_number: Dict[str, int]  # {'X': 3, 'A': 1, 'B': 1}
    lean_begin_line_number: int           # proof starts here...
    lean_end_line_number: int             # ...and ends here

    course: Any = None                    # the parent course


    @classmethod
    def from_parser_data(cls, data: dict, statements: list):
        """
        Create an Exercise from the raw data obtained by the parser

        :param statements: list of all Statement instances until the current
        exercise
        :param data: a dictionary whose keys =
        fields parsed by the from_directory function
        TODO: change definitions into Definitions object
        """
        log = logging.getLogger("Course initialisation")

        ########################
        # expected_vars_number #
        ########################
        expected_vars_number = {}
        if "ExpectedVarsNumber" in data.keys():
            try:
                for equality in data["ExpectedVarsNumber"].split(", "):
                    key, _, value = equality.partition("=")
                    expected_vars_number[key] = int(value)
            except AttributeError:
                log.error(f"wrong format for ExpectedVarsNumber in exercise "
                          f"{data['lean_name']}")
            except ValueError:
                log.error(f"wrong format for ExpectedVarsNumber in exercise "
                          f"{data['lean_name']}")

        ###########################
        # treatment of statements #
        ###########################
        annotated_statements = [(item, False) for item in statements]
        # annotated_statements and statements must always have the same length
        # the list of available statements will be those item for which
        # (item, True) is in annotated_statements
        prefix = {"Tools->Definitions": "definition", "Tools->Theorems":
            "theorem", "Tools->Exercises": "exercise",
                   'Tools->Statements': ""}
        class_dict = {"Tools->Definitions": Definition, "Tools->Theorems":
            Theorem, "Tools->Exercises": Exercise,
                      'Tools->Statements': Statement}
        for field in ["Tools->Definitions", "Tools->Theorems",
                      "Tools->Exercises", "Tools->Statements"]:
            if data[field] is None:
                data[field] = "$UNTIL_NOW"  # default value
            log.debug(f"processing data in {field}, {data[field]}")
            class_ = class_dict[field]
            list_1 = data[field].split()
            list_2 = []
            # first step, replace macros, get a list of strings
            # predefined macros:
            # $UNTIL_NOW
            # todo: implement $AS_PREVIOUSLY
            for item in list_1:
                item = item.strip()
                if item in ["ALL", "$ALL"]:
                    log.warning("$ALL macro not implemented, try '$UNTIL_NOW'")
                    continue
                elif item in ["UNTIL_NOW", "$UNTIL_NOW"]:
                    list_2.append(item)
                    continue
                elif item.startswith("$"):
                    macro_list = data[item].split(", ")
                    list_2.extend(macro_list)
                    continue
                elif item.endswith(","):
                    item = item[:-1]
                if item.startswith("+"):
                    item = item[1:]
                list_2.append(item)
            # second step, annotate statements
            for item in list_2:
                item = item.strip()  # remove spaces
                if item in ["UNTIL_NOW", "$UNTIL_NOW"]:
                    # turn all instances of the good class to True
                    for i in range(len(statements)):
                        item = statements[i]
                        if isinstance(item, class_):
                            new_item = (item, True)
                            annotated_statements[i] = new_item
                elif item.startswith("-"):
                    # find item in statements and change annotation to False
                    item = prefix[field] + "." + item[1:]
                    index, nb = findsuffix(item,
                                           [item.lean_name for item in
                                            statements])
                    if nb > 0:
                        new_item = (statements[index], False)
                        annotated_statements[index] = new_item
                    else:
                        log.warning(
                            f"Cannot remove item {item} from statements")
                else:
                    # find item in statement and change annotation to True
                    item = prefix[field] + "." + item
                    index, nb = findsuffix(item, [item.lean_name for item in
                                                  statements])
                    if nb > 0:
                        new_item = (statements[index], True)
                        annotated_statements[index] = new_item
                        if nb > 1:
                            log.warning(f"Found >1 item {item} in statements")
                    else:
                        log.warning(f"Cannot find item {item} in statements")
        # last step, extract the good list
        available_statements = [item for (item, bool) in annotated_statements
                                if bool]
        ##############################
        # treatment of logic buttons #
        ##############################
        post_data = {}
        labels = {"Tools->Logic": "logic", "Tools->ProofTechniques": "proofs",
                 "Tools->Magic": "magic"}
        dicts = {"Tools->Logic": deaduction.pylib.actions.logic.__actions__,
                 "Tools->ProofTechniques":
                     deaduction.pylib.actions.proofs.__actions__,
                 "Tools->Magic": deaduction.pylib.actions.magic.__actions__}
        for field in labels.keys():
            log.debug(f"processing data in {field}, {data[field]}")
            if data[field] == None:
                data[field] = "$ALL"
            action_dict = dicts[field]
            action_names = [item for (_1, _2, item) in
                            [t.partition("action_") for t in
                             action_dict.keys()]]
            # action_names = list of labels for buttons,
            # action_dict = keys = labels, values = action functions
            log.debug(f"found {labels[field]} names {action_names}")
            list_1 = data[field].split()
            list_2 = []
            # first step, replace macros
            # prefefined macros:
            # $ALL
            for item in list_1:
                item = item.strip()
                if item in ["ALL", "$ALL"]:
                    list_2 = action_names + list_2
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
            #################################
            # second step, remove the minus #
            log.debug(f"list 2: {list_2}")
            list_3 = []
            for item in list_2:
                item = item.strip()
                if item.startswith("-"):
                    item = item[1:]
                    if item in list_3:
                        list_3.remove(item)
                    else:
                        log.warning(f"Cannot remove item {item} from list")
                    continue
                list_3.append(item)
            log.debug(f"list 3: {list_3}")
            #################################
            # end: get logic Actions
            post_data[field] = []
            for item in list_3:
                if item not in action_names:
                    log.warning(f"label {item} not in {labels[field]}  lists")
                else:
                    post_data[field].append(action_dict["action_" + item])


        return cls(data["Description"],
                   data["lean_line"],
                   data["lean_name"],
                   data["lean_statement"],
                   data["lean_variables"], data["PrettyName"],
                   data["text_book_identifier"],
                   post_data["Tools->Logic"],
                   post_data["Tools->Magic"],
                   post_data["Tools->ProofTechniques"],
                   available_statements,
                   expected_vars_number,
                   lean_begin_line_number=0,  # will be set up soon
                   lean_end_line_number=0,
                   )

    def current_name_space(self):
        current_name_space, _, end = self.lean_name.partition(".exercise.")
        return current_name_space

    def all_statements_until(self, statements: List[str]) -> List[str]:
        """
        provide the list of all statements in outline until the namespace
        containing self
        :param outline: outline of the course, as described in the Course class
        TODO: turn this into a @property to be accessed by
        exercise.all_statements_until
        """
        name = self.lean_name
        index = statements.index(name)
        return statements[:index]


def findsuffix(string, list):
    """
    return the number of items in a list of strings that ends with the given,
    and the index of the first matching item
    :param string:
    :param list:
    :return:
    """
    total = [item for item in list if item.endswith(string)]
    nb = len(total)
    index = -1
    if nb > 0:
        index = list.index(total[0])
    return index, nb


if __name__ == "__main__":
    print(deaduction.pylib.actions.logic.__actions__.keys())
    print(deaduction.pylib.actions.proofs.__actions__.keys())
    print(deaduction.pylib.actions.magic.__actions__.keys())
