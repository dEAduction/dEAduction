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
# from typing import List, Dict, Any
# from parsimonious.grammar import Grammar
# from parsimonious.nodes import NodeVisitor

import deaduction.pylib.config.vars as cvars
from deaduction.pylib.config.i18n import _

from deaduction.pylib.mathobj import ProofStep
import deaduction.pylib.actions.logic
import deaduction.pylib.actions.proofs
import deaduction.pylib.actions.magic
import logging

log = logging.getLogger(__name__)

##############################################
# Lists of all instances of the Action class #
##############################################
LOGIC_BUTTONS = deaduction.pylib.actions.logic.__actions__
PROOF_BUTTONS = deaduction.pylib.actions.proofs.__actions__
MAGIC_BUTTONS = deaduction.pylib.actions.magic.__actions__
# e.g. key = action_and, value = corresponding instance of the class Action

LOGIC_BUTTONS_SYMBOLS = [LOGIC_BUTTONS[key].symbol for key in LOGIC_BUTTONS]
PROOF_BUTTONS_SYMBOLS = [PROOF_BUTTONS[key].symbol for key in PROOF_BUTTONS]
MAGIC_BUTTONS_SYMBOLS = [MAGIC_BUTTONS[key].symbol for key in MAGIC_BUTTONS]


# Tentative grammar
# auto_steps = """
# steps = step ("," step)*
#
# step = (selections "/")* button_symbol ("/" user_inputs)*
#
# selections = spaces* (selection spaces*)+
# selection = any_char_not_space*
#
# button_symbol = spaces* button_symbol_ spaces*
#
# user_inputs = spaces* (user_input spaces*)+
# user_input = any_char*
#
# any_char_not_space = !"/" !spaces
# spaces = (" " / end_of_line)*
# end_of_line = "\\n"
# """
# auto_steps_grammar= Grammar(auto_steps)
#
# class AutoStepVisitor(NodeVisitor):
#     def visit_auto_steps(self,
#                         node: str,
#                         visited_children: []):
#         pass
#
#
#     def visit_step(self, node, visited_children):
#         return None
#
#
#     def visit_selections(self, node, visited_children):
#         return None
#
#     def visit_selection(self, node, visited_children):
#         return node.txt
#
#
#
#     def generic_visit(self, node, visited_children):
#         return None


BUTTONS_SYMBOLS = LOGIC_BUTTONS_SYMBOLS \
                  + MAGIC_BUTTONS_SYMBOLS \
                  + PROOF_BUTTONS_SYMBOLS


alternative_symbols = {'→': '⇒',
                       '↔': '⇔',
                       'forall': '∀',
                       'exists': '∃',
                       'and': '∧',
                       'or': '∨',
                       'not': '¬',
                       'proof_methods': _('Proof Methods'),
                       'new_object': _('New Object'),
                       'apply': _('Apply'),
                       'assumption': _('Goal!'),
                       "CQFD": _('Goal!'),
                       'compute': _('Compute')
                       }


@dataclass
class AutoStep:
    """
    A class to store one step of proof in deaduction, simulating selection,
    choice of button or statement, and user input.
    """
    raw_string: str
    selection:  [str]
    button:     str
    statement:  str
    user_input: [str]
    error_type: int  # 0 = WrongUserInput, 1 = FailedRequestError
    error_msg: str
    success_msg: str

    error_dic = {0: '', 1: 'WrongUserInput', 2: 'FailedRequestError'}

    @classmethod
    def from_string(cls, string):
        """
        Analyze a string to extract an AutoStep instance.
        The string should contain a button symbol (e.g. '∀')
        xor a statement name (e.g. 'definition.inclusion')
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
            elif item in BUTTONS_SYMBOLS:
                button = item
                button_or_statement_rank = items.index(item)
            elif item in alternative_symbols:
                button = alternative_symbols[item]
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

        return cls(string, selection, button, statement, user_input,
                   error_type, error_msg, success_msg)

    @classmethod
    def from_proof_step(cls, proof_step: ProofStep, emw):
        """
        Convert proof_step to the corresponding auto_step, e.g. for use as
        with auto_test.
        
        :param proof_step: instance of ProofStep 
        :param emw:         ExerciseMainWindow
        :return: 
        """

        # Selection: [str]
        selection = []
        if proof_step.selection:
            # log.debug("Analysing selection...")
            for math_object in proof_step.selection:
                # log.debug(f"Searching {math_object.display_name}")
                # log.debug(f"in {[mo.display_name for mo in emw.objects]}")
                # log.debug(f"& {[mo.display_name for mo in emw.properties]}")
                if math_object in emw.objects:
                    item_str = "@O" + str(emw.objects.index(math_object)+1)
                elif math_object in emw.properties:
                    item_str = "@P" + str(emw.properties.index(math_object)+1)
                else:
                    item_str = math_object.display_name
                    log.debug(f"Object {item_str} not found")
                selection.append(item_str)

        # Button: '∧', '∨', '¬', '⇒', '⇔', '∀', '∃', 'compute', 'CQFD',
        #         'proof_methods', 'new_objects', 'apply'
        button = ''
        if proof_step.button:
            button = proof_step.button.symbol \
                if hasattr(proof_step.button, 'symbol') \
                else proof_step.button.replace(' ', '_')

        # Statement: short Lean name
        statement = ''
        if proof_step.statement_item:  # This is a TreeWidgetItem
            statement = proof_step.statement_item.statement.lean_short_name

        if not (button or statement):
            return None

        # User input: int
        user_input = []
        if proof_step.user_input:
            user_input = [str(item) for item in proof_step.user_input]

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
            string += ' ' + ' '.join(user_input)
        if proof_step.is_error():
            string += ' ' + AutoStep.error_dic[proof_step.error_type]
            string += ' ' + error_msg
        if success_msg:
            string += ' ' + success_msg

        return cls(string, selection, button, statement, user_input,
                   proof_step.error_type, proof_step.error_msg,
                   proof_step.success_msg)


if __name__ == '__main__':
    print(BUTTONS_SYMBOLS)
    # french result :
    # ['∧', '∨', '¬', '⇒', '⇔', '∀', '∃', 'Calculer', 'CQFD', 'Méthodes De
    # Preuve', 'Nouvel Objet', 'Appliquer']
    # please rather use english equivalents given in the above
    # alternative_symbols dictionary.

