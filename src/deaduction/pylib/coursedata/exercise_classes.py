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
from typing import List, Dict, Any
import logging

import deaduction.pylib.logger as logger
from deaduction.pylib.actions.actiondef import Action
import deaduction.pylib.actions.logic
import deaduction.pylib.actions.proofs
import deaduction.pylib.actions.magic
from deaduction.pylib.coursedata.utils import (find_suffix,
                                               separate,
                                               substitute_macros,
                                               extract_list)

log = logging.getLogger(__name__)

LOGIC_BUTTONS = deaduction.pylib.actions.logic.__actions__
# e.g. key = action_and, value = corresponding instance of the class Action
PROOF_BUTTONS = deaduction.pylib.actions.proofs.__actions__
MAGIC_BUTTONS = deaduction.pylib.actions.magic.__actions__

@dataclass
class Statement:
    lean_line:              int
    # line number of the lemma declaration in Lean file
    lean_name:              str
    # 'set_theory.unions_and_intersections.exercise.union_distributive_inter'
    lean_core_statement:    str
    # 'A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)'
    lean_variables:         str
    # '(X : Type) (A : set X)'
    pretty_name:            str
    # 'Union d'intersections'
    description:            str = None
    # "L'union est distributive par rapport à l'intersection"
    text_book_identifier:   str = None
    lean_begin_line_number: int = None
    # proof starts here...
    # this value is set to None until "begin" is found
    lean_end_line_number:   int = None
    # ...and ends here

    course:                 Any = None
    # the parent course

    initial_proof_state:    Any = None
    # this is used when pre-processing

    @classmethod
    def from_parser_data(cls, **data):
        extract_data = {attribute: data.setdefault(attribute, None)
                        for attribute in cls.attributes()}
        # to keep only the relevant data
        return cls(**extract_data)

    @classmethod
    def attributes(cls):
        return cls.__annotations__.keys()

    @property
    def statement_to_text(self):
        """
        if self has attribute 'initial_proof_state', then return a string
        with a text version of initial goal. E.g.
        Let X be a set.
        Let A be a subset of X.
        Let B be a subset of X.
        Prove that X \ (A ∪ B) = (X \ A) ∩ (X \ B).
        """
        if hasattr(self, "initial_proof_state") and \
                self.initial_proof_state is not None:
            initial_goal = self.initial_proof_state.goals[0]
            text = initial_goal.goal_to_text()
        else:
            text = ""
        return text

    def pretty_hierarchy(self, outline):
        """
        Return the ordered (chapter > section > …) list of sections pretty
        names corresponding to where self is in the lean file. If the
        self.lean_name is 'rings_and_ideals.first_definitions.the_statement',
        return ['Rings and ideals', 'First definitions']. Most of the time
        outline will be present_course.outline, where present_course is the
        instance of Course which initiated self.

        :param outline: A dictionary in which keys are hierarchy levels (e.g.
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

        name = '.'.join(self.lean_name.split('.')[:-2])
        fkt(name)

        return pretty_hierarchy

    def ugly_hierarchy(self):
        """
        return the hierarchical list of lean namespaces ending with the
        namespace containing self
        """
        ugly_hierarchy = self.lean_name.split('.')[:-2]
        return ugly_hierarchy


    @property
    def caption(self) -> str:
        """
        Return a string that shows a simplified version of the statement
        (e.g. to be displayed as a tooltip)
        TODO (1): remove variables from lean_statement
        TODO (2): add properties of the context, if any, as hypotheses
        """
        if not hasattr(self, 'initial_proof_state') \
                or self.initial_proof_state is None:
            text = self.lean_core_statement
            return text
        goal = self.initial_proof_state.goals[0]
        target = goal.target
        text = target.math_type.format_as_utf8(is_math_type=True)
        return text


@dataclass
class Definition(Statement):
    pass


@dataclass
class Theorem(Statement):
    pass


@dataclass
class Exercise(Theorem):
    available_logic:            List[Action] = None
    available_magic:            List[Action] = None
    available_proof:           List[Action] = None
    available_statements:       List[Statement] = None
    expected_vars_number:       Dict[str, int] = None  # {'X': 3, 'A': 1}

    @classmethod
    def from_parser_data(cls, data: dict, statements: list):
        """
        Create an Exercise from the raw data obtained by the parser

        :param statements: list of all Statement instances until the current
        exercise
        :param data: a dictionary whose keys =
        fields parsed by the Course.from_file method
        TODO: change definitions into Definitions object
        """
        #split_macro_lists(data)

        ########################
        # expected_vars_number #
        # This is not used     #
        ########################
        expected_vars_number = {}
        if "expected_vars_number" in data.keys():
            try:
                for equality in data["expected_vars_number"].split(", "):
                    key, _, value = equality.partition("=")
                    key = key.strip()
                    expected_vars_number[key] = int(value)
            except AttributeError:
                log.error(f"wrong format for ExpectedVarsNumber in exercise "
                          f"{data['lean_name']}")
            except ValueError:
                log.error(f"wrong format for ExpectedVarsNumber in exercise "
                          f"{data['lean_name']}")
        # replace data with formatted data
        data['expected_vars_number'] = expected_vars_number

        ###########################
        # treatment of statements #
        ###########################
        unsorted_statements = []
        for statement_type in ['definition',
                               'theorem',
                               'exercise',
                               'statement']:
            field_name = 'available_' + statement_type + 's'
            if field_name not in data.keys():
                data[field_name] = '$UNTIL_NOW'

            string = substitute_macros(data[field_name], data)
            # this is still a string with macro names that should either
            # be '$ALL' or in data.keys() with values in Statements
            statement_callable = make_statement_callable(statement_type,
                                                         statements)
            # this is the function that computes Statements from names
            # we can now compute the available_actions:
            more_statements = extract_list(string, data, statement_callable)
            unsorted_statements.extend(more_statements)

        # finally sort statements:
        data['available_statements'] = []
        for item in statements:
            if item in unsorted_statements:
                data['available_statements'].append(item)

        names = [st.pretty_name for st in data['available_statements']]
        log.debug(f"statements: {names}")

        ########################
        # treatment of buttons #
        ########################
        for action_type in ['logic', 'proof', 'magic']:
            field_name = 'available_' + action_type
            default_field_name = 'default_' + field_name
            if field_name not in data.keys():
                if default_field_name in data.keys():  # take default list
                    data[field_name] = data[default_field_name]
                else:  # take all buttons
                    data[field_name] = '$ALL'  # not optimal

            log.debug(f"processing data in {field_name}, {data[field_name]}")

            string = substitute_macros(data[field_name], data)
            # this is still a string with macro names that should either
            # be '$ALL' or in data.keys() with values in Action
            action_callable = make_action_callable(action_type)
            # this is the function that computes Actions from names
            # we can now compute the available_actions:
            data[field_name] = extract_list(string, data, action_callable)

        # to keep only the relevant data, the keys that appear as attributes
        # in the class Exercise or in the parent class Statement
        # this removes the entry in 'data' corresponding to course_metadata
        extract_data = {attribute: data.setdefault(attribute, None)
                        for attribute in Statement.attributes()}
        more_data = {attribute: data.setdefault(attribute, None)
                        for attribute in cls.attributes()}
        extract_data.update(more_data)

        log.debug(f"available_logic: {extract_data['available_logic']}")
        log.debug(f"available_proof: {extract_data['available_proof']}")
        log.debug(f"available_statements: "
                  f"{len(extract_data['available_statements'])}")
        return cls(**extract_data)

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


def make_action_callable(prefix) -> callable:
    """
    Construct the function corresponding to prefix
    :param prefix: one of logic, proof, magic
    :return: a callable
    """
    if prefix == 'logic':
        dictionary = LOGIC_BUTTONS
    elif prefix == 'proof':
        dictionary = PROOF_BUTTONS
    elif prefix == 'magic':
        dictionary = MAGIC_BUTTONS

    def action_callable(name: str) -> [Action]:
        """
        Return list of actions corresponding to name, as given by the
        LOGIC_BUTTON dict
        e.g. 'and' -> [ LOGIC_BUTTONS['action_and'] ]
        '$ALL' -> LOGIC_BUTTONS
        """
        log.debug(f"searching Action {name}")
        if name in ['ALL', '$ALL']:
            return dictionary.values()

        if not name.startswith("action_"):
            name = "action_" + name
        action = None
        if name in LOGIC_BUTTONS:
            action = LOGIC_BUTTONS[name]
        return [action]

    return action_callable


def make_statement_callable(prefix, statements) -> callable:
    """
    Construct the function corresponding to prefix
    :param prefix: one of statement, definition, theorem, exercise
    :param statements: list of instances of the Statement class
    :return: a callable
    """
    classes = {'statement': Statement,
               'definition': Definition,
               'theorem': Theorem,
               'exercise': Exercise}
    class_ = classes[prefix]

    def statement_callable(name: str) -> [Statement]:
        """
        Return Statement corresponding to name and prefix

        e.g. "union_quelconque" (prefix = "definition)
        ->  Statement whose name endswith definition.union_quelconque
        """
        if name in ['$UNTIL_NOW', 'UNTIL_NOW']:
            available_statements = []
            for statement in statements:
                if isinstance(statement, class_):
                    available_statements.append(statement)
            return available_statements

        statement = None
        name = prefix + '.' + name
        index, nb = find_suffix(name,
                                [item.lean_name for item in
                                 statements])
        if nb > 0:
            statement = statements[index]
        return [statement]

    return statement_callable


if __name__ == "__main__":
    print(LOGIC_BUTTONS)
    print(PROOF_BUTTONS)