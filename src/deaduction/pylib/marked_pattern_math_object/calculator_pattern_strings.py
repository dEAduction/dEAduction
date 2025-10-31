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
from typing import Optional

from deaduction.pylib.math_display.nodes import Node, DefinitionNode
from .marked_pattern_math_object import MarkedPatternMathObject
from deaduction.pylib.pattern_math_obj.definition_math_object import DefinitionMathObject
from deaduction.pylib.mathobj import ContextMathObject
from deaduction.pylib.math_display import MathDisplay, PatternMathDisplay
from ..text import button_symbol

# from deaduction.pylib.math_display.pattern_init import pattern_latex

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
numbers = {str(n): f'NUMBER/value={n}: *NUMBER_TYPES' for n in range(11)}

# Dict of symbol / pattern for CalculatorPatternLines
calculator_pattern_strings = {
                   '+': 'SUM: *NUMBER_TYPES()(?0: *NUMBER_TYPES, ?1: *NUMBER_TYPES)',
                    # FIXME: OPPOSITE vs DIFFERENCE??  -1 vs 2-3
                   '-': 'DIFFERENCE: *NUMBER_TYPES()(?0: *NUMBER_TYPES, ?1: *NUMBER_TYPES)',
                   '*': 'MULT: *NUMBER_TYPES()(?0: *NUMBER_TYPES, ?1: *NUMBER_TYPES)',  # pb = real + int ?
                   '/': 'DIV: *NUMBER_TYPES()(?0: *NUMBER_TYPES, ?1: *NUMBER_TYPES)',
                   '.': 'POINT()',
                    # Useful for set extension:
                   ',': 'COMMA(?0, ?1)',
                   # FIXME:
                   # 'sin': 'APP: CONSTANT/name=ℝ()(CONSTANT/name=sin, '
                   #        '?0: CONSTANT/name=ℝ)',
                   'sin': 'CONSTANT/name=sin: FUNCTION(*NUMBER_TYPES, *NUMBER_TYPES)',
                   # 'max': 'CONSTANT/name=max: FUNCTION(*NUMBER_TYPES, FUNCTION(*NUMBER_TYPES,*NUMBER_TYPES))',
                   # 'max': 'APP: *NUMBER_TYPES()(APP(CONSTANT/name=max, ?0: *NUMBER_TYPES),'
                   #        '?1: *NUMBER_TYPES)',
                   # FIXME:
                   'max': 'APP: *NUMBER_TYPES()(CONSTANT/name=max, ?0: *NUMBER_TYPES,'
                          '?1: *NUMBER_TYPES)',
                   '()': 'GENERIC_PARENTHESES(?0)',
                   # ')': 'CLOSE_PARENTHESIS(...)',
                   # LOGIC
                   # FIXME: bound_var
                   '∀': 'QUANT_∀: PROP()(?0, LOCAL_CONSTANT/name=x, ?2)',
                   # '∀>': 'QUANT_∀(?0, LOCAL_CONSTANT/name=x, '
                   #       'PROP_IMPLIES(PROP_>()))',
                   # '⇒': 'PROP_IMPLIES: PROP()(?0: PROP, ?1: PROP)',
                   # '∧': 'PROP_AND: PROP()(?0: PROP, ?1: PROP)',
                   # '∨': 'PROP_OR: PROP()(?0: PROP, ?1: PROP)',
                   # SET THEORY
                   # '∩': 'SET_INTER: SET(?2)(?0: SET(?2), ?1: SET(?2))',
                   # '∪': 'SET_UNION: SET(?2)(?0: SET(?2), ?1: SET(?2))',
                   # '{}': 'SET_EXTENSION1(?0)',
                    # Fixme: boundvar:
                   '{|}': 'SET_INTENSION(?0: TYPE, ?1, ?2: PROP)'
}
calculator_pattern_strings.update(numbers)

automatic_matching_patterns = {
    "APP(?0: !FUNCTION(?1, ?2), ?3: ?1): ?2",  # : ((0,), r"\parentheses",
    # (1,)),
    # FIXME: a single point... a single sign...
    "COMPOSITE_NUMBER: *NUMBER_TYPES()(?0: *NUMBER_TYPES, ?1: *NUMBER_TYPES)",
    # : (0, 1),
    # "SEVERAL(?0, ?1)": (0, ' ', 1),
    # "SEVERAL(?0, ?1, ?2)": (0, ' ', 1, ' ', 2)
    # "GENERIC_NODE(?0, ?1)"  #: (0, 1)
}


def populate_automatic_patterns(cls):
    for pattern_string in automatic_matching_patterns:
        mpmo = MarkedPatternMathObject.from_string(pattern_string)
        MarkedPatternMathObject.automatic_patterns.append(mpmo)


calc_shortcuts_macro = dict()
for key, value in MathDisplay.standard_latex_to_utf8.items():
    if isinstance(value, str):
        calc_shortcuts_macro[key] = value

calc_shortcuts_macro.update({'\\implies': '⇒',
                             '\\and': '∧',
                             '*': '\\times'})

# greek_list = ['αβγ', 'ε', 'δ', 'η', 'φψ', 'λμν', 'πρ', 'θα', 'στ']

greek_shortcuts = {'\\alpha': 'α', '\\beta': 'β', '\\gamma': 'γ',
                   '\\epsilon': 'ε', '\\delta': 'δ', '\\eta': 'η', '\\phi':
                       'φ', '\\psi': 'ψ', '\\lambda': 'λ', '\\mu': 'μ',
                   '\\nu':  'ν', '\\pi': 'π', '\\rho': 'ρ', '\\theta': 'θ',
                   '\\sigma': 'σ', '\\tau': 'τ'}

calc_shortcuts_macro.update(greek_shortcuts)


class CalculatorAbstractButton:
    """
    A class to store the data needed to build a CalculatorButton.
    """

    def __init__(self, latex_symbol: str,
                 patterns: [MarkedPatternMathObject],  # or just one
                 button_symbol: str = None,
                 tooltip: Optional[str] = None,
                 menu=None,
                 shortcut=None):
        self.latex_symbol = latex_symbol
        if not button_symbol:
            button_symbol = MathDisplay.latex_to_utf8(self.latex_symbol)
        self.button_symbol = button_symbol
        self.tooltip = tooltip
        if not patterns:
            patterns = CalculatorPatternLines.marked_patterns.get(
                self.button_symbol)
        self.patterns = patterns if isinstance(patterns, list) else [patterns]
        self.menu = menu
        self.shortcut = shortcut

    @property
    def lean_symbol(self):
        symbol = MathDisplay.latex_to_lean(self.latex_symbol)
        return symbol

    @classmethod
    def from_node(cls, node: Node):
        patterns = node.marked_pattern_math_objects()
        return cls(latex_symbol=node.latex_symbol(),
                   button_symbol=node.button_symbol(),
                   tooltip=node.button_tooltip(),
                   patterns=patterns,
                   shortcut=node.shortcut,
                   menu=node.button_menu())

    @classmethod
    def from_math_object(cls, math_object, copy_math_object=True):
        symbol = math_object.to_display(format_='html', use_color=True)
        shortcut: str = math_object.to_display(format_='utf8', use_color=True)
        if not shortcut.replace('\\', '').isalnum():
            shortcut = None
        if copy_math_object:
            marked_pmo = MarkedPatternMathObject.from_math_object(math_object)
        else:
            assert isinstance(math_object, MarkedPatternMathObject)
            marked_pmo = math_object
        return cls(latex_symbol=symbol,
                   tooltip=None,
                   patterns=marked_pmo,
                   menu=None,
                   shortcut=shortcut)

    @classmethod
    def from_pattern_nodes(cls, node):
        pass
        # TODO
        # patterns should be the list of all PatternNodes which are based on
        # node


class CalculatorPatternLines:
    """
    A class to store the logical data needed to build a group of buttons for
    the calculator.

    """

    bound_vars_title = _('Bound variables')
    context_title = _('Context')
    complex_tags = ('bound vars', 'definitions')

    # Dict of symbol / MarkedPMO
    marked_patterns = OrderedDict()
    for symbol, string in calculator_pattern_strings.items():
        marked_pmo = MarkedPatternMathObject.from_string(string, [])
        marked_patterns[symbol] = marked_pmo

    # # Special patterns
    # marked_patterns['()'] = parentheses_patterns() + [marked_patterns['()']]

    def __init__(self, title: str, lines: list, patterns=None,
                 tag=None):
        """
        Lines is a list of symbols which are keys for the cls.marked_patterns
        dict, which is updated with the optional patterns argument.
        """
        # FIXME: marked_patterns should be just patterns??
        #  turned into marked_patterns when inserted
        self.title = title
        self.lines = lines
        self.tag = tag
        if patterns:
            self.marked_patterns = patterns
            CalculatorPatternLines.marked_patterns.update(patterns)

    @classmethod
    def from_context(cls, context_math_objects: list[ContextMathObject]):
        patterns = dict()
        for obj in context_math_objects:
            symbol = obj.to_display(format_='html',
                                    use_color=True)
            marked_pmo = MarkedPatternMathObject.from_math_object(obj)
            patterns[symbol] = marked_pmo
        cpl = cls(title= cls.context_title,
                  lines=[list(patterns.keys())],
                  patterns=patterns,
                  tag="context")
        return cpl

    @classmethod
    def bound_vars(cls):
        title = cls.bound_vars_title
        cpl = cls(title=title, lines=[], tag='bound vars')
        return cpl

    @classmethod
    def constants_from_definitions(cls, only_numbers=False):
        """
        Create CalculatorPatternLines from the constants appearing in the
        definitions of the Lean file. A constant is selected only if it also
        appears in the PatternMathDisplay class list of constants.
        """

        # Max and abs already with numbers
        excluded_names = ('max', 'abs', 'limit_function')

        # Get all definitions from statements in Lean file
        csts_dict = DefinitionMathObject.get_constants()
        # Get patterns for those definitions
        MarkedPatternMathObject.populate_app_marked_patterns()
        patterns_dict = MarkedPatternMathObject.app_patterns

        # Cosmetic
        pretty_names = PatternMathDisplay.constants_pretty_names

        # Get nodes with some type indications
        definition_node_names = [node.node_name for node in
                                 DefinitionNode.calculator_nodes]
        cpls = []
        for section, constants in csts_dict.items():
            if constants:
                symbols, patterns = [], OrderedDict()
                for obj in constants:
                    name = obj.name
                    if name in patterns_dict and name not in excluded_names:
                        marked_pmo = patterns_dict[name]
                        symbol = pretty_names.get(name, name)
                        # Not twice in the same section:
                        if symbol not in symbols:
                            symbols.append(symbol)
                            patterns[symbol] = marked_pmo
                        if name in definition_node_names:
                            # Use definition_node_name to have more precise
                            # type indications
                            idx = definition_node_names.index(name)
                            node = DefinitionNode.calculator_nodes[idx]
                            marked_pmos = node.marked_pattern_math_objects()
                            patterns[symbol] = marked_pmos
                            if (only_numbers and
                                    all(mo.is_prop()
                                        for mo in marked_pmos)):
                                patterns.pop(symbol)
                                symbols.remove(symbol)

                # Slices of 4
                if symbols:
                    symbols = [symbols[4*idx:4*(idx+1)]
                               for idx in range(len(symbols) // 4 + 1)]
                    cpl = cls(title=section,
                              lines=symbols,
                              patterns=patterns,
                              tag="definitions")

                    cpls.append(cpl)

        return cpls

    def pattern_from_symbol(self, symbol):
        pattern = self.marked_patterns[symbol]
        return pattern


# calculator_group = CalculatorPatternLines(_('Calculator'),
#                                           [['7', '8', '9', '/'],
#                                            ['4', '5', '6', '*'],
#                                            ['1', '2', '3', '-'],
#                                            ['0', '.', '()', '+'],
#                                            ])
# sci_calc_group = CalculatorPatternLines(_('scientific calculator'),
#                                         [['sin', '()', ','],
#                                          # ['=', '<']
#                                          ])
# logic_group = CalculatorPatternLines(_('Logic'), [['∀', '⇒', '∧']])
# set_theory_group = CalculatorPatternLines(_('Set theory'), [['∩', '∪']])

