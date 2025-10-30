"""
##########################################################################
# nodes.py : provide the Nodes class #
##########################################################################

    This file provides the Node class. For now, instances of this class are
    used to create CalculatorButtons.
    TODO: use this as nodes for MathObjects,
        instead of strings, and use them for display.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 11 2020 (creation)
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

from typing import Union
from deaduction.pylib.math_display import MathDisplay

global _

if __name__ == "__main__":
    def _(s):
        return s


class Node:
    """
    Instances of this class are used to create CalculatorButtons.

    The node_pattern attribute is turned into a PatternMathObject under the
    from_string method. It provides in particular the number of children
    (and their type, if known).
    The latex_shape is used for displaying the button, via its main symbol.

    WARNING: do not forget that every NODE needs its children, including types.
    e.g. write
        'APPLICATION: ?3()(?0: FUNCTION(?2, ?3), ?1: ?2)'
    and NOT
        'APPLICATION: ?3(?0: FUNCTION(?2, ?3), ?1: ?2)'.
    """

    calculator_nodes = []
    _name = ""
    # sub-class so that name is registered for translation:
    __name_for_translation = ""

    # Access to utility classes, to be set somewhere else:
    PatternMathObject = None
    MarkedPatternMathObject = None

    _button_symbol = None
    _button_tooltip = None
    _button_menu = None

    _pattern_math_objects = None
    _marked_pattern_math_objects = None

    def __init__(self, node_name, node_patterns: Union[str, list],
                 latex_shape, text_shape=None, lean_shape=None,
                 display_in_calculator=True):

        self._node_name = node_name
        self.shortcut = None

        # Populate self._node_patterns
        self._node_patterns: [str] = []
        if isinstance(node_patterns, str):
            node_patterns = [node_patterns]

        for node_pattern_str in node_patterns:
            # if node_pattern_str.startswith('('):
            #     # No type indication
            #     node_pattern = node_name + node_pattern_str
            # elif not node_pattern_str.startswith(node_name):
            #     node_pattern = node_name + " :" + node_pattern_str
            # else:
            #   node_pattern = node_pattern_str
            self._node_patterns.append(node_pattern_str)

        self._latex_shape = latex_shape
        self._text_shape = text_shape
        self._lean_shape = lean_shape

        if display_in_calculator:
            self.__class__.calculator_nodes.append(self)

    @classmethod
    def name(cls):
        """
        Translate self._name on the fly.
        """
        return _(cls._name)

    @classmethod
    def all_nodes_names(cls):
        names = [node.name for node in cls.calculator_nodes]
        return names

    def set_button_symbol(self, symbol):
        self._button_symbol = symbol

    def set_button_tooltip(self, tooltip: str):
        self._button_tooltip = tooltip

    def set_button_menu(self, menu_items: [str]):
        self._button_menu = menu_items

    def set_shortcut(self, shortcut):
        self.shortcut = shortcut

    @property
    def node_name(self):
        return self._node_name

    @property
    def node_patterns(self):
        return self._node_patterns

    def latex_shape(self, math_object=None):
        return self._latex_shape

    def text_shape(self, math_object=None):
        if self._text_shape:
            return self._text_shape
        else:
            # Fixme: apply latex_to_text?
            return self.latex_shape(math_object)

    def lean_shape(self, math_object=None):
        if self._lean_shape:
            return self._lean_shape
        else:
            return self.latex_shape(math_object)

    def priority_test(self):
        pass

    def need_parentheses(self, other):
        pass

    def nb_children(self, math_object=None):
        children_nbs = (item for item in self.latex_shape(math_object)
                        if isinstance(item, int))
        return max(children_nbs)

    def pattern_math_objects(self):
        """
        Return the PMOs computed from self.node_patterns.
        """

        if not self._pattern_math_objects:
            # if len(self._pattern_math_objects) == 2:
            #     print("toto")
            self._pattern_math_objects = \
                [self.PatternMathObject.from_string(pattern_str)
                 for pattern_str in self.node_patterns]
        return self._pattern_math_objects

    def marked_pattern_math_objects(self):
        """
        Return the PMO computed from self.node_type.
        To be overridden in the PMO module.
        """
        if not self._marked_pattern_math_objects:
            self._marked_pattern_math_objects = \
                [self.MarkedPatternMathObject.from_string(pattern_str)
                 for pattern_str in self.node_patterns]
        return self._marked_pattern_math_objects

    def main_symbol(self) -> (int, str):
        """
        Return the main symbol of the node, e.g.
        'PROP_AND'  --> r'\and'.
        The main symbol is the str item that startswith '&&' if any,
        or the first item that startswith '\'.
        """

        shape = self.latex_shape()

        return MathDisplay.main_symbol_from_shape(shape)

        # (1) First try
        symbol = None
        latex_symbol = None
        ms_symbol = None
        counter = 0
        for item in shape:
            if not isinstance(item, str):
                pass
            elif item.startswith(r'\ms'):
                ms_symbol = item[3:]
                ms_idx = counter
            elif (not latex_symbol
                  and item != r"\no_text"
                  and item.strip().startswith('\\')):
                latex_symbol = item
                latex_idx = counter
            else:
                symbol = item
                idx = counter
            counter += 1

        if ms_symbol:
            return ms_idx, ms_symbol
        elif latex_symbol:
            return latex_idx, latex_symbol
        elif symbol:
            return idx, symbol
        else:
            return len(shape)-1, None

    def latex_symbol(self) -> str:
        return self.main_symbol()[1]

    def button_symbol(self) -> str:
        """
        Text that should appear on the Calculator button corresponding to node.
        By default, this is the main_symbol computed from latex_shape.
        """
        if self._button_symbol:
            return self._button_symbol
        else:
            symbol = MathDisplay.latex_to_utf8(self.latex_symbol())
            return symbol

    def button_tooltip(self) -> str:
        """
        Text to serve as a tooltip on the Calculator button corresponding to
        node. By default, this is the (last) pattern of the node.
        """
        if self._button_tooltip:
            return self._button_tooltip
        else:  # Take display and replace spaces
            pattern = self.pattern_math_objects()[-1]
            self._button_tooltip = pattern.to_display(format_='utf8')
            return self._button_tooltip

    def button_menu(self):
        return self._button_menu


class LogicalNode(Node):
    _name = "Logic"
    __name_for_translation = _("Logic")
    calculator_nodes = []


forall = LogicalNode(
    "QUANT_∀",
    ['QUANT_∀: PROP()'
     '(?0: *TYPE, LOCAL_CONSTANT/name=?.BoundVar: ?0, ?2: PROP)',
     'QUANT_∀: PROP()'
     '(?0: *TYPE, LOCAL_CONSTANT/name=?.BoundVar: ?0, '
     'PROP_IMPLIES(PROP_>(BV, ?2), ?3: PROP))',
     'QUANT_∀: PROP()'
     '(?0: *TYPE, LOCAL_CONSTANT/name=?.BoundVar: ?0, '
     'PROP_IMPLIES(PROP_≥(BV, ?2), ?3: PROP))',],
    (r"\forall", 1, r" \in_quant ", 0, ", ", 2))

forall.set_button_tooltip('∀ a ∈ ?, ?')
forall.set_shortcut(r'\forall')

exists = LogicalNode(
    "QUANT_∃",
    ['QUANT_∃: PROP()(?0: *TYPE, '
     'LOCAL_CONSTANT/name=?.BoundVar: ?0, ?2: PROP)',
     'QUANT_∃: PROP()'
     '(?0: *TYPE, LOCAL_CONSTANT/name=?.BoundVar: ?0, '
     'PROP_IMPLIES(PROP_>(BV, ?2), ?3: PROP))',
     'QUANT_∃: PROP()'
     '(?0: *TYPE, LOCAL_CONSTANT/name=?.BoundVar: ?0, '
     'PROP_IMPLIES(PROP_≥(BV, ?2), ?3: PROP))',
     ],
    (r"\exists", 1, r" \in_quant ", 0, r'\such_that', 2))
exists.set_button_tooltip('∃ a ∈ ?, ?')
exists.set_shortcut(r'\exists')


# "QUANT_∃!": (r"\exists_unique", 1, r" \in_quant ", 0, r'\such_that', 2)

implies = LogicalNode("PROP_IMPLIES",
                      'PROP_IMPLIES: PROP()(?0: PROP, ?1: PROP)',
                      (r'\if', 0, r"\ms\Rightarrow ", 1)
                      )
and_ = LogicalNode('PROP_AND',
                   'PROP_AND: PROP()(?0: PROP, ?1: PROP)',
                   (0, r"\and", 1)
                   )
or_ = LogicalNode('PROP_OR',
                  'PROP_OR: PROP()(?0: PROP, ?1: PROP)',
                  (0, r"\or", 1)
                  )
not_ = LogicalNode("PROP_NOT",
                   'PROP_NOT: PROP()(?0:PROP)',
                   (r"\not", 0)
                   )
iff = LogicalNode("PROP_IFF",
                  'PROP_IFF: PROP()(?0: PROP, ?1: PROP)',
                  (0, r" \Leftrightarrow ", 1)
                  )
equal = LogicalNode("PROP_EQUAL",
                    'PROP_EQUAL: PROP()(?0: ?2, ?1: ?2)',
                    (r"\no_text", 0, r" \equal ", 1)
                    )

# "PROP_EQUAL_NOT": (r"\no_text", 0, r" \neq ", 1),  # todo
# "PROP_FALSE": (r"\false",)


class SetTheoryNode(Node):
    _name = "Set Theory"
    __name_for_translation = _("Set Theory")
    calculator_nodes = []


belongs = SetTheoryNode("PROP_BELONGS",
                        'PROP_BELONGS: PROP()(?0: ?2, ?1: SET(?2))',
                        (0, r" \in ", 1))
included = SetTheoryNode("PROP_INCLUDED",
                         'PROP_INCLUDED: PROP()(?0: SET(?2), ?1: SET(?2))',
                         (0, r" \subset ", 1))
# not_belongs = SetTheoryNode("PROP_NOT_BELONGS",
#                             'PROP()(?0: ?2, ?1: SET(?2))',
#                             (0, r" \not\in ", 1))
inter = SetTheoryNode("SET_INTER",
                      'SET_INTER: SET(?2)(?0: SET(?2), ?1: SET(?2))',
                      (0, r" \cap ", 1))
union = SetTheoryNode("SET_UNION",
                      'SET_UNION: SET(?2)(?0: SET(?2), ?1: SET(?2))',
                      (0, r" \cup ", 1))
diff = SetTheoryNode("SET_DIFF",
                     'SET_DIFF: SET(?2)(?0: SET(?2), ?1: SET(?2))',
                     (0, r" \backslash ", 1))
diff.set_shortcut(r'\diff')
empty = SetTheoryNode("SET_EMPTY",
                      'SET_EMPTY()',
                      (r"\emptyset",)
                      )
singleton = SetTheoryNode("SET_EXTENSION1",
                          'SET_EXTENSION1: SET(?1)(?0: ?1)',
                          (r'\{', 0, r'\}')
                          )
singleton.set_button_symbol('{·}')
singleton.set_button_tooltip(_("A singleton (set with one element)"))

pair = SetTheoryNode("SET_EXTENSION2",
                     'SET_EXTENSION2: SET(?2)(?0: ?2, ?1: ?2)',
                     (r'\{', 0, ', ', 1, r'\}')
                     )
pair.set_button_symbol('{·,·}')
pair.set_button_tooltip(_("A pair (set with two elements"))

# "SET_EXTENSION3": (r'\{', 0, ', ', 1, ', ', 2, r'\}'),

set_image = SetTheoryNode("SET_IMAGE",
                          'SET_IMAGE: SET(?3)(?0: FUNCTION(?2, ?3), ?1: SET(?2))',
                          (0, r'\set_image', r'\parentheses', 1)
                          )
set_image.set_button_symbol("f({·})")
set_image.set_button_tooltip(_("The image of a subset under a function"))
set_inverse = SetTheoryNode("SET_INVERSE",
                            'SET_INVERSE: SET(?2)(?0: FUNCTION(?2, ?3), ?1: SET(?3))',
                            (0, r'\set_inverse', r'\parentheses', 1)
                            )
set_inverse.set_button_symbol("f⁻¹({·})")
set_inverse.set_button_tooltip(_("The inverse image of a subset under a "
                                 "function"))

subsets = SetTheoryNode("SUBSETS",
                        "SET: TYPE()(?0: *TYPE)",
                        (r'\set_of_subsets', [r'\symbol_parentheses', 0]))
subsets.set_button_symbol("𝒫(·)")
subsets.set_button_tooltip(_("The set of subsets of a set."))


functions = SetTheoryNode('FUNCTIONS',
                          'FUNCTION: TYPE()(?0:TYPE, ?1:TYPE)',
                          (0, r'\to', 1))
functions.set_button_tooltip(_("A set of functions"))

# "SET": (r'\set_of_subsets', [r'\symbol_parentheses', 0]),
# "PROP": (r'\proposition',),
# "TYPE": (r'\set',),
# "SET_INDEX": (r'\set',),
# "FUNCTION": (r'\function_from', 0, r'\to', 1),  # (0, r" \to ", 1),
# "SET_PRODUCT(?0, ?1)": (r'\type_element', (0,), r'\times', (1,)),
# "SET_INTER+": (r"\bigcap", 0),  # !! big ⋂
# "SET_UNION+": (r"\bigcup", 0),
# "SET_DIFF": (0, r" \backslash ", 1),
# "SET_COMPLEMENT": (0, r" \backslash ", 1),
# "SET_DIFF_SYM": (0, r" \Delta ", 1),
# "SET_UNIVERSE": (0,),
# "SET_FAMILY": (
#     0, r" \to ", r'\set_of_subsets', r'\parentheses', 1),  # Fixme ms
# # "SET_IMAGE": (0, "(", 1, ")"),
# # "SET_INVERSE": (0, [r'^', '-1'], '(', 1, ')'),  # LEAVE the list as is!
# "SET_PRODUCT": (0, r'\times', 1),
# "COUPLE": (r'\parentheses', 0, ',', 1),
# "SET_INTENSION": (
#     r"\no_text", r'\{', 1, r' \in ', 0, ' | ', 2, r'\}'),
# "SET_INTENSION_EXT": (
#     r"\no_text", r'\{', 2, ' | ', 1, r' \in ', 0, r'\}'),
# symbol = '{|}': 'SET_INTENSION(?0: TYPE, ?1, ?2: PROP)'


class FunctionNode(Node):
    """
    Class to store a few basic nodes related to functions: application of a
    function to an argument (or a sequence to an index), composition,
    définition of a function.
    """
    _name = "Functions"
    __name_for_translation = _("Functions")
    calculator_nodes = []
    application = None  # Set below

# NB: 'APPLICATION' is a special pattern
application_node = FunctionNode("APPLICATION",
                            # "GENERIC_APPLICATION",
                            # 'APPLICATION: ?3()(?0: FUNCTION(?2, ?3), ?1: ?2)',
                            # 'APPLICATION(?0, ?1)',
                            ['APPLICATION: ?3()(?0: !FUNCTION(?2, ?3), '
                                '?1: ?2)',
                             'APPLICATION: ?3()(?0: !SEQUENCE(CONSTANT/name=ℕ, '
                             '?3), ?1: CONSTANT/name=ℕ)'
                             ],
                            (0, "\\parentheses", 1))

application_node.set_button_symbol("f(·)")
application_node.set_button_tooltip(_("Application of a function to an element\\n"
                                 "or term of a sequence."))
application_node.set_button_menu(["f(x)", "u_n"])
application_node.set_shortcut("APP")

FunctionNode.application = application_node

composition = FunctionNode("COMPOSITION",
                            "COMPOSITION: FUNCTION(?1, ?3)"
                            "(?4: FUNCTION(?2, ?3), ?5: FUNCTION(?1, ?2))",
                            (4, r'\circ', 5)
                            )
composition.set_button_tooltip(_("Composition of two functions"))

mapsto = FunctionNode("LAMBDA",
                     "LAMBDA: FUNCTION(?0, ?2)(?0,"
                     "LOCAL_CONSTANT/name=?.BoundVar: ?0, ?3: ?2)",
                     (1, r'\in', 0, r"\mapsto", 3)
                     )
mapsto.set_button_symbol("↦")
mapsto.set_button_tooltip(_("Define a function"))
mapsto.set_shortcut("\mapsto")


class NumberNode(Node):
    """
    Class to store number and operators nodes. We give up *NUMBER_TYPES.
    """
    _name = "Numbers"
    __name_for_translation = _("Numbers")
    calculator_nodes = []
    parentheses = None  # Set below


Naturals = NumberNode('ℕ',
                      "CONSTANT/name=ℕ: TYPE",
                      (r'\type_N',))
Integers = NumberNode('ℤ',
                      "CONSTANT/name=ℤ: TYPE",
                      (r'\type_Z',))
Rationals = NumberNode('ℚ',
                       "CONSTANT/name=ℚ: TYPE",
                       (r'\type_Q',))
Reals = NumberNode('ℝ',
                   "CONSTANT/name=ℝ: TYPE",
                   (r'\type_R',))
Naturals.set_shortcut('\\N')
Integers.set_shortcut('\\Z')
Rationals.set_shortcut('\\Q')
Reals.set_shortcut('\\R')

Naturals.set_button_symbol('ℕ')
Integers.set_button_symbol('ℤ')
Rationals.set_button_symbol('ℚ')
Reals.set_button_symbol('ℝ')


def instantiate_nb_node(i: int):
    node = NumberNode(f'NUMBER',
                      f'NUMBER/value={i}: *NUMBER_TYPES',
                      (str(i), ))


for i in [7, 8, 9]:
    instantiate_nb_node(i)


# NB: I do not type operands since they coulld be numbers but also functions,
# sequences, and so on.
div_ = NumberNode('DIV',
                  'DIV: ?2()(?0: ?2, ?1: ?2)',
                  (0, "/", 1)
                  )

for i in [4, 5, 6]:
    instantiate_nb_node(i)

mult_ = NumberNode('MULT',
                   'MULT: ?2()(?0: ?2, ?1: ?2)',
                   (0, r"\times", 1)
                   )

for i in [1, 2, 3]:
    instantiate_nb_node(i)

diff = NumberNode('DIFFERENCE',
                  ['MINUS: ?1()(?0: ?1)',
                      'DIFFERENCE: ?2()(?0: ?2, ?1: ?2)'],
                  (0, "-", 1)
                  )
diff.set_button_tooltip(_("-? or ?-?"))

# sqrt = NumberNode('SQRT',
#                   '*NUMBER_TYPES()(?0: *NUMBER_TYPES)',
#                   ("√", 0)
#                   )

instantiate_nb_node(0)

# point = NumberNode('POINT',
#                    'POINT()',
#                    ('.', )
#                    )

point = NumberNode(f'NUMBER',
                   f"NUMBER/value=.: *NUMBER_TYPES",
                   ('.',))

# NB: 'APPLICATION' is a special pattern
parentheses = NumberNode('GENERIC_PARENTHESES',
                         'GENERIC_PARENTHESES: ?0()(?0)',
                         # ['GENERIC_APPLICATION',
                         #  'GENERIC_PARENTHESES: ?0()(?0)'],
                         ('(', 0, ')')
                         )
parentheses.set_button_symbol("()")

NumberNode.parentheses = parentheses

sum_ = NumberNode('SUM',
                  # 'SUM: ?2: *HAS_ADD()()(?0: ?2, ?1: ?2)',
                  'SUM: ?2()(?0: ?2, ?1: ?2)',
                  (0, "+", 1)
                  )

power = NumberNode('POWER',
                   'POWER: ?2()(?0: ?2=*NUMBER_TYPES, ?1: *INT_OR_NAT)',
                   (0, "^", 1)
                   )

abs_ = NumberNode('abs',
                      'APP(CONSTANT/name=abs, ?0: *NUMBER_TYPES)',
                      ('|', -1, '|'))
abs_.set_button_symbol('|·|')
abs_.set_button_tooltip(_("Absolute value"))
abs_.set_shortcut('\\abs')

max_ = NumberNode('max',
                      'APP(CONSTANT/name=max, ?0: ?2=*NUMBER_TYPES, ?1: ?2=*NUMBER_TYPES)',
                      ('max ', '\\parentheses', -2, ', ', -1))

min_ = NumberNode('min',
                      'APP(CONSTANT/name=min, ?0: ?2=*NUMBER_TYPES, ?1: ?2=*NUMBER_TYPES)',
                      ('min ', '\\parentheses', -2, ', ', -1))


class InequalityNode(Node):
    _name = "Inequalities"
    __name_for_translation = _("Inequalities")
    calculator_nodes = []


lt = InequalityNode("PROP_<",
                    'PROP_<: PROP()(?0: ?2=*NUMBER_TYPES, ?1: ?2=*NUMBER_TYPES)',
                    (0, " < ", 1)
                    )
lt.set_button_symbol('&#60;')  # Html code

leq = InequalityNode("PROP_≤",
                     'PROP_≤: PROP()(?0: ?2=*NUMBER_TYPES, ?1: ?2)',
                     (0, " ≤ ", 1)
                     )


gt = InequalityNode("PROP_>",
                    'PROP_>: PROP()(?0: ?2=*NUMBER_TYPES, ?1: ?2=*NUMBER_TYPES)',
                    (0, " > ", 1)
                    )


geq = InequalityNode("PROP_≥",
                     'PROP_≥: PROP()(?0: ?2=*NUMBER_TYPES, ?1: ?2=*NUMBER_TYPES)',
                     (0, " ≥ ", 1)
                     )

# "PROP_EQUAL_NOT": (r"\no_text", 0, r" \neq ", 1),  # todo
equal_not = InequalityNode("PROP_EQUAL_NOT",
                           'PROP_EQUAL_NOT: PROP()(?0: ?2, ?1: ?2)',
                           (r"\no_text", 0, r" \neq ", 1))

equal2 = InequalityNode("PROP_EQUAL",
                        'PROP_EQUAL: PROP()(?0: ?2, ?1: ?2)',
                        (r"\no_text", 0, r" \equal ", 1))


class DefinitionNode(Node):
    """
    A class for definition nodes, to specify the patterns.
    """
    _name = "Definitions"
    __name_for_translation = _("Definitions")
    calculator_nodes = []


even = DefinitionNode('even',
                      'APP: PROP()(CONSTANT/name=even, ?0: *NUMBER_TYPES)',
                      (-1, '\text_is', _('even')))
odd = DefinitionNode('odd',
                      'APP: PROP()(CONSTANT/name=odd, ?0: *NUMBER_TYPES)',
                      (-1, '\text_is', _('even')))
divides = DefinitionNode('divides',
                      'APP: PROP()(CONSTANT/name=divides, ?0: *NUMBER_TYPES, '
                      '?1: *NUMBER_TYPES)',
                      (-2, ' ' + _('divides') + ' ', -1))
prime = DefinitionNode('prime',
                      'APP: PROP()(CONSTANT/name=prime, ?0: *NUMBER_TYPES)',
                      (-1, '\text_is', _('prime')))


class SpecialNode(Node):
    """
     "COE": (0,),  # We do not want to see bindings
         "METAVAR": ('?',),
         "POINT": (0, '.', 1),
         "COMMA": (0, ', ', 1),
         "GENERIC_PARENTHESES": ('(', 0, ')'),
         "OPEN_PARENTHESIS": ('(', 0),
         "CLOSE_PARENTHESIS": (0, ')'),
         "GENERIC_NODE": (0, '¿', 1),
         "COMPOSITE_NUMBER": (0, 1),
         "LOCAL_CONSTANT": ('self.local_constant_shape',),
         # "APPLICATION": (0, '\\parentheses', 1),
         "LAMBDA": (1, "\\mapsto", 2),
         "CONSTANT": (display_name,),
    """


class TypeNode(Node):
    """
         "SET": (r'\set_of_subsets', [r'\symbol_parentheses', 0]),
         "PROP": (r'\proposition',),
         "TYPE": (r'\set',),
         "SET_INDEX": (r'\set',),
         "FUNCTION": (r'\function_from', 0, r'\to', 1),  # (0, r" \to ", 1),
         "SEQUENCE": (r'\sequence_in', 1),  # (0, r" \to ", 1),
         "NUMBER": (display_value,),
    """


# class TextNode(Node):
#     """
#     This subclass is for use only to display text.
#     """
#
#     pass


class PatternNode(Node):

    ##########################
    # Bounded quantification #
    ##########################
    @classmethod
    def forall_in(cls):
        return cls("QUANT_∀",
                   "QUANT_∀: PROP()(?0, ?1, PROP_IMPLIES(PROP_BELONGS(?1, ?2), ?3))",
                   (r"\forall", (2, 0), ", ", (2, 1)))

    ##########################
    # Special quantification #
    ##########################
    @classmethod
    def forall_prop(cls):
        return cls("QUANT_∀",
                   "QUANT_∀: PROP()(PROP, ?0: PROP, ?1: PROP)",
                   (r"\forall", (1,), r'\proposition', ", ", (2,)))

    @classmethod
    def forall_subset(cls):
        return cls("QUANT_∀",
                   "QUANT_∀: PROP()(SET(...), ?0, ?1)",
                   (r"\forall", (1,), r" \subset ", (0, 0), ", ", (2,)),
                   (_("for every subset") + " ", (1,), _(" of "), (0, 0), ", ", 1))


class LeanPatternNode(PatternNode):
    """
    This subclass is used only for displaying Lean code.

        "QUANT_∀(?0, LOCAL_CONSTANT/binder_info=implicit, ?2)":
        (r"\forall", '{', (1,), ": ", (0,), '}', ", ", (2,)),
    "QUANT_∀(?0, LOCAL_CONSTANT/binder_info=strict_implicit, ?2)":
        (r"\forall", '⦃', (1,), ": ", (0,), '⦄', ", ", (2,)),
    # type class instance between brackets:
    "QUANT_∀(?0, LOCAL_CONSTANT/binder_info=inst_implicit, ?2)":
        (r"\forall", '[', (1, ), ": ", (0, ), ']', ", ", (2, )),
    "CONSTANT/name=_inst_1": ('_inst_1',),
    "CONSTANT/name=_inst_2": ('_inst_2',),
    """


