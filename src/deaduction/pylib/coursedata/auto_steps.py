"""
##############################################
# auto_steps.py : provide the AutoStep class #
##############################################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 04 2021 (creation)
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

from dataclasses import dataclass
from typing import Union

import deaduction.pylib.config.vars as cvars

# from deaduction.pylib.mathobj import ProofStep
import deaduction.pylib.actions.logic
import deaduction.pylib.actions.magic
import logging

log = logging.getLogger(__name__)
global _

##############################################
# Lists of all instances of the Action class #
##############################################
# LOGIC_BUTTONS = deaduction.pylib.actions.logic.__actions__
# PROOF_BUTTONS = deaduction.pylib.actions.proofs.__actions__
# MAGIC_BUTTONS = deaduction.pylib.actions.magic.__actions__
# # e.g. key = action_and, value = corresponding instance of the class Action
#
# LOGIC_BUTTONS_SYMBOLS = [LOGIC_BUTTONS[key].symbol for key in LOGIC_BUTTONS]
# PROOF_BUTTONS_SYMBOLS = [PROOF_BUTTONS[key].symbol for key in PROOF_BUTTONS]
# MAGIC_BUTTONS_SYMBOLS = [MAGIC_BUTTONS[key].symbol for key in MAGIC_BUTTONS]



# BUTTONS_SYMBOLS = LOGIC_BUTTONS_SYMBOLS \
#                   + MAGIC_BUTTONS_SYMBOLS \
#                   + PROOF_BUTTONS_SYMBOLS


button_dict = {
               '∀': "forall",
               '∃': "exists",
               '→': "implies",
               '⇒': "implies",
               '∧': "and",
               '∨': "or",
               '∀prove': "forall_prove",
               '∃prove': "exists_prove",
               '→prove': "implies_prove",
               '⇒prove': "implies_prove",
               '∧prove': "and_prove",
               '∨prove': "or_prove",
               '∀use': "forall_use",
               '∃use': "exists_use",
               '→use': "implies_use",
               '⇒use': "implies_use",
               '∧use': "and_use",
               '∨use': "or_use",
               '↔': "iff",
               '⇔': "iff",
               '¬': "not",
               '=': "equal",
               "CQFD": "assumption",
               'compute': "assumption",
               '↦': "map",
               'proof': 'proof_methods',
               'new': 'new_object',
               'object': 'new_object'
               }


class UserAction:
    """
    A class for storing usr actions for one step.
    Button name is the action name (e.g. "action_and --> name = "and")
    Statement name is the end of the lean_name (e.g. definition.inclusion)
        so that lean_name.endswith(statement_name) is True.
    """
    selection = None  # [ContextMathObject] or [str]
    target_selected = None
    button_name = ""  # str
    statement = None  # Optional[Statement]
    _statement_name = ""  # str
    user_input = None  # Union[int, str]
    prove_or_use = ""  # "" / "prove" / "use"

    def __init__(self,
                 selection=None,
                 button_name=None,
                 statement=None,
                 statement_name=None,
                 user_input=None,
                 target_selected=False):
        if selection is None:
            selection = []
        if user_input is None:
            user_input = []
        self.selection = selection
        self.button_name = button_name
        self.statement = statement
        self._statement_name = statement_name
        self.user_input = user_input
        self.target_selected = target_selected

    @classmethod
    def simple_action(cls, symbol):
        user_action = cls(button_name=symbol)
        return user_action

    @classmethod
    def from_proof_step(cls, proof_step):
        return proof_step.user_action
        # return cls(selection=proof_step.selection,
        #            button_name=proof_step.button_name,
        #            statement_name=proof_step.statement_lean_name,
        #            user_input=proof_step.user_input,
        #            target_selected=proof_step.target_selected)

    def __repr__(self) -> str:
        msg = f"UserAction with {len(self.selection)} selected objects, " \
              f"button name = {self.button_name}, statement name = " \
              f"{self.statement_name}, user input = {self.user_input}," \
              f"target selected = {self.target_selected}"
        return msg

    @property
    def statement_name(self):
        if self.statement:
            return self.statement.lean_name
        else:
            return self._statement_name

    def prove_or_use_button_name(self):
        name = self.button_name
        if self.prove_or_use and not (name.startswith("use_")
                                      or name.startswith("prove_")):
            name = self.prove_or_use + '_' + name
        return name

    def button_name_adapted_to_mode(self, mode=None):
        """
        Return the button name that corresponds to self.button_name adapted
        to mode : without prefix 'prove_' / 'use_' if the unified buttons are
        displayed, with prefix in the opposite case. Note that the returned
        name may not be adapted if self.prove_or_use is None.
        """

        name = self.button_name
        if not name:
            return ""

        if not mode:
            mode = cvars.get('logic.button_use_or_prove_mode')

        adapted_name = name
        if mode in ('display_switch', 'display_both'):
            adapted_name = self.prove_or_use_button_name()
        elif mode == 'display_unified':
            adapted_name = name.replace('use_', '')
            adapted_name = adapted_name.replace('prove_', '')

        return adapted_name


class AutoStep(UserAction):
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
    # Inputs:
    # selection:  [str]
    # button_name:     str
    # statement:  str
    # user_input: [str]

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
                 5: 'No proof state',
                 6: 'File unchanged',
                 7: 'Action cancelled',
                 10: 'unknown error'}

    def __init__(self, selection, button_name, statement_name, user_input,
                 target_selected, raw_string, error_type, error_msg, success_msg):

        UserAction.__init__(self, selection, button_name, None,
                            statement_name, user_input, target_selected)
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
        statement_name = None
        button_or_statement_rank = None
        error_type = 0
        error_msg = ""
        success_msg = ""
        target_selected = None

        # Split at spaces and remove unnecessary spaces
        items = [item.strip() for item in string.split(' ') if item]
        for item in items:
            if item.startswith('definition') \
                    or item.startswith('theorem'):
                statement_name = item
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
            elif item.startswith('target') or item.startswith(_('target')):
                target_selected = True

        if not button and not statement_name:
            return None

        selection = items[:button_or_statement_rank]
        try:
            selection.remove('target')
            selection.remove(_('target'))
        except ValueError:
            pass

        # Remaining non-trivial items are user input
        user_input = [item.replace('__', ' ')
                      for item in items[button_or_statement_rank+1:] if item]
        user_input = [int(item) if item.isdecimal() else item
                      for item in user_input]

        return cls(selection, button, statement_name, user_input,
                   target_selected, string, error_type, error_msg, success_msg)

    @classmethod
    def from_proof_step(cls, proof_step, emw):
        """
        Convert proof_step to the corresponding AutoStep, e.g. for use as
        with auto_test.
        
        :param proof_step: instance of ProofStep 
        :param emw:         ExerciseMainWindow
        :return: 
        """

        user_action: UserAction = proof_step.user_action

        # Selection: [str]
        selection = []
        if user_action.selection:
            # log.debug("Analysing selection...")
            for math_object in user_action.selection:
                # log.debug(f"Searching {math_object.display_name}")
                # log.debug(f"in {[mo.display_name for mo in emw.objects]}")
                # log.debug(f"& {[mo.display_name for mo in emw.properties]}")
                if math_object in emw.objects:
                    item_str = "@O" + str(emw.objects.index(math_object)+1)
                elif math_object in emw.properties:
                    item_str = "@P" + str(emw.properties.index(math_object)+1)
                elif math_object.info.get("user_input"):
                    # Artificial object created from user_input:
                    #  do not save (will be retrieved from user_input).
                    item_str = None
                else:
                    item_str = math_object.display_name
                    log.debug(f"Object {item_str} not found")
                if item_str is not None:
                    selection.append(item_str)

        # Target selected ?
        if user_action.target_selected:
            selection.append("target")

        # Button: '∧', '∨', '¬', '⇒', '⇔', '∀', '∃', 'compute', 'CQFD',
        #         'proof_methods', 'new_objects', 'apply'
        button = user_action.prove_or_use_button_name()

        if button is None:
            button = ''

        # Statement: short Lean name
        statement = user_action.statement.lean_short_name \
            if user_action.statement else ''

        if not (button or statement):
            return None

        # User input: int
        user_input = []
        if user_action.user_input:
            user_input = [str(item) for item in user_action.user_input]

        error_msg = proof_step.error_msg
        if error_msg:
            error_msg = error_msg.split(',')[0]  # No ',' allowed in AutoStep
            error_msg = 'error=' + error_msg.replace(' ', '_')
        success_msg = proof_step.success_msg
        if success_msg:
            success_msg = success_msg.split(',')[0]
            success_msg = 'success=' + success_msg.replace(' ', '_')

        # Computing string
        string = ''
        if selection:
            string = ' '.join(selection) + ' '
        string += button + statement
        if user_input:
            # Replace spaces by '__'
            user_input = [item.replace(' ', '__') for item in user_input]
            string += ' ' + ' '.join(user_input)
        if proof_step.is_error():
            string += ' ' + AutoStep.error_dic[proof_step.error_type]
            string += ' ' + error_msg
        if success_msg:
            string += ' ' + success_msg

        target_selected = proof_step.target_selected

        return cls(selection, button, statement, user_input, target_selected,
                   string, proof_step.error_type, proof_step.error_msg,
                   proof_step.success_msg)


if __name__ == '__main__':
    pass
    # print(BUTTONS_SYMBOLS)
    # french result :
    # ['∧', '∨', '¬', '⇒', '⇔', '∀', '∃', 'Calculer', 'CQFD', 'Méthodes De
    # Preuve', 'Nouvel Objet', 'Appliquer']
    # Rather use english equivalents given in the above
    # button_dict dictionary.

