"""
###############################################################################
# pattern_data.py : data for creating PatternMathObject as helper for display #
###############################################################################

This modules produces dictionaries for pattern matching, that are used by the
new_display module:
    latex_from_pattern_string,
    latex_from_pattern_string_for_type
The keys are strings, and the values are PatternMathObjects.
The strings are converted to Tree instances by the pattern_parser module.
Then the Tree instances are converted to PatternMO by the PMO.from_tree
class method.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 11 2022 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2022 the d∃∀duction team

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

# TODO: integrate
#  - couple_of_node_to_latex / to_text
#  - latex_from_constant_name (and translate to english)

import logging

from deaduction.pylib.math_display.display_data import name, value
from deaduction.pylib.math_display.pattern_parser import tree_from_str
from deaduction.pylib.pattern_math_obj import PatternMathObject

log = logging.getLogger(__name__)

global _
# _ = lambda x: x  # Just for debugging:


# BEWARE: do not use negative number in pattern strings!
# info may be provided within nodes, e.g. "CONSTANT/name=toto".
# Use "?" as a joker, e.g. "CONSTANT/name=?".
# In the shape values, tuples point for children (generalized or not),
# other int point to metavars.
# "global" in first position in shape means that variables will be  inserted at
# "{}". This is used for text conversion and translation.

###############
# QUANTIFIERS #
###############

quant_pattern = {
    # NB: QUANT nodes must have 3 children, with children[1] the bound var.
    # Thus "QUANT_∀(SET(...), ...) does not work.
    # !! Macro must be alone in their string (up to spaces) after splitting
    # We use child nbs and not metavars to indicate P(x), since this is used
    # for good parenthesing
    "QUANT_∀(SET(...), ?0, ?1)":      (r"\forall", 0, r" \subset ", (0, 0), ", ", (2, )),
    "QUANT_∀(FUNCTION(...), ?0, ?1)": (r"\forall", 0, r" \function_from", (0, 0), r'\to', (0, 1), ", ", (2, )),
    "QUANT_∀(PROP, ?0, ?1)":          (r"\forall", 0, r'\proposition', ", ", (2, )),
    "QUANT_∀(TYPE(...), ?0, ?1)":     (r"\forall", 0, r" \set", ", ", (2, )),
    # FIXME: this is odd!!! :
    # ("QUANT_∀", "SEQUENCE"): (r"\forall", 1, r" \function_from", (0, 0),
    #                           r'\to', (0, 1), ", ", 2),
}

# Exists pattern #
additional_quant_pattern = {}
forall_node = "QUANT_∀"
forall_macro = r"\forall"
for pattern, shape in quant_pattern.items():
    for new_node, quant_macro in [("QUANT_∃", r'\exists'),
                                  ("QUANT_∃!", r'\exists_unique')]:
        new_key = pattern.replace(forall_node, new_node)
        new_value = ((shape[0].replace(forall_macro, quant_macro), )
                     + shape[1:])
        additional_quant_pattern[new_key] = new_value
quant_pattern.update(additional_quant_pattern)


latex_from_pattern_string = {
    # TODO: refactor seq and set families
    # ("APPLICATION", "LOCAL_CONSTANT_EXPANDED_SEQUENCE"):
    #     ((0, 2, 0), ['_', 1]),
    # ("APPLICATION", "LOCAL_CONSTANT_EXPANDED_SET_FAMILY"):
    #     ((0, 2, 0), ['_', 1]),
    # ("APPLICATION", "LAMBDA_EXPANDED_SEQUENCE"):
    #     ((0, 2, 0), ['_', 1]),
    # ("APPLICATION", "LAMBDA_EXPANDED_SET_FAMILY"):
    #     ((0, 2, 0), ['_', 1]),

    ###############
    # APPLICATION #
    ###############
    "APP(CONSTANT/name=composition, ...)": ((-2,), r'\circ', (-1,)),
    "APP(CONSTANT/name=Identite, ...)":  ("Id",),
    "APP(CONSTANT/name=symmetric_difference, ...)": ((-2, ), r'\Delta', (-1, )),

    # Generic app for constants and their negation
    # CST? = CONSTANT with any name
    "NOT(APP(CST?,...))": ((0, -1), r'\text_is_not', (0, 0)),
    "APP(CST?, ...)": ((-1,), [r'\text_is', (0,)]),
    # f(x):
    "APP(?0: FUNCTION(?1, ?2), ?3)": ((0, ), r"\parentheses", (1, )),
    # u_n:
    # Here ?0 will be an expanded sequence, thus child 0 is the body "u_n",
    # we want the child 0 of this ("u").
    # "APP(?0: SEQUENCE(?1, ?2), ?3)": ((0, 0), ["_", 1]),
    "APP(LOCAL_CONSTANT:SET_FAMILY(?0, ?1)(?2), ?3)": ('(0.name)', '_', 2),
    "LOCAL_CONSTANT:SET_FAMILY(?0, ?2)(?1)":
        (r"\{", name, '_', 1, ', ', 1, r"\in_symbol", 0, r"\}"),
    # "LAMBDA:SET_FAMILY(?0, ?2)(?1)":
    #     (r"\{", name, '_', 2, ', ', 2, r"\in_symbol", 0, r"\}")
    ######
    # in #
    ######
}

latex_from_pattern_string.update(quant_pattern)

# NB: no parentheses will be put around property P(x)
# If parentheses are needed then we must switch to children (instead of
# metavars), e.g. (2,) for indicating P(x).
text_from_pattern_string = {
    "QUANT_∀(SET(...), ?0, ?1)":      (_("for every subset") + " ", 0,
                                       _(" of "), (0, 0), ", ", 1),
    "QUANT_∀(FUNCTION(...), ?0, ?1)": (_("for every function") + " ", 0,
                                       _(" from "), (0, 0), _(" to "), (0,
                                                                        1), ", ", 1),
    "QUANT_∀(PROP, ?0, ?1)":          (_("for every proposition") + " ", 0, ", ", 1),
    "QUANT_∀(TYPE(...), ?0, ?1)":     (_("for every set") + " ", 0, ", ", 1),
    "QUANT_∀(SEQUENCE(...), ?0, ?1)":
        ("global", _("for every sequence {} of elements of {}, {}"),
         0, (0, 0), (0, 1), 1),
    "QUANT_∃(SET(...), ?0, ?1)":      (_("there exists a subset") + " ", 0,
                                       " of ", (0, 0), _(" such that "), 1),
    "QUANT_∃(FUNCTION(...), ?0, ?1)":
        ("global", _("there exists a function {} from {} to {} such that {}"),
         0, (0, 0), (0, 1), 1),
    "QUANT_∃(PROP, ?0, ?1)":
        ("global", _("there exists a proposition {} such that {}"), 0, 1),
    "QUANT_∃(TYPE(...), ?0, ?1)":     (_("there exists a set") + " ", 0,
                                       _(" such that "), 1),
    "QUANT_∃(SEQUENCE(...), ?0, ?1)":
        ("global", _("there exists a sequence {} of elements of {} such that {}"),
         0, (0, 0), (0, 1), 1),
    "QUANT_∃!(SET(...), ?0, ?1)": (_("there exists a unique subset") + " ",
                                   0, _(" of "), (0, 0), _(" such that "), 1),
    "QUANT_∃!(FUNCTION(...), ?0, ?1)":
        ("global", _("there exists a unique function {} from {} to {} such that {}"),
         0, (0, 0), (0, 1), 1),
    "QUANT_∃!(PROP, ?0, ?1)":
        ("global", _("there exists a unique  proposition {} such that {}"), 0, 1),
    "QUANT_∃!(TYPE(...), ?0, ?1)": (_("there exists a unique set") + " ", 0,
                                    _(" such that "), 1),
    "QUANT_∃!(SEQUENCE(...), ?0, ?1)":
        ("global",
         _("there exists a unique sequence {} of elements of {} such that {}"),
         0, (0, 0), (0, 1), 1)
}

# TODO: handle jokers, e.g. *INEQUALITY

latex_from_pattern_string_for_type = {
    "SET(?0)": (r'\type_subset', 0),
    "SET_FAMILY(...)": (r'\type_family_subset', (1, )),
    "SEQUENCE(...)": (r'\type_sequence', (1, )),
    # TYPE... TODO (r'\type_element', name)
    "TYPE": (r'\set',),
    "FUNCTION(...)": (r'\function_from', (0, ), r'\to', (1, )),
    "?:TYPE": (r'\type_element', name),  # NB: TYPE is treated above
    "?:SET": (r'\type_element', name),
    "CONSTANT/name=ℕ": (r'\type_N', ),  # TODO: test!!
    "CONSTANT/name=ℤ": (r'\type_Z',),
    "CONSTANT/name=ℚ": (r'\type_Q',),
    "CONSTANT/name=ℝ": (r'\type_R',),
    "CONSTANT/name=RealSubGroup": (r'\type_R',)
}

#############################
# This are the useful lists #
#############################
pattern_latex = []
pattern_text = []
pattern_latex_for_type = []

dic_list_pairs = [(latex_from_pattern_string, pattern_latex),
                  (latex_from_pattern_string_for_type, pattern_latex_for_type),
                  (text_from_pattern_string, pattern_text)]


def string_to_pattern():
    """
    Fill-in the patterns_from_string dict by turning the keys of
    latex_from_pattern_string into PatternMathObject.
    """
    log.info("Pattern from strings:")
    for dict_, list_ in dic_list_pairs:
        for key, latex_shape in dict_.items():
            tree = tree_from_str(key)
            metavars = []
            pattern = PatternMathObject.from_tree(tree, metavars)
            list_.append((pattern, latex_shape, metavars))
            print(key)
            print(tree.display())


string_to_pattern()

