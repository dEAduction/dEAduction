"""
##########################################################################
# display_data.py : data for displaying MathObject, used by display_math #
##########################################################################

    This file provides dictionaries for converting MathObjects into strings.
    Here only strings, and dic/lists/tuples/sets of strings are manipulated.
    Processing on MathObjects take place in the companion file display_math.

    It also provides several functions, like the function needs_paren.

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

# !! Latex commands should be alone in their strings,
# except for spaces around them, so that up to strip(), they appear in
# latex_to_utf8_dic

global _

if __name__ == "__main__":
    def _(s):
        return s

# _ = lambda x: x  # Just for debugging:


# NB Some latex macro have a special treatment elsewhere, e.g.
# r'\not'
# r'\in' and all its variation (\in_quant, \in_prop,etc.)
# \text_is
# and so on

def lean_application(mo):
    """
    Return Lean shape for APPLICATION(0, 1, 2, ...)
    -> [0, " ", 1, " ", ...]
    """

    # FIXME: take the "non @" form for constants registered in app_pattern_data.
    li = []
    for i in range(len(mo.children)):
        li.extend([i, " "])
    return li


def display_name(mo):
    return mo.display_name


def raw_display_name(mo):
    return mo.info.get('name', 'no_name')


def display_value(mo):
    return mo.info.get('value')


def math_type_for_lean(mo):
    if not mo.math_type.is_no_math_type():
        return [': ', mo.math_type]


def display_lean_value(mo):
    type_ = mo.math_type
    val = display_value(mo)
    if type_.is_no_math_type:
        return val
    else:
        return '(' + val + ': ' + type_.to_display(format_='lean') + ')'

# def lean_inst_name(mo):
#     return '[' + name(mo) + ']'


def local_constant_shape(mo):
    return mo.local_constant_shape


######################
######################
# LATEX dictionaries #
######################
######################

class MathDisplay:
    """
    A class with no instance, to store data and methods for displaying
    MathObjects. Most attributes are dict.

    Some dicts have an update method, that allows the translation to be
    up-to-date.

    Mind that values are tuples whose tuple elements indicate "descendant"
    (children of children). Otherwise, use lists within main tuple.
    '\no_text' indicates that text mode should not be used in the current display
    (e.g. within an equality)
    """

    latex_to_text = dict()
    plurals = dict()
    every = dict()
    numbers = dict()
    standard_latex_to_utf8 = dict()
    latex_to_utf8_dic = dict()

    # Tags to mark the position just before and just after a marked node:
    marked_tag = r'\marked'
    cursor_tag = r'\DeadCursor'
    # Set to True if the cursor position should be markd by the cursor tag:
    mark_cursor = False
    # cursor_pos = None

    # TODO: compléter !!
    invisible_macros = [r'\no_text', r'\variable', r'\marked']

    latex_from_node = \
        {"PROP_AND": (0, r"\and", 1),
         "PROP_OR": (0, r"\or", 1),
         "PROP_FALSE": (r"\false",),  # Macro to be defined by LateX
         "PROP_IFF": (0, r" \Leftrightarrow ", 1),
         # NB: negation has a special treatment in recursive_display!
         "PROP_NOT": (r"\not", 0),  # Macro to be defined.
         # '\if' is just here for text mode:
         "PROP_IMPLIES": (r'\if', 0, r" \Rightarrow ", 1),  # Fixme main symb
         # "∃ (H : P), Q" is treated as "P and Q",
         # and also handled by the 'AND' button
         "PROP_∃": (0, r"\and", 1),
         ###############
         # SET THEORY: #
         ###############
         "PROP_INCLUDED": (0, r" \subset ", 1),
         "PROP_BELONGS": (0, r" \in ", 1),
         "PROP_NOT_BELONGS": (0, r" \not\in ", 1),
         "SET_INTER": (0, r" \cap ", 1),  # !! small ∩
         "SET_UNION": (0, r" \cup ", 1),  #
         "SET_INTER+": (r"\bigcap", 0),  # !! big ⋂
         "SET_UNION+": (r"\bigcup", 0),
         "SET_DIFF": (0, r" \backslash ", 1),
         "SET_COMPLEMENT": (0, r" \backslash ", 1),
         "SET_DIFF_SYM": (0, r" \Delta ", 1),
         "SET_UNIVERSE": (0,),  # Fixme add empty strings?
         "SET_EMPTY": (r"\emptyset",),
         "SET_EXTENSION1": (r'\{', 0, r'\}'),
         "SET_EXTENSION2": (r'\{', 0, ', ', 1, r'\}'),
         "SET_EXTENSION3": (r'\{', 0, ', ', 1, ', ', 2, r'\}'),
         "SET_FAMILY": (
             0, r" \to ", r'\set_of_subsets', r'\parentheses', 1),  # Fixme ms
         # "SET_IMAGE": (0, "(", 1, ")"),
         # "SET_INVERSE": (0, [r'^', '-1'], '(', 1, ')'),  # LEAVE the list as is!
         "SET_IMAGE": (0, r'\set_image', r'\parentheses', 1),
         "SET_INVERSE": (0, r'\set_inverse', r'\parentheses', 1),
         "SET_PRODUCT": (0, r'\times', 1),
         "COUPLE": (r'\parentheses', 0, ',', 1),
         "SET_INTENSION": (
             r"\no_text", r'\{', 1, r' \in ', 0, ' | ', 2, r'\}'),
         "SET_INTENSION_EXT": (
             r"\no_text", r'\{', 2, ' | ', 1, r' \in ', 0, r'\}'),
         # FIXME: instantiate set extensions
         ############
         # NUMBERS: #
         ############
         "COE": (0,),  # We do not want to see bindings
         "PROP_EQUAL": (r"\no_text", 0, r" \equal ", 1),  # influence text
         # conversion
         "PROP_EQUAL_NOT": (r"\no_text", 0, r" \neq ", 1),  # todo
         "PROP_<": (0, " < ", 1),  # Fixme ms: <>+-*....
         "PROP_>": (0, " > ", 1),
         "PROP_≤": (0, r" \leq ", 1),
         "PROP_≥": (0, r" \geq ", 1),
         "DIFFERENCE": (0, " - ", 1),
         "SUM": (0, " + ", 1),
         "MULT": (0, r" \mul ", 1),
         "PRODUCT": (0, r" \times ", 1),
         "DIV": (0, r"/", 1),
         "MINUS": ("-", 0),
         "POWER": (0, [r'\super', 1]),  # FIXME: remove list??
         "SQRT": ('√', -1),
         ##################
         # GENERAL TYPES: #
         ##################
         "COMPOSITION": (0, r'\circ', 1),
         "SET": (r'\set_of_subsets', [r'\symbol_parentheses', 0]),
         "PROP": (r'\proposition',),
         "TYPE": (r'\set',),
         "SET_INDEX": (r'\set',),
         "FUNCTION": (r'\function_from', 0, r'\to', 1),  # (0, r" \to ", 1),
         "SEQUENCE": (r'\sequence_in', 1),  # (0, r" \to ", 1),
         "CONSTANT": (display_name,),
         "NUMBER": (display_value,),
         "LOCAL_CONSTANT": ('self.local_constant_shape',),
         "APPLICATION": (0, r'\parentheses', 1),
         "LAMBDA": (1, r"\mapsto", 2),
         "METAVAR": ('?',),
         "POINT": (0, '.', 1),
         "COMMA": (0, ', ', 1),
         "GENERIC_PARENTHESES": ('(', 0, ')'),
         "OPEN_PARENTHESIS": ('(', 0),
         "CLOSE_PARENTHESIS": (0, ')'),
         "GENERIC_NODE": (0, '¿', 1),
         # "COMPOSITE_NUMBER": (0, 1),
         # "CURSOR": ('_', ),
         # "CLOSED_PARENTHESIS": (0,)
         }

    #####################
    #####################
    # LEAN dictionaries #
    #####################
    #####################
    # Only those shape that are distinct from the latex_from_node dict
    lean_from_node = {
        "LOCAL_CONSTANT": (display_name,),
        "CONSTANT": ("@", display_name),  # e.g. @composition
        "QUANT_∀": (r"\forall", 1, ": ", 0, ", ", 2),
        "QUANT_∃": (r"\exists", 1, ": ", 0, ", ", 2),
        "QUANT_∃!": (r"\exists_unique", 1, r": ", 0, r', ', 2),
        # Types:
        "FUNCTION": (0, r'\to', 1),
        "SEQUENCE": (0, r"\to", 1),
        "LAMBDA": ("λ ", '(', 1, ': ', 0, '), ', 2),
        "SET": ('set ', 0),
        "SET_UNIVERSE": ('(', 'univ', ': ', 'set ', 0, ')'),
        "SET_INDEX": ('index_set',),
        "APPLICATION": (lean_application,),
        # Prevent pattern NOT(APP(CONSTANT(...)) -> is not:
        "PROP_NOT": (r'\not', 0),
        "SET_EMPTY": ('(', r'\emptyset', math_type_for_lean, ')'),  # including ':'
        "SET_UNION+": ("set.Union", "(", 0, ")"),
        "SET_INTER+": ("set.Inter", "(", 0, ")"),
        "SET_COMPLEMENT": ('set.compl', ' ', '(', 1, ')'),
        # Type indication for numbers, otherwise '-1' --> 'has_neg nat ??'
        "NUMBER": (display_lean_value, ),
        "RAW_LEAN_CODE": (display_name, ),
        'COMPOSITION': ('(', 0, r'\circ', 1, ')'),
    }

    # Only those lean symbols that are distinct from the latex_to_utf8 dict
    latex_to_lean_dic = {
        r'\and': " " + "and" + " ",
        r'\or': " " + "or" + " ",
        r'\Leftrightarrow': '↔',
        r'\Rightarrow': '→',
        r'\subset': '⊆',
        r'\cap': '∩',
        r'\cup': '∪',
        r'\bigcap': '⋂',  # probably useless
        r'\bigcup': '⋃',
        r'\false': 'false',
        r'\proposition': 'Prop',
        r'\set': 'Type',
        r'\set_image': " '' ",
        r'\set_inverse': " ⁻¹' ",
        r'\set_of_subsets': "set ",
        r'\if': "",
        r'\such_that': "",
        'ℕ': "nat",
        'ℤ': "int",
        'ℚ': "rat",
        'ℝ': "real",
        r'\type_N': 'nat',
        r'\type_Z': 'int',
        r'\type_Q': "rat",
        r'\type_R': 'real',
        ''
        r'used_property': "",
        r'\not': "not ",
        r'\times': "×",
        r'\mul': "*"
    }

    @classmethod
    def update_latex_node(cls):
        # \in_quant --> "belonging to", or "in" in text mode
        # (but NOT "belongs to")
        latex_from_quant_node = {
            "QUANT_∀": (r"\forall", 1, r" \in_quant ", 0, ", ", 2),
            "QUANT_∃": (r"\exists", 1, r" \in_quant ", 0, r'\such_that', 2),
            # "PROP_∃": ("*PROP_∃*",),
            "QUANT_∃!": (r"\exists_unique", 1, r" \in_quant ", 0, r'\such_that', 2)
            }

        cls.latex_from_node.update(latex_from_quant_node)

    @classmethod
    def update_latex_to_utf8(cls):
        """
        Convert Latex command into utf8 symbols.
        """

        cls.standard_latex_to_utf8 = {
            r'\circ': '∘',
            r'\times': '×',
            r'\mul': '×',
            r'\power': "^",
            r'\in': '∈',  # '∊'
            r'\Leftrightarrow': '⇔',
            r'\Rightarrow': '⇒',
            r'\forall': '∀',
            r'\exists': '∃',
            r'\exists_unique': '∃!',
            r'\subset': _('⊆'),  # ⊂ for French students
            r'\not\in': '∉',
            r'\cap': '∩',
            r'\cup': '∪',
            r'\bigcap': '⋂',
            r'\bigcup': '⋃',
            r'\emptyset': '∅',
            r'\to': '→',
            r'\mapsto': '↦',
            r'\neq': '≠',
            r'\leq': '≤',
            r'\geq': '≥',
            r'\set_inverse': ['^', '-1'],
        }

        cls.latex_to_utf8_dic = {
            # r'\and': " " + _("and") + " ",
            # r'\or': " " + _("or") + " ",
            r"\ms": "",
            r"\equal": "=",
            r'\backslash': '\\',
            r'\Delta': '∆',
            r'\in_quant': '∈',
            r"\in_symbol": '∈',
            r'\in_prop': ":",
            r'\in_set': ":",
            r'\in_function': ":",
            r'\set_of_subsets': '𝒫',
            r'\{': '{',
            r'\}': '}',
            r'\[': '[',
            r'\]': ']',
            r'\false': _("Contradiction"),
            r'\proposition': _("proposition"),
            r'\set': _("set"),
            r'\metric_space': _('metric space'),
            r'\not': " " + _("not") + " ",
            r'\set_image': "",
            r'\if': "",  # '\if' is just here for text mode
            r'\such_that': ", ",
            r'\context_function_from': "",
            # To avoid double ":" for context_math_obj
            r'\function_from': ": ",
            r'\text_is': " ",
            # " " + _("is") + " " ? Anyway 'is' will be removed?
            r'\text_is_not': " " + _('not') + " ",  # Idem
            r'\no_text': "",
            # r'\text': "",
            r'\symbol_parentheses': r'\parentheses',
            # True parentheses for symbols
            r'\real': "ℝ",
            #########
            # TYPES #
            #########
            # Used for display in math mode (not text mode)
            r'\type_subset': _("subset of") + " ",
            r'\type_sequence': _("sequence in") + " ",
            r'\type_family_subset': _("family of subsets of") + " ",
            r'\type_element': _("element of") + " ",
            r'\type_point': _("point of") + " ",
            r'\type_N': _('non-negative integer'),
            r'\type_Z': _('integer'),
            r'\type_Q': _('rational number'),
            r'\type_R': _('real number')
        }

        cls.latex_to_utf8_dic.update(cls.standard_latex_to_utf8)

    #####################
    #####################
    # TEXT dictionaries #
    #####################
    #####################
    @classmethod
    def update_text_dict(cls):
        cls.latex_to_text = {
            r'\and': " " + _("and") + " ",
            r'\or': " " + _("or") + " ",
            r'\Leftrightarrow': " " + _("if and only if") + " ",
            r'\not': _("the negation of") + _(":") + " ",
            r'\if': _("if") + " ",
            r'\Rightarrow': _("then"),
            r'\set_of_subsets': _("the set of subsets of") + " ",
            r'\proposition': _("a proposition"),
            r'\set': _("a set"),
            r'\metric_space': _('a metric space'),
            r'\such_that': " " + _("such that") + " ",

            r'\forall': _("for every") + " ",
            r"\forall {} \subset {}, {}": _("for every subset {} of {}, {}"),
            r"\forall {}  \function_from {} \to {}, {}":
                _("for every function {} from {} to {}, {}"),
            r"\forall {} \proposition, {}": _("for every proposition {}, {}"),
            # r"\forall {} \set{} {}": _("for every set {}{} {}"),

            r'\exists': _("there exists") + " ",
            r"\exists {} \subset {}, {}": _(
                "there exists a subset {} of {} such that {}"),
            r"\exists {}  \function_from {} \to ""{}, {}": _(
                "there exists a function {"
                "} from {} to {} such that {}"),
            r"\exists {} \proposition, {}": _(
                "there exists a proposition {} such that {}"),
            r"\exists {} \set, {}": _("there exists a set {} such that {}"),

            r"\exists_unique": _("there exists a unique") + " ",
            r"\exists_unique {} \subset {}, {}": _(
                "there exists a unique subset {} of {} such that {}"),
            r"\exists_unique {}  \function_from {} \to {}, {}": _(
                "there exists a unique function {} from {} to {} such that {}"),
            r"\exists_unique {} \proposition, {}": _(
                "there exists a unique proposition {} such that {}"),
            r"\exists_unique {} \set, {}": _(
                "there exists a unique set {} such that {}"),

            # TODO: add sentences with sequence
            r'\context_function_from': " " + _("a function from") + " ",
            r'\function_from': " " + _("a function from") + " ",
            r'\sequence_in': " " + _("a sequence in") + " ",  # FIXME...
            r'\to': " " + _("in") + " ",  # FIXME: OK in French but not in english!
            # r'\in': " " + _("belongs to") + " ",
            r'\in_prop': " " + _("is") + " ",
            r'\in_set': " " + _("is") + " ",
            r'\in_function': " " + _("is") + " ",  # FIXME: ???
            r'\in_quant': " " + _("in") + " ",
            r'\text_is': " " + _('is') + " ",
            r'\text_is_not': " " + _('is not') + " ",
            r'\symbol_parentheses': "",  # Parentheses but for symbols only
            r'\type_subset': _("a subset of") + " ",
            r'\type_sequence': _("a sequence in") + " ",
            r'\type_family_subset': _("a family of subsets of") + " ",
            r'\type_element': _("an element of") + " ",
            r'\type_point': _("a point of") + " ",
            r'\type_N': _('a non-negative integer'),
            r'\type_Z': _('an integer'),
            r'\type_Q': _('a rational number'),
            r'\type_R': _('a real number')
        }

        cls.numbers = {
            1: _("one"),
            2: _("two"),
            3: _("three"),
            4: _("four"),
            5: _("five"),
            6: _("six"),
            7: _("seven"),
            8: _("eight"),
            9: _("nine"),
            10: _("ten")
        }

    @classmethod
    def update_plurals(cls):
        """
        Update the plural dictionary, useful if language changes.
        """
        cls.plurals = {
            _('Let {} be {}'): _("Let {} be {} {}"),  # Translate plural!!
            _('a proposition'): _("propositions"),
            _('a set'): _("sets"),
            _('a subset'): _("subsets"),
            _('an element'): _("elements"),
            _('a function'): _("functions"),
            _('a sequence'): _("sequences"),
            _('a non-negative integer'): _('non-negative integers'),
            _('an integer'): _("integers"),
            _('a rational number'): _("rational numbers"),
            _('a real number'): _("real numbers")
        }

        # For substitution in types, and translation
        cls.every = {
            _('a proposition'): _("every proposition"),
            _('a set'): _("every set"),
            _('a subset'): _("every subset"),
            _('an element'): _("every element"),
            _('a function'): _("every function"),
            _('a sequence'): _("every sequence"),
            _('a non-negative integer'): _('every non-negative integer'),
            _('an integer'): _("every integer"),
            _('a rational number'): _("every rational number"),
            _('a real number'): _("every real number")
        }

    @classmethod
    def update_dict(cls):
        cls.update_latex_node()
        cls.update_latex_to_utf8()
        cls.update_text_dict()
        cls.update_plurals()

    @classmethod
    def single_to_every(cls, an_object: str) -> str:
        """
        Replace "an object", e.g. "an element", by "every object", e.g. "every
        element".
        """
        for key, value in cls.every.items():
            if an_object.find(key) != -1:
                every_object = an_object.replace(key, value)
                return every_object

    @classmethod
    def plural_types(cls, type_, utf8_type=None):
        """
        Return type_ where the first word in utf8_type of the plurals dict have been
        replaced by its plural.
        """

        plural_type = None
        if not utf8_type:
            utf8_type = type_
        # Keep only nonempty words:
        words = [word for word in utf8_type.split(" ") if word]
        for counter in range(len(words)):
            first_words = " ".join(words[:counter + 1])
            # cls.update_plurals()
            if first_words in cls.plurals:
                plural_first_words = cls.plurals[first_words]
                plural_type = type_.replace(first_words, plural_first_words)
                # new_words = [plural_first_words] + words[counter+1:]
                # plural_type = " ".join(new_words)
                break
        return plural_type


####################
####################
# Helper functions #
####################
####################
    NATURE_LEAVES_LIST = ("PROP", "TYPE", "SET_UNIVERSE", "SET", "ELEMENT",
                          "FUNCTION", "SEQUENCE", "SET_FAMILY",
                          "TYPE_NUMBER", "NUMBER", "VAR", "SET_EMPTY",
                          "CONSTANT", "LOCAL_CONSTANT", "NONE", "METAVAR")

    # needs_paren_couples = [('MULT', 'SUM')]
    # dont_need_paren_couples = [('SUM', 'MULT'), ()]

    priorities = [{'NUMBER'},
                  {'POINT'},  # FIXME: DECIMAL?
                  {'COMPOSITION'},
                  {'APPLICATION'},
                  {'MINUS'},
                  {'MULT', 'DIV'},
                  {'SUM', 'DIFFERENCE'},
                  {'PROP_EQUAL', 'PROP_<', 'PROP_>', 'PROP_≤', 'PROP_≥'},
                  # {'CLOSE_PARENTHESIS', 'OPEN_PARENTHESIS'}
                  ]

    @classmethod
    def priority(cls, self: str, other: str) -> str:
        """
        Return '=' if self and other have the same priority level,
        '>' or '<' if they have distinct comparable priority levels,
        None otherwise.
        """

        if not self or not other:
            return None
        self_found = False
        other_found = False
        for nodes in cls.priorities:
            if self in nodes:
                if other_found:
                    return '<'
                if other in nodes:
                    return '='
                else:
                    self_found = True
            elif other in nodes:
                if self_found:
                    return '>'
                else:
                    other_found = True

    @classmethod
    def priority_test(cls, child_node, parent_node, child_number):
        """
        return True is self can be a left/right child of parent
        (left iff left_children=True), with no parentheses.
        """
        if not cls.priority(parent_node, child_node):
            return None
        if child_number == 0:
            # self can be a left child of parent?
            test = (cls.priority(parent_node, child_node) != '>')
        else:
            # self can be a right child of parent?
            test = (cls.priority(parent_node, child_node) not in ('=', '>'))
        return test

    @classmethod
    def needs_paren(cls, parent, child, child_number) -> bool:
        """
        Decides if parentheses are needed around the child
        e.g. if math_obj.node = PROP.IFF then
        needs_paren(math_obj, children[i], i)
        will be set to True for i = 0, 1 so that the display will be
        ( ... ) <=> ( ... )

        :param parent:          MathObject
        :param child:           MathObject
        :param child_number:    an integer or a list indicating the line_of_descent
        :return:                bool
        """

        # TODO : tenir compte de la profondeur des parenthèses,
        #   et utiliser Biggl( biggl( Bigl( bigl( (x) bigr) Bigr) biggr) Biggr)

        p_node = parent.node
        c_node = child.node if child is not None else "NONE"

        # Priority operator rules
        test = cls.priority_test(c_node, p_node, child_number)
        if test is not None:
            return not test

        if p_node in ('PARENTHESES', 'CLOSE_PARENTHESIS', 'OPEN_PARENTHESIS',
                      'GENERIC_PARENTHESES'):
            return False
        if c_node in ('PARENTHESES', 'CLOSE_PARENTHESIS', 'OPEN_PARENTHESIS',
                      'GENERIC_PARENTHESES'):
            return False
        if c_node == 'COE':  # Act as if COE node was replaced by its child
            c_node = child.children[0].node
        if p_node == 'COE':  # Should be treated at the previous level, see above
            return False
        if (p_node in ("SET_IMAGE", "SET_INVERSE")
                and child_number == 1):  # f(A), f^{-1}(A)
            return True
        elif c_node in cls.NATURE_LEAVES_LIST:
            return False
        elif p_node == 'PROP_NOT':
            return True
        elif c_node in ("SET_IMAGE", "SET_INVERSE", "PROP_BELONGS", "PROP_EQUAL",
                        "PROP_EQUAL_NOT", "PROP_≤", "PROP_≥", "PROP_<", "PROP_>",
                        "PROP_INCLUDED", "SET_UNION+", "SET_INTER+",
                        "SET_INTENSION", "SET_EXTENSION1", "SET_EXTENSION2",
                        "SET_EXTENSION3"):
            return False
        elif (p_node == "SET_INVERSE"
              and child_number == 0
              and c_node != "LOCAL_CONSTANT"):
            # e.g. (f∘g)^{-1} (x)
            return True
        # Fixme: Does not work?:
        elif p_node == "APPLICATION" and child.children:  # and child_number == -1
            return True
        elif c_node == "APPLICATION":
            return False
        elif p_node in ("SET_IMAGE", "SET",
                        "SET_UNION+", "SET_INTER+", "APPLICATION",
                        "SET_INTENSION",
                        "PROP_INCLUDED", "PROP_BELONGS", "PROP_NOT_BELONGS",
                        "LAMBDA",
                        "PROP_EQUAL", "PROP_EQUAL_NOT",
                        "PROP_≤", "PROP_≥", "PROP_<", "PROP_>"):
            return False
        elif p_node.startswith("QUANT"):
            # for tuple as child_number, cf the descendant MathObject method
            if child_number in (0, 1, (0,), (1,), (2, 0)):
                # No parentheses around the variable, the type, or the leading
                # inequality
                return False
            elif c_node.startswith("QUANT"):
                return False
        return True

    @classmethod
    def latex_to_utf8(cls, string: str):
        """
        Convert a string or a list of string from latex to utf8.
        """
        # FIXME: this should be used only for strings.

        utf8_string = None

        # if isinstance(string, list):
        #     return string.recursive_map(cls.latex_to_utf8)
        # if isinstance(string, list) or isinstance(string, tuple):
        #     return [cls.latex_to_utf8(item) for item in string]
        # elif isinstance(string, str):
        striped_string = string.strip()  # Remove spaces
        if striped_string in cls.latex_to_utf8_dic:
            utf8_string = cls.latex_to_utf8_dic[striped_string]
        elif striped_string in cls.latex_to_text:  # Useful for and,
            # \typeElement...
            utf8_string = cls.latex_to_text[striped_string]
        if utf8_string is not None:
            if isinstance(utf8_string, str):
                utf8_string = string.replace(striped_string, utf8_string)
            else:
                utf8_string = list(utf8_string)

        return utf8_string if utf8_string is not None else string

    @classmethod
    def latex_to_lean(cls, string: str):
        """
        Convert a string or a list of string from latex to Lean.
        Warning, this has not really been tested.
        (Used only in logic.py.)
        """

        # FIXME: this should be used only for strings.

        # if isinstance(string, list):
        #     return [cls.latex_to_lean(item) for item in string]
        # elif isinstance(string, str):
        striped_string = string.strip()  # Remove spaces
        if striped_string in cls.latex_to_lean_dic:
            lean_string = cls.latex_to_lean_dic[striped_string]
            if isinstance(lean_string, str):
                lean_string = string.replace(striped_string, lean_string)
            return lean_string
        elif striped_string in cls.latex_to_utf8_dic:
            utf8_string = cls.latex_to_utf8_dic[striped_string]
            if isinstance(utf8_string, str):
                utf8_string = string.replace(striped_string, utf8_string)
            return utf8_string
        else:
            return string
        # else:
        #     return string

    # @staticmethod
    # def wrap_lean_shape_with_type(mo, lean_shape):
    #     """
    #     Add type indication for Lean shape, if this is pertinent.
    #     Return a new tuple shape.
    #     """
    #
    #     # lean_shape = list(lean_shape)
    #
    #     if mo.node == 'NUMBER' and (mo.math_type.is_number()
    #                                 or mo.math_type.node == '*NUMBER_TYPES'):
    #         lean_type = mo.math_type.to_display(format_='lean')
    #         wrap_shape = ['(', '('] + lean_shape + [') : ', lean_type, ')']
    #         return wrap_shape
    #     else:
    #         return lean_shape

    @staticmethod
    def main_symbol_from_shape(shape) -> (int, str):
        """
        Return the main symbol of the node, e.g.
        'PROP_AND'  --> r'\and'.
        The main symbol is the str item that startswith '&&' if any,
        or the first item that startswith '\'.
        """

        # (1) First try
        symbol = None
        counter = 0
        for item in shape:
            if not isinstance(item, str):
                pass
            elif item.startswith(r'\ms'):
                symbol = item[3:]
            elif ((not symbol) and item not in MathDisplay.invisible_macros
                  and item != '\\parentheses'
                  and item.strip().startswith('\\')):
                symbol = item
            counter += 1

        if symbol:
            return counter, symbol

        # (2) Second try: symbol is first str
        counter = 0
        for symbol in shape:
            if isinstance(symbol, str) and symbol not in MathDisplay.invisible_macros:
                return counter, symbol
            counter += 1

        return len(shape)-1, None

    @classmethod
    def main_symbol_from_node(cls, node) -> (int, str):
        """
        Return the main symbol of the node, e.g.
        'PROP_AND'  --> r'\and'.
        The main symbol is the str item that startswith '&&' if any,
        or the first item that startswith '\'.
        """

        shape = cls.latex_from_node.get(node)
        if not shape:
            return

        return cls.main_symbol_from_shape(shape)

    @classmethod
    def remove_macros_from_shape(cls, shape):
        """
        Return shape without macros.
        """

        shape2 = [item for item in shape
                  if not (isinstance(item, str) and item in cls.invisible_macros)]
        return shape2

    @staticmethod
    def flat_shape(shape: [], add_close_parentheses=False) -> []:
        """
        Turn shape into a flat list, whose items are not lists.
        If add_close_parentheses is True, then 'close_parentheses' is added
        at the right places, to match '\\parentheses' items. This is useful
        to get the right shape length (in conjunction with mark_cursor).

        Return a list whose items are not lists.
        """

        flat_s = []
        close_paren = False
        for item in shape:
            if item == '\\parentheses':
                close_paren = True
                flat_s.append('(')
            elif isinstance(item, list):
                flat_s.extend(MathDisplay.flat_shape(item))
            else:
                flat_s.append(item)

        if close_paren and add_close_parentheses:
            flat_s.append(')')

        return flat_s

    @classmethod
    def ordered_children(cls, shape) -> list:
        """
        Return the list of children or descendants nbs corresponding to shape,
        with string items replaced by None. This method looks into item
        that are lists.
        """

        children = []
        flat_shape = MathDisplay.flat_shape(shape, add_close_parentheses=True)
        shape2 = cls.remove_macros_from_shape(flat_shape)
        for item in shape2:
            if isinstance(item, int) or isinstance(item, tuple):
                children.append(item)
            else:
                children.append(None)

        return children

    # @classmethod
    # def marked_latex_shape(cls, latex_shape, cursor_pos):
    #     if cursor_pos is None:
    #         idx, main_symbol = cls.main_symbol_from_shape(latex_shape)
    #     else:
    #         idx = cursor_pos
    #     m_latex_shape = list(latex_shape)
    #
    #     if not cls.mark_cursor:
    #         m_latex_shape = [r'\marked'] + m_latex_shape
    #         idx += 1
    #     else:
    #         flat_s = MathDisplay.flat_shape(latex_shape,
    #                                         add_close_parentheses=True)
    #         m_latex_shape = cls.remove_macros_from_shape(flat_s)
    #         m_latex_shape.insert(idx+1, cls.cursor_tag)
    #     return m_latex_shape


# def insert_str_in_shape_at_pos(string: str, shape: [], idx: int):
#     counter = 0
#     for item in shape:
#         pass


# Init MathDIsplay dictionaries
MathDisplay.update_dict()


new_properties = _("Examples of syntax:") + "\n" + \
                 _("""
    x ∈ A ∩ B          --> x belongs (A cap B)
    A ⊂ B               --> A subset B
    A = ∅               --> A = emptyset
    ∀x ∈ A ∩ A', x ∈ A   --> forall x belongs (A cap A'), x belongs A """) + \
                 "\n \n" + \
                 _("You can use the keywords and, or, not, implies, iff, forall, exists.") + \
                 "\n" + _("In case of error, try with more parentheses.")

new_objects = _("Examples of syntax:") + "\n \n" + \
              _("""
    A ∩ B           --> A cap B
    A ∪ B           --> A cup B
    X \\ A          --> complement A
    f(A)            --> f direct_image A
    f⁻¹(A)          --> f inverse_image A
    f∘g (x)         --> (composition f g)(x)
    {x}             --> sing x
    {x, x'}         --> pair x x'
    And also f(x) ; x+1/2 ; 2*n, max m n, abs x, epsilon...
""") + "\n \n" + \
              _("In case of error, try with more parentheses.")


# if __name__ == '__main__':
#     l, r = MathDisplay.left_right_children('QUANT_∀')
#     print(MathDisplay.main_symbol_from_node('QUANT_∀'))
#     print(l, r)
#     l, r = MathDisplay.left_right_children('PROP_AND')
#     print(MathDisplay.main_symbol_from_node('PROP_AND'))
#     print(l, r)
#     l, r = MathDisplay.left_right_children('SUM')
#     print(MathDisplay.main_symbol_from_node('SUM'))
#     print(l, r)
#
#     print(MathDisplay.main_symbol_from_node("MULT"))