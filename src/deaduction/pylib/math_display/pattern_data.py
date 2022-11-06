"""
###############################################################################
# pattern_data.py : data for creating PatternMathObject as helper for display #
###############################################################################

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

# TODO: turn APP(APP(...)) into APP(...) in MathObject.__init__() ???


import logging

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
latex_from_pattern_string = {
    # "LOCAL_CONSTANT": (name, ),
    # "CONSTANT": (name, ),
    # "NUMBER": (value, ),
    ##########
    # QUANTS #
    ##########
    # NB: QUANT nodes must have 3 children, with children[1] the bound var.
    # Thus "QUANT_∀(SET(...), ...) does not work.
    "QUANT_∀(SET(...), ?0, ?1)": (r"\forall", 0, r" \subset ", (0, 0), ", ", 1),
    "QUANT_∀(FUNCTION(...), ?0, ?1)": (r"\forall", 0, r" \function_from",
                                       (0, 0), r'\to', (0, 1), ", ", 1),
    "QUANT_∀(PROP, ?0, ?1)": (r"\forall", 0, r'\proposition', ", ", 1),
    "QUANT_∀(TYPE(...), ?0, ?1)": (r"\forall", 0, r" \set", ", ", 1),
    # ("QUANT_∀", "SEQUENCE"): (r"\forall", 1, r" \function_from", (0, 0),
    #                           r'\to', (0, 1), ", ", 2),
    # ("APPLICATION", "LOCAL_CONSTANT_EXPANDED_SEQUENCE"):
    #     ((0, 2, 0), ['_', 1]),
    # ("APPLICATION", "LOCAL_CONSTANT_EXPANDED_SET_FAMILY"):
    #     ((0, 2, 0), ['_', 1]),
    # ("APPLICATION", "LAMBDA_EXPANDED_SEQUENCE"):
    #     ((0, 2, 0), ['_', 1]),
    # ("APPLICATION", "LAMBDA_EXPANDED_SET_FAMILY"):
    #     ((0, 2, 0), ['_', 1]),

    #######
    # APP #
    #######
    "APP(CONSTANT/name=composition, ...)": ((-2,), r'\circ', (-1,)),
    # Generic app for constants and their negation
    # CST? = CONSTANT with any name
    "APP(CST?, ...)": ((-1,), [r'\text_is', (0,)]),
    "NOT(APP(CST?,...))": ((-2,), r'\text_is_not', (-1,)),
    # f(x):
    "APP(?0: FUNCTION(?1, ?2), ?3)": (0, r"\parentheses", 1),
    # u_n:
    # Here ?0 will be an expanded sequence, thus child 0 is the body "u_n",
    # we want the child 0 of this ("u").
    "APP(?0: SEQUENCE(?1, ?2), ?3)": ((0, 0), ["_", 3])

    ######
    # in #
    ######
}

# TODO: handle jokers, e.g. *INEQUALITY
# TODO: handle CONSTANT, e.g. 'composition'

###########################
# This is the useful dict #
###########################
pattern_latex_pairs = []


def string_to_pattern():
    """
    Fill-in the patterns_from_string dict by turning the keys of
    latex_from_pattern_string into PatternMathObject.
    """
    log.info("Pattern from strings:")
    for key, latex_shape in latex_from_pattern_string.items():
        tree = tree_from_str(key)
        metavars = []
        pattern = PatternMathObject.from_tree(tree, metavars)
        pattern_latex_pairs.append((pattern, latex_shape, metavars))
        print(key)
        print(tree.display())
        # print(pattern)
        # log.debug(f"-->{pattern.to_display(format_='utf8')}")


string_to_pattern()

