"""
pattern_string.py : provide some basic pattern strings for PatternMathObject.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 06 2023 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2023 the d∃∀duction team

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

from collections import OrderedDict

from .marked_pattern_math_object import MarkedPatternMathObject
from deaduction.pylib.mathobj import ContextMathObject

global _

# From display_data:
# "DIFFERENCE": (0, " - ", 1),
# "SUM": (0, " + ", 1),
# "MULT": (0, r" \mul ", 1),
# "PRODUCT": (0, r" \times ", 1),
# "DIV": (0, r"/", 1),
# "MINUS": ("-", 0),
# "POWER": (0, [r'\super', 1]),
# "SQRT": ('√', -1),

# NUMBERS
numbers = {str(n): f'NUMBER/value={n}' for n in range(11)}
calculator_pattern_strings = {     # NUMBERS
                   # '0': 'NUMBER/value=0',  # Unspecified math_type...
                   # '1': 'NUMBER/value=1',
                   # '2': 'NUMBER/value=2',
                   # '3': 'NUMBER/value=3',
                   # '4': 'NUMBER/value=4',
                   '+': 'SUM(?0: ?2, ?1: ?2)',  # pb = real + int ?
                   '-': 'DIFFERENCE(?0: ?2, ?1: ?2)',  # Pb =  or MINUS(?0)
                    # '-': ('MINUS(?0)', 'DIFFERENCE(?0: ?2, ?1: ?2)'),
                   '*': 'MULT(?0: ?2, ?1: ?2)',  # pb = real + int ?
                   '÷': 'DIV(?0: ?2, ?1: ?2)',  # pb = real + int ?
                   '.': 'POINT(?0, ?1)',
                    # Useful for set extension:
                   ',': 'COMMA(?0, ?1)',
                   'sin': 'APP(CONSTANT/name=sin, ?0: CONSTANT/name=ℝ)',

                   '()': 'CLOSE_PARENTHESIS(OPEN_PARENTHESIS(?0))',
                   # ')': 'CLOSE_PARENTHESIS(...)',
                   # LOGIC
                   '∀': 'QUANT_∀(?0, ?1, ?2)',  # FIXME: bound_var
                   '⇒': 'PROP_IMPLIES(?0: PROP, ?1: PROP)',
                   '∧': 'PROP_AND(?0: PROP, ?1: PROP)',
                   '∨': 'PROP_OR(?0: PROP, ?1: PROP)',
                   # SET THEORY
                   '∩': 'SET_INTER: SET(?2)(?0: SET(?2), ?1: SET(?2))',
                   '∪': 'SET_UNION: SET(?2)(?0: SET(?2), ?1: SET(?2))',
                   '{}': 'SET_EXTENSION1(?0)',
                    # Fixme: boundvar:
                   '{|}': 'SET_INTENSION(?0: TYPE, ?1, ?2: PROP)'
}
calculator_pattern_strings.update(numbers)

automatic_matching_patterns = {
    "APP(?0: !FUNCTION(?1, ?2), ?3: ?1)": ((0,), r"\parentheses", (1,)),
    "COMPOSITE_NUMBER(...)": (0, 1),  # FIXME: could have more children
    "SEVERAL(?0, ?1)": (0, ' ', 1),
    "SEVERAL(?0, ?1, ?2)": (0, ' ', 1, ' ', 2)
}


class CalculatorPatternLines:
    """
    A class to store the logical data needed to build a group of buttons for
    the calculator.

    """

    marked_patterns = OrderedDict()
    for symbol, string in calculator_pattern_strings.items():
        marked_pmo = MarkedPatternMathObject.from_string(string, [])
        marked_patterns[symbol] = marked_pmo

    def __init__(self, title: str, lines: [],
                 patterns=None):

        # FIXME: marked_patterns should be just patterns??
        #  turned into marked_patterns when inserted
        self.title = title
        self.lines = lines
        if patterns:
            self.marked_patterns = patterns

    @classmethod
    def from_context(cls, context_math_objects: [ContextMathObject]):
        title = _('Context')
        patterns = {}
        for obj in context_math_objects:
            symbol = obj.to_display(format_='utf8')
            patterns[symbol] = obj
        cpl = cls(title=title,
                  lines=list(patterns.keys()),
                  patterns=patterns)
        return cpl

    def pattern_from_symbol(self, symbol):
        pattern = self.marked_patterns[symbol]
        return pattern


calculator_group = CalculatorPatternLines(_('Calculator'),
                                          [['7', '8', '9', '÷'],
                                           ['4', '5', '6', '*'],
                                           ['1', '2', '3', '-'],
                                           ['0', '.', '()', '+'],
                                           ])
sci_calc_group = CalculatorPatternLines(_('scientific calculator'),
                                        [['sin'],
                                         # ['=', '<']
                                         ])
logic_group = CalculatorPatternLines(_('Logic'), [['∀', '⇒', '∧']])
set_theory_group = CalculatorPatternLines(_('Set theory'), [['∩', '∪']])

