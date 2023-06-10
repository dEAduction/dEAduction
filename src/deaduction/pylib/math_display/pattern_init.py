"""
###############################################################
# pattern_init.py : create usable lists of patterns from data #
###############################################################

This modules produces lists for pattern matching, that are used by the
new_display module:
    pattern_latex : patterns for displaying objects with symbols
    pattern_text : idem, with text
    pattern_latex_for_type : idem, for types of context objects.

The patterns are produced by the PMO.from_tree class method, based on the
dictionaries in
    pattern_data.py
    app_pattern_data.py

This also makes use of the tree_from_str() function of pattern_parser.py.

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


import logging

from deaduction.pylib.math_display.pattern_data import \
    latex_from_pattern_string, latex_from_pattern_string_for_type, \
    text_from_pattern_string, quant_pattern, \
    set_quant_pattern, lean_from_pattern_string

from deaduction.pylib.math_display.app_pattern_data import \
    latex_from_app_pattern, app_pattern_from_constants, generic_app_dict

from deaduction.pylib.pattern_math_obj.pattern_parser import tree_from_str
from deaduction.pylib.pattern_math_obj import PatternMathObject

log = logging.getLogger(__name__)

#############################
# This are the useful lists #
#############################
pattern_latex = []
pattern_lean = []
pattern_text = []
pattern_latex_for_type = []

# This list indicates how to populate pattern lists from dictionaries:
# Careful, order matters.
dic_list_pairs = \
    [(lean_from_pattern_string, pattern_lean),
     (latex_from_app_pattern, pattern_latex),
     # The order matters! The generic patterns must come at the end.
     (generic_app_dict, pattern_latex),
     (quant_pattern, pattern_latex),
     (latex_from_pattern_string, pattern_latex),
     (latex_from_pattern_string_for_type, pattern_latex_for_type),
     (text_from_pattern_string, pattern_text)]


def string_to_pattern():
    """
    Fill-in the patterns_from_string dict by turning the keys of
    latex_from_pattern_string into PatternMathObject.
    """

    log.info("Pattern from strings:")
    # (1) Clear pattern lists
    for dict_, list_ in dic_list_pairs:
        list_.clear()

    # (2) Fill in pattern dicts
    for dict_, list_ in dic_list_pairs:
        for key, latex_shape in dict_.items():
            tree = tree_from_str(key)
            metavars = []
            pattern = PatternMathObject.from_tree(tree, metavars)
            list_.append((pattern, latex_shape, metavars))
            # print(key)
            # print(tree.display())


def pattern_init(additional_constants=None):
    set_quant_pattern()
    app_pattern_from_constants(additional_data=additional_constants)
    string_to_pattern()


########################################
########################################
# We need some code to create the data #
########################################
########################################
pattern_init()
