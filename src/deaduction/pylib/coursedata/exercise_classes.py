"""
##############################################################################
# exercise.py : provide the classes Statement, Exercise, Definition, Theorem #
##############################################################################

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
from typing import List, Dict, Any, Optional
import logging

# from deaduction.pylib.config.i18n import _
import deaduction.pylib.logger as logger
from deaduction.pylib.actions.actiondef import Action
import deaduction.pylib.actions.logic
import deaduction.pylib.actions.proofs
import deaduction.pylib.actions.magic
from deaduction.pylib.coursedata.utils import (find_suffix,
                                               substitute_macros,
                                               extract_list)
from deaduction.pylib.coursedata.auto_steps import AutoStep

log = logging.getLogger(__name__)

##############################################
# Lists of all instances of the Action class #
##############################################
LOGIC_BUTTONS = deaduction.pylib.actions.logic.__actions__
# e.g. key = action_and, value = corresponding instance of the class Action
PROOF_BUTTONS = deaduction.pylib.actions.proofs.__actions__
MAGIC_BUTTONS = deaduction.pylib.actions.magic.__actions__


@dataclass
class Statement:
    """
    A class for storing information about Lean's statements.
    This is the parent class for classes Exercise, Definition, Theorem.
    """
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
    description:            str             = None
    # "L'union est distributive par rapport à l'intersection"
    text_book_identifier:   str             = None
    lean_begin_line_number: int             = None
    # proof starts here...
    # this value is set to None until "begin" is found
    lean_end_line_number:   int             = None
    # ...and ends here

    course:                 Any             = None
    # the parent course

    initial_proof_state:    Any             = None
    # this is used when pre-processing

    auto_steps: str                         = ''
    auto_test: str                          = ''
    __refined_auto_steps: Optional[AutoStep]= None

    info:                   Dict[str, Any]  = None
    # Any other (non-essential) information

    @classmethod
    def from_parser_data(cls, **data):
        """
        Create a Statement instance from data.

        :param data:    dictionary containing the relevant information:
                        keys in data will be transformed into attributes.
        """
        attributes = cls.attributes()
        extract_data = {}
        for attribute in attributes:
            if attribute in data.keys():
                extract_data[attribute] = data.pop(attribute)
        # extract_data = {attribute: data.setdefault(attribute, None)
        #                for attribute in attributes}
        # keep only the relevant data, i.e. the keys which corresponds to
        # attribute of the class. The remaining information are put in the
        # info dictionary attribute
        for field_name in data:  # replace string by bool if needed
            if data[field_name] == 'True':
                data[field_name] = True
            elif data[field_name] == 'False':
                data[field_name] = False

        polish_data(extract_data)

        extract_data["info"] = data
        return cls(**extract_data)

    @classmethod
    def attributes(cls):
        """return the list of attributes of the class"""
        return cls.__annotations__.keys()

    @property
    def lean_short_name(self):
        """
        Keep only the last two parts, e.g.
        'set_theory.unions_and_intersections.exercise.union_distributive_inter'
        -> # 'exercise.union_distributive_inter'
        """
        return '.'.join(self.lean_name.split('.')[-2:])

    @property
    def statement_to_text(self):
        """
        if self has attribute 'initial_proof_state', then return a string
        with a text version of initial goal. E.g.
        Let X be a set.
        Let A be a subset of X.
        Let B be a subset of X.
        Prove that X \\ (A ∪ B) = (X \\ A) ∩ (X \\ B).
        """
        if self.initial_proof_state is not None:
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
        Return the hierarchical list of lean namespaces ending with the
        namespace containing self.
        e.g.
        'set_theory.unions_and_intersections.exercise.union_distributive_inter'
        -> [set_theory, unions_and_intersections]
        """
        ugly_hierarchy = self.lean_name.split('.')[:-2]
        return ugly_hierarchy

    @property
    def caption(self) -> str:
        """
        Return a string that shows a simplified version of the statement
        (e.g. to be displayed as a tooltip).
        """
        if not self.initial_proof_state:
            text = self.lean_core_statement
        else:
            goal = self.initial_proof_state.goals[0]
            # target = goal.target
            # text = target.math_type.to_display(is_math_type=True)
            text = goal.to_tooltip(type="non-exercise")
        return text

    @property
    def refined_auto_steps(self) -> [AutoStep]:
        """
        Turn the raw string parsed from the lean file into a
        :return:
        """
        if self.__refined_auto_steps:
            return self.__refined_auto_steps

        if not self.auto_steps:
            if not self.auto_test:
                return ''
            else:
                self.auto_steps = self.auto_test
        auto_steps = self.auto_steps.replace('\\n', ' ')
        auto_steps_strings = auto_steps.split(',')
        auto_steps = []
        for string in auto_steps_strings:
            if string is not None:
                auto_steps.append(AutoStep.from_string(string))
        auto_steps = [step for step in auto_steps if step]
        self.__refined_auto_steps = auto_steps
        return auto_steps

    @refined_auto_steps.setter
    def refined_auto_steps(self, refined_auto_steps) -> [AutoStep]:
        self.__refined_auto_steps = refined_auto_steps

    def has_name(self, lean_name):
        return self.lean_name.endswith(lean_name)

    def has_pretty_name(self, pretty_name):
        return self.pretty_name.__contains__(pretty_name)

    def is_definition(self):
        return isinstance(self, Definition)

    def is_theorem(self):
        return isinstance(self, Theorem)

    def is_exercise(self):
        return isinstance(self, Exercise)

    @property
    def type(self):
        if self.is_definition():
            return _('definition')
        elif self.is_theorem():
            return _('theorem')
        elif self.is_exercise():
            return _('exercise')


@dataclass
class Definition(Statement):
    pass


@dataclass
class Theorem(Statement):
    pass


@dataclass
class Exercise(Theorem):
    """
    The class for storing exercises's info.
    On top of the parent class info, the attributes stores
    - the lists of buttons that will be available for this specific exercise
        (in each three categories, resp. logic, proof and magic buttons)
    - the list of statements that will be available for this specific exercise.
    """
    available_logic:            List[Action]    = None
    available_magic:            List[Action]    = None
    available_proof:            List[Action]    = None
    available_statements:       List[Statement] = None
    expected_vars_number:       Dict[str, int]  = None  # e.g. {'X': 3, 'A': 1}
    # FIXME: not used
    info:                       Dict[str, Any]  = None
    negate_statement:           bool            = False
    # This is True if the negation of the statement must be proved.

    @property
    def exercise_number(self) -> int:
        exercises = [statement for statement in self.course.statements
                     if isinstance(statement, Exercise)]
        return exercises.index(self)

    @classmethod
    def from_parser_data(cls, data: dict, statements: list):
        """
        Create an Exercise from the raw data obtained by the parser.
        The main task is to determine
        - the list of available_statements,
        - the list of available actions (corresponding to buttons of the UI)
        from the metadata. Both lists are computed in roughly the same way.

        :param statements:  list of all Statement instances until the current
                            exercise, from which the available_statements
                            list will be extracted
        :param data:        a dictionary whose keys are fields parsed by the
                            Course.from_file method.
        """

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
            # In case int(value) has no meaning:
            except AttributeError:
                log.error(f"wrong format for ExpectedVarsNumber in exercise "
                          f"{data['lean_name']}")
            except ValueError:
                log.error(f"wrong format for ExpectedVarsNumber in exercise "
                          f"{data['lean_name']}")
        # Replace data with formatted data
        data['expected_vars_number'] = expected_vars_number

        ###########################
        # Treatment of statements #
        ###########################
        data['available_statements'] = extract_available_statements(data,
                                                                    statements)
        names = [st.pretty_name for st in data['available_statements']]
        # log.debug(f"Available statements: {names}")

        ########################
        # Treatment of buttons #
        ########################
        # The following modifies directly the data dict,
        # i.e. substitutes the data field content corresponding to
        # keys AvailableLogic, ...
        # by the relevant list of Action buttons.
        extract_available_buttons(data)

        ######################################################################
        # Extract the data corresponding to attributes of the Exercise class #
        ######################################################################
        # To keep only the relevant data, the keys that appear as attributes
        # in the class Exercise or in the parent class Statement:
        # this removes the entry in 'data' corresponding to course_metadata
        extract_data = {}
        for attributes in [Statement.attributes(), cls.attributes()]:
            for attribute in attributes:
                if attribute in data.keys():
                    extract_data[attribute] = data.pop(attribute)
        # Keep only the relevant data, i.e. the keys which corresponds to
        # attribute of the class. The remaining information are put in the
        # info dictionary attribute
        for field_name in data:  # replace string by bool if needed
            if data[field_name] == 'True':
                data[field_name] = True
            elif data[field_name] == 'False':
                data[field_name] = False

        extract_data["info"] = data

        polish_data(extract_data)

        # log.debug(f"available_logic: {extract_data['available_logic']}")
        # log.debug(f"available_proof: {extract_data['available_proof']}")
        # log.debug(f"available_statements: "
        #           f"{len(extract_data['available_statements'])}")
        # log.debug(f"Creating exercise with supplementary info"
        #          f" {extract_data['info']}")
        # log.debug(f"Creating exercise, line: {extract_data['lean_line']}")

        #########################################
        # Finally construct the Exercise object #
        #########################################
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

    def is_last(self) -> bool:
        """
        Check if self is the last exercise in the statements list of
        self.Course.
        """
        return self.next_exercise() is None

    def next_exercise(self):
        """
        Return next Exercise in the statements list of self.Course, or None
        if self is the last exercise in the list.
        """

        statements = self.course.statements
        index = statements.index(self)
        for statement in statements[index+1:]:
            if isinstance(statement, Exercise):
                return statement
        return None


#############
# utilities #
#############
def extract_available_statements(data: dict, statements: list):
    """
    Extract from the statements list the sublist specified by the data dict.

    :param data:        dict whose pertinent keys are
                available_statements,
                available_definitions,
                available_theorems,
                available_exercises
                        and values are either 'NONE', 'UNTIL_NOW',
                        a macro defined in the Lean file,
                        with modifications using "+" or "-",
                        or a (string) list of statement names
    e.g.
    $UNTIL_NOW -union_quelconque_ensembles -intersection_quelconque_ensembles

    :param statements:  list of Statements
    :return:
    """
    # Default value = '$UNTIL_NOW'
    # Other pre-defined value = 'NONE'
    # Other possibility = macro defined in the Lean file
    unsorted_statements = []
    for statement_type in ['definition',
                           'theorem',
                           'exercise',
                           'statement'
                           ]:
        field_name = 'available_' + statement_type + 's'
        if 'available_statements' in data:
            if data['available_statements'].endswith("NONE"):
                # If data['available_statements'].endswith("NONE")
                # then default value is '$NONE'
                data.setdefault(field_name, "$NONE")
        elif (statement_type == 'statement'
              and 'available_statements' not in data.keys()
        ):
            continue  # DO NOT add all statements!
        # if not NONE then default value = UNTIL_NOW
        data.setdefault(field_name, "$UNTIL_NOW")
        # Now field_name is in data
        if data[field_name].endswith("NONE"):
            continue  # No statement of type statement_type

        # (Step 1) Substitute macros in string
        string = substitute_macros(data[field_name], data)
        # this is still a string containing
        # (a) macro names that should either be '$ALL'
        # or in data.keys() with values in Statements, and
        # (b) usual names describing statements.

        statement_callable = make_statement_callable(statement_type,
                                                     statements)
        # This is the function that computes Statements from names
        # We can now compute the available_actions:

        # (Step 2) Replace every word in string by the corresponding
        # statement or list of statements
        more_statements = extract_list(string, data, statement_callable)
        unsorted_statements.extend(more_statements)

    # Finally sort unsorted_statements in the order given by statements:
    # this is not optimised!!
    available_statements = []
    for item in statements:
        if item in unsorted_statements:
            available_statements.append(item)
    return available_statements


def extract_available_buttons(data: dict):
    """
    Extract from the LOGIC_BUTTONS, PROOF_BUTTONS, MAGIC_BUTTONS lists
    the buttons specified in data.

    :param data: dict with pertinent info corresponding to keys
    data[''available_logic],
    data[''available_proof],
    data[''available_magic].

    :return: no direct return, but modify the data dict.
    """
    for action_type in ['logic', 'proof', 'magic']:
        field_name = 'available_' + action_type
        default_field_name = 'default_' + field_name
        if field_name not in data.keys():
            if default_field_name in data.keys():  # Take default list
                data[field_name] = data[default_field_name]
            else:  # Take all buttons
                data[field_name] = '$ALL'  # not optimal

        # log.debug(f"Processing data in {field_name}, {data[field_name]}")

        string = substitute_macros(data[field_name], data)
        # This is still a string with macro names that should either
        # be '$ALL' or in data.keys() with values in Action
        action_callable = make_action_callable(action_type)
        # This is the function that computes Actions from names.
        # We can now compute the available_actions:
        data[field_name] = extract_list(string, data, action_callable)


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
        # log.debug(f"searching Action {name}")
        if name in ['NONE', '$NONE']:
            return []
        if name in ['ALL', '$ALL']:
            return dictionary.values()
        if not name.startswith("action_"):
            name = "action_" + name
        action = None
        if name in dictionary:
            action = [dictionary[name]]
        return action

    return action_callable


def make_statement_callable(prefix: str, statements) -> callable:
    """
    Construct the function corresponding to prefix
    :param prefix:      one of 'statement', 'definition', 'theorem', 'exercise'
    :param statements:  list of instances of the Statement class
    :return:            a callable
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
        # log.debug(f"searching {prefix} {name}")
        if name in ['NONE', '$NONE']:
            return []
        if name in ['$UNTIL_NOW', 'UNTIL_NOW']:
            available_statements = []
            for statement in statements:
                if class_ == Theorem:
                    if (isinstance(statement, Theorem)
                            and not isinstance(statement, Exercise)):
                        available_statements.append(statement)
                        # log.debug(f"Considering {statement.pretty_name}...")
                elif isinstance(statement, class_):
                    available_statements.append(statement)
                    # log.debug(f"Considering {statement.pretty_name}...")
            return available_statements

        statement = None
        name = prefix + '.' + name
        index, nb = find_suffix(name, [item.lean_name for item in statements])
        if nb > 0:
            statement = [statements[index]]
        return statement

    return statement_callable


def polish_data(data):
    """
    Make some formal smoothing.
    """
    if 'description' in data:
        data['description'] = data['description'].capitalize()
        if data['description'][-1].isalpha():
            data['description'] += '.'


if __name__ == "__main__":
    print(LOGIC_BUTTONS)
    print(PROOF_BUTTONS)
    print(LOGIC_BUTTONS.keys())
    print(PROOF_BUTTONS.keys())