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


from typing import Union

from logging import getLogger

# from deaduction.pylib.mathobj import MathObject
from deaduction.pylib.pattern_math_obj import PatternMathObject

from deaduction.pylib.math_display.pattern_parser import tree_from_str

log = getLogger(__name__)

global _
# _ = lambda x: x  # Just for debugging:


def name(mo):
    return mo.info.get('name', "NO NAME")


def value(mo):
    return mo.info.get('value')


def math_object_itself(mo):
    return mo


latex_from_pattern_string = {
    "CONSTANT": (name, ),
    "NUMBER": (value, ),
    "LOCAL_CONSTANT": (math_object_itself, ),  # Delay display!
    # ∀A⊆X, ... :
    "FORALL(SET(?0), ?1, ?2)": (r'\forall', 1, r'\subset', 0, 2),

    #######
    # APP #
    #######
    "APP('composition', ...)": (-2, r'\circ', -1),
    # "APP(CONSTANT(name='composition'), ..., ?-2, ?-1)"
    # f is not injective:
    "NOT(APP(...)": (-2, r'\text_is_not', -1),
    # f(x):
    "APP(?0: FUNCTION(?1, ?2), ?3)": (0, r"\parentheses", 1),
    # u_n:
    # Here ?0 will be an expanded sequence, thus child 0 is the body "u_n",
    # we want the child 0 of this ("u").
    "APP(?0: SEQUENCE(?1, ?2), ?3)": ((0, 0), ["_", 3])
}

latex_from_patterns = {}


def string_to_pattern():
    """
    Fill-in the patterns_from_string dict by turning the keys of
    latex_from_pattern_string into PatternMathObject.
    """
    log.info("Pattern from strings:")
    for key, value in latex_from_pattern_string.items():
        tree = tree_from_str(key)
        pattern = PatternMathObject.from_tree(tree)  # Fixme
        latex_from_patterns[key] = pattern
        log.debug(key)
        # log.debug(f"-->{pattern.to_display(format_='utf8')}")


string_to_pattern()



