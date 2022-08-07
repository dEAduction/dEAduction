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

# from deaduction.pylib.config.i18n import _

# !! Latex commands should be alone in their strings,
# except for spaces around them, so that up to strip(), they appear in
# latex_to_utf8_dic

global _
# _ = lambda x: x  # FIXME: just for debugging:


# NB Some latex macro have a special treatment elsewhere, e.g.
# r'\not'
# r'\in' and all its variation (\in_quant, \in_prop,etc.)
# \text_is
# and so on


######################
######################
# LATEX dictionaries #
######################
######################
# Mind that values are tuples whose tuple elements indicate "descendant"
# (children of children). Otherwise use lists within main tuple.
# '\no_text' indicates that text mode should not be used in the current display
#   (e.g. within an equality)
latex_from_node = {
    "PROP_AND": (0, " " + _("and") + " ", 1),
    "PROP_OR": (0, " " + _("or") + " ", 1),
    "PROP_FALSE": (r"\false", ),  # Macro to be defined by LateX
    "PROP_IFF": (0, r" \Leftrightarrow ", 1),
    # NB: negation has a special treatment in recursive_display!
    "PROP_NOT": (r"\not", 0),  # Macro to be defined.
    # '\if' is just here for text mode:
    "PROP_IMPLIES": (r'\if', 0, r" \Rightarrow ", 1),
    # "∃ (H : P), Q" is treated as "P and Q",
    # and also handled by the 'AND' button
    "PROP_∃":  (0, " " + _("and") + " ", 1),
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
    "SET_DIFF_SYM": (0, r" \Delta ", 1),
    "SET_EMPTY": (r"\emptyset",),
    "SET_EXTENSION1": (r'\{', 0, r'\}'),
    "SET_EXTENSION2": (r'\{', 0, ', ', 1, r'\}'),
    "SET_EXTENSION3": (r'\{', 0, ', ', 1, ', ', 2, r'\}'),
    "SET_FAMILY": (0,  r" \to ", r'{\mathcal P}', r'\parentheses', 1),
    # "SET_IMAGE": (0, "(", 1, ")"),
    # "SET_INVERSE": (0, [r'^', '-1'], '(', 1, ')'),  # LEAVE the list as is!
    "SET_IMAGE": (0, r'\set_image', 1),
    "SET_INVERSE": (0, r'\set_inverse', 1),
    "SET_PRODUCT": (0, r'\times', 1),
    "COUPLE": (r'\parentheses', 0, ',', 1),
    "SET_INTENSION": (r"\no_text", r'\{', 1, r' \in ', 0, ' | ', 2, r'\}'),
    "SET_INTENSION_EXT": (r"\no_text", r'\{', 2, ' | ', 1, r' \in ', 0, r'\}'),
    # FIXME: instantiate set extensions
    ############
    # NUMBERS: #
    ############
    "COE": (0,),    # We do not want to see bindings
    "PROP_EQUAL": (r"\no_text", 0, r" \equal ", 1),  # influence text
    # conversion
    "PROP_EQUAL_NOT": (r"\no_text", 0, r" \neq ", 1),  # todo
    "PROP_<": (0, " < ", 1),
    "PROP_>": (0, " > ", 1),
    "PROP_≤": (0, r" \leq ", 1),
    "PROP_≥": (0, r" \geq ", 1),
    "DIFFERENCE": (0, " - ", 1),
    "SUM": (0, " + ", 1),
    "MULT": (0, r" \times ", 1),
    "PRODUCT": (0, r" \times ", 1),
    "DIV": (0, r"/", 1),
    "MINUS": ("-", 0),
    "POWER": (0, [r'\super', 1]),
    "SQRT": ('√', -1),
    ##################
    # GENERAL TYPES: #
    ##################
    # (r'{\mathcal P}', "(", 0, ")"),
    # "SET": (r'\set_of_subsets', [r"\parentheses", 0]),
    "SET": (r'\set_of_subsets', [r'\symbol_parentheses', 0]),
    "PROP": (r'\proposition',),
    "TYPE": (r'\set',),
    "FUNCTION": (r'\function_from', 0, r'\to', 1),  # (0, r" \to ", 1),
    "SEQUENCE": (r'\sequence_from', 0, r'\to', 1),  # (0, r" \to ", 1),
    "LOCAL_CONSTANT_EXPANDED_SEQUENCE":
        (r"(", 2, ')', ['_', 1, r"\in_symbol", 0]),
    # NB: children[2] is the whole body, "u_n"
    "LOCAL_CONSTANT_EXPANDED_SET_FAMILY":
        (r"\{", 2, ', ', 1, r"\in_symbol", 0, r"\}"),
    "LAMBDA_EXPANDED_SEQUENCE":
        (r"(", 2, ')', ['_', 1, r"\in_symbol", 0]),
    # NB: children[2] is the whole body, "u_n"
    "LAMBDA_EXPANDED_SET_FAMILY":
        (r"\{", 2, ', ', 1, r"\in_symbol", 0, r"\}")
    }

# \in_quant --> "belonging to", or "in" in text mode (but NOT "belongs to")
latex_from_quant_node = {
    "QUANT_∀": (r"\forall", 1, r" \in_quant ", 0, ", ", 2),
    "QUANT_∃": (r"\exists", 1, r" \in_quant ", 0, r'\such_that', 2),
    "PROP_∃": ("*PROP_∃*",),
    "QUANT_∃!": (r"\exists_unique", 1, r" \in_quant ", 0, r'\such_that', 2)
}

# Negative value = from end of children list
latex_from_constant_name = {
    "STANDARD_CONSTANT": (-1, r'\text_is', 0),
    # "STANDARD_CONSTANT_NOT": (-1, " " + _("is not") + " ", 0),  deprecated
    # NB: STANDARD_CONSTANT prevents supplementary arguments,
    # Do not use with a CONSTANT c s.t. APP(c, x) is a FUNCTION,
    # or anything that can be applied (i.e. in APP(APP(c,x),...) )
    "symmetric_difference": (-2, r'\Delta', -1),
    "composition": (4, r'\circ', 5),  # APP(compo, X, Y, Z, g, f)
    "prod": (1, r'\times', 2),
    "Identite": ("Id",),
    "ne": (2, r" \neq ", 3),  # Lean name for ≠
    "interval": (r"\[", -2, ",", -1, r"\]"),
    # FIXME: translate to english in Lean files
    "majorant": (-1, r'\text_is', " majorant de ", -2),
    "minorant": (-1, r'\text_is', " minorant de ", -2),
    "borne_sup": ("Sup ", -2, " = ", -1),
    "borne_inf": ("Inf ", -2, " = ", -1),
    "est_majore": (-1, r'\text_is', " majoré"),
    "est_minore": (-1, r'\text_is', " minoré"),
    "est_borne": (-1, r'\text_is', " borné"),
    "limit": ("lim ", -2, " = ", -1),
    "limit_plus_infinity": ("lim ", -1, " = +∞"),
    "abs": ('|', -1, '|'),
    "max": ("Max", r'\parentheses', -2, ",", -1),
    "inv": ([r'\parentheses', -1], [r'^', '-1']),
    "product": (-2, ".", -1),
    "identite": ("Id",),
    "image": (-1, " = ", -3, "(", -2, ")"),
    "relation_equivalence": (-1, " " + _("is an equivalence relation")),
    "classe_equivalence": (r"\[", -1, r"\]", ["_", 1]),
    "disjoint": (-2, " " + _("and") + " ", -1, " " + _("are disjoint")),
    "powerset": (r'\set_of_subsets', [r"\parentheses", -1]),
    "partition": (-1, " " + _("is a partition of") + " ", -2),
    "application": (-1, " " + _("is an application") + " "),
    "application_bijective":  (-1, " " + _("is a bijective application") + " "),
    "bounded_sequence": (-1,  r'\text_is', " " + _("bounded")),
    "RealSubGroup": (r"\real", ),
    "even":  (-1,  r'\text_is', " " + _("even"))
}


###################
###################
# UTF8 dictionary #
###################
###################
# Convert Latex command into utf8 symbols
latex_to_utf8_dic = {
    r"\equal": "=",
    r'\backslash': '\\',
    r'\Delta': '∆',
    r'\circ': '∘',
    r'\times': '×',
    r'\in': '∈',  # '∊'
    r'\in_quant': '∈',
    r"\in_symbol": '∈',
    r'\in_prop': ":",
    r'\in_set': ":",
    r'\in_function': ":",
    r'\Leftrightarrow': '⇔',
    r'\Rightarrow': '⇒',
    r'\forall': '∀',
    r'\exists': '∃',
    r'\exists_unique': '∃!',
    r'\subset': '⊂',
    r'\not\in': '∉',
    r'\cap': '∩',
    r'\cup': '∪',
    r'\bigcap': '⋂',
    r'\bigcup': '⋃',
    r'\emptyset': '∅',
    r'\to': '→',
    r'\neq': '≠',
    r'\leq': '≤',
    r'\geq': '≥',
    r'\set_of_subsets': '𝒫',
    r'\{': '{',
    r'\}': '}',
    r'\[': '[',
    r'\]': ']',
    r'\false': _("Contradiction"),
    r'\proposition': _("proposition"),
    r'\set': _("set"),
    r'\not': " " + _("not") + " ",
    r'\set_image': "",
    r'\set_inverse': [r'^', '-1'],
    r'\if': "",  # '\if' is just here for text mode
    r'\such_that': ", ",
    r'\context_function_from': "",  # To avoid double ":" for context_math_obj
    r'\function_from': ": ",
    r'\text_is': " ",  # " " + _("is") + " " ? Anyway 'is' will be removed?
    r'\text_is_not': " " + _('not') + " ",  # Idem
    r'\no_text': "",
    r'\symbol_parentheses': r'\parentheses',  # True parentheses for symbols
    r'\real': "ℝ"
}


#####################
#####################
# TEXT dictionaries #
#####################
#####################
latex_to_text = {
    r'\Leftrightarrow': " " + _("if and only if") + " ",
    r'\not': _("the negation of") + _(":") + " ",
    r'\if': _("if") + " ",
    r'\Rightarrow': _("then"),
    r'\set_of_subsets': _("the set of subsets of") + " ",
    r'\proposition': _("a proposition"),
    r'\set': _("a set"),
    r'\such_that': " " + _("such that") + " ",
    r'\forall': _("for every") + " ",
    r'\exists': _("there exists") + " ",
    r"\exists_unique": _("there exists a unique") + " ",
    r'\context_function_from': " " + _("a function from") + " ",
    r'\function_from': " " + _("a function from") + " ",
    r'\sequence_from': " " + _("a sequence from") + " ",  # FIXME...
    r'\to': " " + _("in") + " ",  # FIXME: OK in French but not in english!
    # r'\in': " " + _("belongs to") + " ",
    r'\in_prop': " " + _("is") + " ",
    r'\in_set': " " + _("is") + " ",
    r'\in_function': " " + _("is") + " ",  # FIXME: ???
    r'\in_quant': " " + _("in") + " ",
    r'\text_is': " " + _('is') + " ",
    r'\text_is_not': " " + _('is not') + " ",
    r'\symbol_parentheses': ""  # Parentheses but for symbols only
    # r'\subset': " " + _("is included in") + " " Does not help
}
plurals = {
    _('Let {} be {}'): _("Let {} be {} {}"),  # Translate plural!!
    _('a proposition'): _("propositions"),
    _('a set'): _("sets"),
    _('a subset'): _("subsets"),
    _('an element'): _("elements"),
    _('a function'): _("functions"),
    _('a sequence'): _("sequences"),
    _('a real number'): _("real numbers")
}

numbers = {
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

text_from_node = {
    # # "PROP_AND": (0, " " + _("and") + " ", 1),
    # # "PROP_OR": (0, " " + _("or") + " ", 1),
    # # "PROP_FALSE": (_("Contradiction"), ),
    # "PROP_IFF": (0, " " + _("if and only if") + " ", 1),
    # "PROP_NOT": (_("the negation of") + " ", 0),
    # "PROP_IMPLIES": (_("if") + " ", 0, " " + _("then") + " ", 1),
    ###############
    # SET THEORY: #
    ###############
    # "PROP_INCLUDED": (0, " " + _("is included in") + " ", 1),
    # "PROP_BELONGS": (0, " ∈ ", 1),  # This special case is processed in
                                    # the function display_belongs_to
    # "SET_INTER": (_("the intersection of") + " ", 0, " " + _("and") + " ",
    # 1),
    # "SET_UNION": (_("the union of") + " ", 0, " " + _("and") + " ", 1),
    # "SET_INTER+": (_("the intersection of the sets") + " ", 0),
    # "SET_UNION+": (_("the union of the sets") + " ", 0),
    # "SET_COMPLEMENT": (_("the complement of ") + " ", 0),
    # "SET_EMPTY": (_("the empty set"),),
    # "SET_FAMILY": (_("a family of subsets of") + " ", 1),
    # "SET_IMAGE": (_("the image under") + " ", 0, " " + _("of") + " ", 1),
    # "SET_INVERSE": (_("the inverse image under") + " ", 0, " " + _("of") +
    # " ", 1),
    ############
    # NUMBERS: #
    ############
    # "PROP_EQUAL": (0, " " + _("equals") + " ", 1),
    # "PROP_EQUAL_NOT": (0, " " + _("is different from") + " ", 1),
    # "PROP_<": (0, " " + _("is less than") + " ", 1),
    # "PROP_>": (0, " " + _("is greater than") + " ", 1),
    # "PROP_≤": (0, " " + _("is less than or equal to") + " ", 1),
    # "PROP_≥": (0, " " + _("is greater than or equal to") + " ", 1),
    ##################
    # GENERAL TYPES: #
    ##################
    # "SET": ("P(", 0, ")"),
    # "PROP": (_("a proposition"),),
    # "TYPE": (_("a set"),),
    # "FUNCTION": (_("a function from") + " ", 0, " " + _("to") + " ", 1),
}

text_from_all_nodes = {
    "PROP_AND": (0, " " + _("and") + " ", 1),
    "PROP_OR": (0, " " + _("or") + " ", 1),
    "PROP_FALSE": (_("Contradiction"), ),
    "PROP_IFF": (0, " " + _("if and only if") + " ", 1),
    "PROP_NOT": (_("the negation of") + " ", 0),
    "PROP_IMPLIES": (_("if") + " ", 0, " " + _("then") + " ", 1),
    ###############
    # SET THEORY: #
    ###############
    "PROP_INCLUDED": (0, " " + _("is included in") + " ", 1),
    "PROP_BELONGS": (0, " ∈ ", 1),  # This special case is processed in
                                    # the function display_belongs_to
    "SET_INTER": (_("the intersection of") + " ", 0, " " + _("and") + " ", 1),
    "SET_UNION": (_("the union of") + " ", 0, " " + _("and") + " ", 1),
    "SET_INTER+": (_("the intersection of the sets") + " ", 0),
    "SET_UNION+": (_("the union of the sets") + " ", 0),
    "SET_COMPLEMENT": (_("the complement of ") + " ", 0),
    "SET_EMPTY": (_("the empty set"),),
    "SET_FAMILY": (_("a family of subsets of") + " ", 1),
    "SET_IMAGE": (_("the image under") + " ", 0, " " + _("of") + " ", 1),
    "SET_INVERSE": (_("the inverse image under") + " ", 0, " " + _("of") + " ",
                    1),
    ############
    # NUMBERS: #
    ############
    "PROP_EQUAL": (0, " " + _("equals") + " ", 1),
    "PROP_EQUAL_NOT": (0, " " + _("is different from") + " ", 1),
    "PROP_<": (0, " " + _("is less than") + " ", 1),
    "PROP_>": (0, " " + _("is greater than") + " ", 1),
    "PROP_≤": (0, " " + _("is less than or equal to") + " ", 1),
    "PROP_≥": (0, " " + _("is greater than or equal to") + " ", 1),
    ##################
    # GENERAL TYPES: #
    ##################
    "SET": ("P(", 0, ")"),
    "PROP": (_("a proposition"),),
    "TYPE": (_("a set"),),
    "FUNCTION": (_("a function from") + " ", 0, " " + _("to") + " ", 1),
}

text_from_quant_node = {
    "QUANT_∀": (_("for every") + " ", 1, " " + _("in") + " ", 0,
                ", ", 2),
    "QUANT_∃": (_("there exists") + " ", 1, " " + _("in") + " ", 0,
                " " + _("such that") + " ", 2),
    "QUANT_∃!": (_("there exists a unique") + " ", 1, " " + _("in") + " ", 0,
                 " " + _("such that") + " ", 2),
    "PROP_∃": ("*PROP_∃*",)
}


###################
###################
# LEAN dictionary #
###################
###################
# Only those lean symbols that are distinct from the latex_to_utf8 dict
latex_to_lean_dic = {
    #'AND': 'and',
    #'OR': 'or',
    #'NOT': 'not',
    r'\Leftrightarrow': '↔',
    r'\Rightarrow': '→',
    r'\cap': '∩',
    r'\cup': '∪',
    r'\bigcap': '⋂',  # probably useless
    r'\bigcup': '⋃',
    r'\false': 'False',
    r'\proposition': 'Prop',
    r'\set': 'Type',
    "SET_FAMILY": (),  # FIXME: should be lean_name
    r'\set_image': " '' ",
    r'\set_inverse': " ⁻¹' ",
    r'\set_of_subsets': "set"
}


####################
# Couples of nodes #
####################
# In the following dic, the second node is assumed to be the first child node.
couples_of_nodes_to_text = {
    ("QUANT_∀", "SET"): (_("for every subset {} of {}, {}"),
                         (1, (0, 0), 2)),
    ("QUANT_∀", "PROP"): (_("for every proposition {}, {}"),
                          (1, 2)),
    ("QUANT_∀", "TYPE"): (_("for every set {}, {}"),
                          (1, 2)),
    ("QUANT_∀", "FUNCTION"): (_("for every function {} from {} to {}, {}"),
                          (1, (0, 0), (0, 1), 2)),
    ("QUANT_∀", "SEQUENCE"): (_("for every sequence {} in {}, {}"),
                              (1, (0, 1), 2)),
    ("QUANT_∃", "SET"): (_("there exists a subset {} of {} such that {}"),
                         (1, (0, 0), 2)),
    ("QUANT_∃", "PROP"): (_("there exists a proposition {} such that {}"),
                          (1, 2)),
    ("QUANT_∃", "TYPE"): (_("there exists a set {} such that {}"),
                          (1, 2)),
    ("QUANT_∃", "FUNCTION"): (_("there exists a function {} from {} to {} "
                                "such that {}"),
                              (1, (0, 0), (0, 1), 2)),
    ("QUANT_∃", "SEQUENCE"): (_("there exists a sequence {} in {} such that "
                                "{}"),
                              (1, (0, 1), 2)),
    ("QUANT_∃!", "SET"): (_("there exists a unique subset {} of {} such that "
                            "{}"),
                         (1, (0, 0), 2)),
    ("QUANT_∃!", "PROP"): (_("there exists a unique proposition {} such that "
                             "{}"), (1, 2)),
    ("QUANT_∃!", "TYPE"): (_("there exists a unique set {} such that {}"),
                           (1, 2)),
    ("QUANT_∃!", "FUNCTION"): (_("there exists a unique function {} from {} "
                                 "to {} such that {}"),
                               (1, (0, 0), (0, 1), 2)),
    ("QUANT_∃!", "SEQUENCE"): (_("there exists a unique sequence {} in {} "
                                 "such that {}"), (1, (0, 1), 2))
}

couples_of_nodes_to_latex = {
    ("QUANT_∀", "SET"): (r"\forall", 1, r" \subset ", (0, 0), ", ", 2),
    ("QUANT_∀", "PROP"): (r"\forall", 1, r'\proposition', ", ", 2),
    ("QUANT_∀", "TYPE"): (r"\forall", 1, r" \set", ", ", 2),
    ("QUANT_∀", "FUNCTION"): (r"\forall", 1, r" \function_from", (0, 0),
                              r'\to', (0, 1), ", ", 2),
    ("QUANT_∀", "SEQUENCE"): (r"\forall", 1, r" \function_from", (0, 0),
                              r'\to', (0, 1), ", ", 2),
    ("APPLICATION", "LOCAL_CONSTANT_EXPANDED_SEQUENCE"):
        ((0, 2, 0), ['_', 1]),
    ("APPLICATION", "LOCAL_CONSTANT_EXPANDED_SET_FAMILY"):
        ((0, 2, 0), ['_', 1]),
        ("APPLICATION", "LAMBDA_EXPANDED_SEQUENCE"):
        ((0, 2, 0), ['_', 1]),
    ("APPLICATION", "LAMBDA_EXPANDED_SET_FAMILY"):
        ((0, 2, 0), ['_', 1])
}
# Other quantifiers are treated automatically below
# ("QUANT_∃", "SET"): (r"\exists", 1, r" \subset ", (0, 0), ", ", 2),
# ("QUANT_∃", "PROP"): (r"\exists", 1, r'\proposition'),
# ("QUANT_∃", "TYPE"): (r"\exists", 1, r" \set"),
# ("QUANT_∃", "FUNCTION"): (r"\exists", 1, r" \function_from", (0, 0),
#                           r'\to', (0, 1)),
# ("QUANT_∃", "SEQUENCE"): (r"\exists", 1, r'\in', (0, 1)),


first_nodes_of_couples = {node for (node, _) in couples_of_nodes_to_text}

# Extend couples_of_nodes_to_latex with other quantifiers
supplementary_couples = {}
for quant_node, type_node in couples_of_nodes_to_latex:
    for new_quant_node, quant_macro in [("QUANT_∃", r'\exists'),
                                        ("QUANT_∃!", r'\exists_unique')]:
        new_key = new_quant_node, type_node
        old_value = couples_of_nodes_to_latex[(quant_node, type_node)]
        new_value = (quant_macro,) + old_value[1:]
        supplementary_couples[new_key] = new_value
couples_of_nodes_to_latex.update(supplementary_couples)

# Dic of first nodes: e.g. dic_of_first_nodes["QUANT_∀"] = ["SET", "PROP",...]}
dic_of_first_nodes_text = {node: [] for node, _ in couples_of_nodes_to_text}
for (first_node, second_node) in couples_of_nodes_to_text:
    dic_of_first_nodes_text[first_node].append(second_node)

dic_of_first_nodes_latex = {node: [] for node, _ in couples_of_nodes_to_latex}
for (first_node, second_node) in couples_of_nodes_to_latex:
    dic_of_first_nodes_latex[first_node].append(second_node)

####################
####################
# Helper functions #
####################
####################
# Nodes of math objects that need instantiation of bound variables
HAVE_BOUND_VARS = ("QUANT_∀", "QUANT_∃", "QUANT_∃!", "SET_INTENSION",
                   "LAMBDA", "EXTENDED_SEQUENCE", "EXTENDED_SET_FAMILY")

# TO_BE_EXPANDED = ("SEQUENCE", "SET_FAMILY", "LAMBDA")

INEQUALITIES = ("PROP_<", "PROP_>", "PROP_≤", "PROP_≥", "PROP_EQUAL_NOT")

NATURE_LEAVES_LIST = ("PROP", "TYPE", "SET_UNIVERSE", "SET", "ELEMENT",
                      "FUNCTION", "SEQUENCE", "SET_FAMILY",
                      "TYPE_NUMBER", "NUMBER", "VAR", "SET_EMPTY",
                      "CONSTANT", "LOCAL_CONSTANT", "NONE")


def needs_paren(parent, child, child_number, text_depth=0) -> bool:
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
    if c_node == 'COE':  # Act as if COE node was replaced by its child
        c_node = child.children[0].node
    if p_node == 'COE':  # Should be treated at the previous level, see above
        return False
    if (p_node in ("SET_IMAGE", "SET_INVERSE")
            and child_number == 1):  # f(A), f^{-1}(A)
        return True
    elif c_node in NATURE_LEAVES_LIST:
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
    elif p_node == "APPLICATION" and child_number == 1 and child.children:
        return True
    elif c_node == "APPLICATION":
        return False
    elif p_node in ("SET_IMAGE",  "SET",
                    "SET_UNION+", "SET_INTER+", "APPLICATION",
                    "SET_INTENSION",
                    "PROP_INCLUDED",  "PROP_BELONGS", "PROP_NOT_BELONGS",
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


def latex_to_utf8(string: Union[str, list]):
    """
    Convert a string or a list of string from latex to utf8.
    """
    if isinstance(string, list) or isinstance(string, tuple):
        return [latex_to_utf8(item) for item in string]
    elif isinstance(string, str):
        striped_string = string.strip()  # Remove spaces
        if striped_string in latex_to_utf8_dic:
            utf8_string = latex_to_utf8_dic[striped_string]
            if isinstance(utf8_string, str):
                utf8_string = string.replace(striped_string, utf8_string)
            else:
                utf8_string = list(utf8_string)
            return utf8_string
        else:
            return string
    else:
        return string


def latex_to_lean(string: Union[str, list]):
    """
    Convert a string or a list of string from latex to Lean.
    Warning, this has not really been tested.
    (Used only in logic.py.)
    """
    # Fixme: this should also handles lambda expression
    #  (including sequences, set families, and so on)
    if isinstance(string, list):
        return [latex_to_lean(item) for item in string]
    elif isinstance(string, str):
        striped_string = string.strip()  # Remove spaces
        if striped_string in latex_to_lean_dic:
            lean_string = latex_to_lean_dic[striped_string]
            if isinstance(lean_string, str):
                utf8_string = string.replace(striped_string, lean_string)
            return lean_string
        elif striped_string in latex_to_utf8_dic:
            utf8_string = latex_to_utf8_dic[striped_string]
            if isinstance(utf8_string, str):
                utf8_string = string.replace(striped_string, utf8_string)
            return utf8_string
        else:
            return string
    else:
        return string


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
    And also f(x) ; x+1/2 ; 2*n, max m n, abs x...
""") + "\n \n" + \
_("In case of error, try with more parentheses.")
