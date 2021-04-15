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
                       'assumption': _('QED'),
                       'compute': _('Compute')
                       }


@dataclass
class AutoStep:
    """
    A class to store one step of proof in deaduction, simulating selection,
    choice of button or statement, and user input.
    """
    selection:  [str]
    button:     str
    statement:  str
    user_input: [str]

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
        # Split at spaces and remove unnecessary spaces
        items = [item.strip() for item in string.split(' ') if item]
        for item in items:
            if item.startswith('definition') \
                    or item.startswith('theorem'):
                statement = item
                button_or_statement_rank = items.index(item)
                break
            if item in BUTTONS_SYMBOLS:
                button = item
                button_or_statement_rank = items.index(item)
                break
            elif item in alternative_symbols:
                button = alternative_symbols[item]
                button_or_statement_rank = items.index(item)
                break
        if not button and not statement:
            return None

        selection = items[:button_or_statement_rank]
        user_input = items[button_or_statement_rank+1:]

        return cls(selection, button, statement, user_input)


if __name__ == '__main__':
    print(BUTTONS_SYMBOLS)
    # french result :
    # ['∧', '∨', '¬', '⇒', '⇔', '∀', '∃', 'Calculer', 'CQFD', 'Méthodes De
    # Preuve', 'Nouvel Objet', 'Appliquer']
    # please rather use english equivalents given in the above
    # alternative_symbols dictionary.

