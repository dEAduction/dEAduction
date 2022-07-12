"""
# user_action.py : a class to store user actions in the UI #

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 12 2021 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the d∃∀duction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    d∃∀duction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import Union, Optional, List

from deaduction.pylib.mathobj import ContextMathObject


class UserAction:
    """
    A class for storing usr actions for one step.
    Button name is the action name (e.g. "action_and --> name = "and").
    """

    def __init__(self, button_name: str):
        self.button_name = button_name


class UserHistoryAction(UserAction):
    history_actions_names = ("history_undo", "history_redo",
                             "history_rewind", "history_goto")

    def __init__(self, button_name: str):
        assert button_name in self.history_actions_names
        super().__init__(button_name)


class UserProofAction(UserAction):
    """
    Statement name is the end of the lean_name (e.g. definition.inclusion)
    so that lean_name.endswith(statement_name) is True.
    There are two main ways to create a UserProofAction:
        - either    UserProofAction(button_name="forall")
        - or        UserProofAction(statement_name="definition.inclusion")
    `selection` and `target_selected` attributes may also be specified.
    """

    def __init__(self,
                 button_name: str = "statement",
                 statement_name: str = None,
                 selection: Optional[List[ContextMathObject]] = None,
                 target_selected: bool = False,
                 user_input: Optional[List[Union[str, int]]] = None):
        super().__init__(button_name)

        if selection is None:
            selection = []
        if user_input is None:
            user_input = []
        self.statement_name  = statement_name
        self.selection       = selection
        self.target_selected = target_selected
        self.user_input      = user_input

    def set_selection(self, selection):
        self.selection = selection

    def set_target_selected(self, yes=True):
        self.target_selected = yes

    def add_user_input(self, choice: [Union[str, int]]):
        self.user_input.append(choice)

    def contextualize(self, goal):
        """
        Turn self.selection from [str] to [ContextMathObject]
        """
        pass  # TODO


button_dict = {'→': "implies",
               '⇒': "implies",
               '↔': "iff",
               '⇔': "iff",
               '∀': "forall",
               '∃': "exists",
               '∧': "and",
               '∨': "or",
               '¬': "not",
               '=': "equal",
               "CQFD": "assumption",
               'compute': "assumption",
               '↦': "map",
               'proof': 'proof_methods',
               'new': 'new_object',
               'object': 'new_object'
               }


class AutoStep(UserProofAction):
    """
    A class to store one step of proof in deaduction, simulating selection,
    choice of button or statement, and user input. Attributes error_msg,
    success_msg also allow to store deaduction's answer to the step; this is
    useful for debugging, e.g comparing actual answer to answer in a
    stored exercise.
    Data is stored in a string format, which is independent of the objects
    of the interface, which is crucial for saving.
    AutoStep may be created:
    - either from a raw string; this is a useful way to get them from
    metadata in the Lean file (see the exercise.refined_auto_steps property);
    - either from ProofStep; this is the way AutoStep are systematically
    computed and stored during exercise solving.
    AutoStep are used for testing.

    :attribute raw_string: A single string that contains all information.
    Other attributes may be computed from this string by the "from_string"
    method.

    :attribute selection: a list of string represented selected objects of
    the context, e.g. @P1, @O2 for property n°1, object n°2 of the context.

    :attribute button: A button symbol or equivalent (cf BUTTON_SYMBOLS,
    button_dict).

    :attribute statement: statement short name,
    e.g. definition.intersection_two_sets

    :attribute user_input: list of integers converted into string.
    """

    raw_string: str = ""

    # Response:
    error_type: int = 0  # 0 = WrongUserInput, 1 = FailedRequestError
    error_msg: str = ""
    success_msg: str = ""

    error_dic = {0: '',
                 1: 'WrongUserInput',
                 2: 'FailedRequestError',
                 3: 'Timeout',
                 4: 'UnicodeDecodeError',
                 5: 'No proof state'}

    def __init__(self, button_name: str, statement_name: str,
                 selection: [str], target_selected: bool = False,
                 user_input: [Union[str, int]] = None,
                 raw_string: str = "",
                 error_type: int = 0, error_msg: str = "",
                 success_msg: str = ""):

        super().__init__(button_name, statement_name,
                         selection, target_selected, user_input)

        self.raw_string = raw_string
        self.error_type = error_type
        self.error_msg = error_msg
        self.success_msg = success_msg

    @classmethod
    def from_string(cls, string):
        """
        Analyze a string to extract an AutoStep instance.
        The string should contain a button symbol (e.g. '∀')
        xor a statement name (e.g. 'definition.inclusion').
        Items are separated by spaces, and the last item should represents
        an action, i.e. a statement name or a button symbol.
         e.g. the following sequence of strings may be passed to the
        "from.string" method:
            ∀ success=Objet_x_ajouté_au_contexte,
            ∀ success=Objet_x'_ajouté_au_contexte,
            ⇒ success=propriété_H0_ajoutée_au_contexte,
            @P3 @P2 ⇒ success=propriété_H3_ajoutée_au_contexte,
            @P4 @P1 ⇒ success=propriété_H4_ajoutée_au_contexte,
            Goal!
        """

        string.replace("\\n", " ")
        button = None
        statement = None
        button_or_statement_rank = None
        error_type = 0
        error_msg = ""
        success_msg = ""

        # Split at spaces and remove unnecessary spaces
        items = [item.strip() for item in string.split(' ') if item]
        for item in items:
            if item.startswith('definition') \
                    or item.startswith('theorem'):
                statement = item
                button_or_statement_rank = items.index(item)
            # elif item in BUTTONS_SYMBOLS:
            #     button = item
            #     button_or_statement_rank = items.index(item)
            elif item in button_dict.values():
                button = item
                button_or_statement_rank = items.index(item)
            elif item in button_dict:
                button = button_dict[item]
                button_or_statement_rank = items.index(item)
            elif item in ('WrongUserInput', 'WUI'):
                error_type = 1
                items[items.index(item)] = ''  # item is not user_input
            elif item in ('FailedRequestError', 'FRE'):
                error_type = 2
                items[items.index(item)] = ''
            elif item.startswith('error='):
                error_msg = item[len('error='):].replace('_', ' ')
                items[items.index(item)] = ''
            elif item.startswith('e='):
                error_msg = item[len('e='):].replace('_', ' ')
                items[items.index(item)] = ''
            elif item.startswith('success='):
                success_msg = item[len('success='):].replace('_', ' ')
                items[items.index(item)] = ''
            elif item.startswith('s='):
                success_msg = item[len('s='):].replace('_', ' ')
                items[items.index(item)] = ''

        if not button and not statement:
            return None

        selection = items[:button_or_statement_rank]
        user_input = [item for item in items[button_or_statement_rank+1:]
                      if item]  # Remove if item = ''
        if "target" in selection:
            selection.remove("target")
            target_selected = True
        else:
            target_selected = False

        return cls(button, statement, selection, target_selected, user_input,
                   string, error_type, error_msg, success_msg)

    @classmethod
    def from_proof_step(cls, proof_step, emw):
        """
        Convert proof_step to the corresponding AutoStep, e.g. for use as
        with auto_test.

        :param proof_step: instance of ProofStep
        :param emw:         ExerciseMainWindow
        :return:
        """

