"""
##########################################################
# app_pattern_data.py : patterns to display APPLICATIONs #
##########################################################

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

from deaduction.pylib.math_display.display_data import name, value

log = logging.getLogger(__name__)

global _

# NB: the

latex_from_app_pattern = {
    # For functions, two patterns: (f circ g)(x) and (f circ g).
    "APP(CONSTANT/name=composition, ?1, ?2, ?3, ?4: FUNCTION(?2, ?3), "
    "?5: FUNCTION(?1, ?2), ?6: ?7)": (4, r'\circ', 5, r"\parentheses", 6),
    "APP(CONSTANT/name=composition, ?1, ?2, ?3, ?4: FUNCTION(?2, ?3), "
    "?5: FUNCTION(?1, ?2))": (4, r'\circ', 5),
    # TODO: test Id, Id(x)
    "APP(CONSTANT/name=Identite, ?1, ?2: ?1)": ("Id", r"\parentheses", 2),

    # TODO: sequences and set families
    # u_n:
    "APP(LOCAL_CONSTANT: !SEQUENCE(?2, ?3)(...), ?1: ?2)":
        ('(0, ).name', ["_", (1, )]),
    # APP(E, i) --> E_i
    #   Here E is the name of the local constant, which is self.children[0]
    "APP(LOCAL_CONSTANT: !SET_FAMILY(?2, ?3)(...), ?1: ?2)":
        ('(0,).name', ['_', (1, )]),
    "APP(CONSTANT/name=limit_function, LAMBDA(?2, ?3, ?4), ?0, ?1)":
        (r'\no_text', "lim", ['_', (-3, 1), r'\to', (-2,)], ' ', (-3, 2),
         " = ", (-1,))
}

# TODO: english translation
# Negative value = from end of children list
# Here int stands for children (not metavars), but only if they are not nested
# inside lists
latex_from_constant_name = {
    "symmetric_difference": (-2, r'\Delta', -1),
    # "composition": (4, r'\circ', 5),  # APP(compo, X, Y, Z, g, f)
    "prod": (1, r'\times', 2),
    "Identite": ("Id",),# FIXME: use Id for name...
    "identite": ("Id",),
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
    "converging_seq": (-1, r'\text_is', _(" converging")),
    "limit_plus_infinity": ("lim ", -1, " = +∞"),
    "increasing_seq": (-1, r'\text_is', _(" non decreasing")),
    "bounded_above": (-1, r'\text_is', " " + _("bounded from above")),
    "bounded_below": (-1, r'\text_is', " " + _("bounded from below")),
    "bounded_sequence": (-1, r'\text_is', " " + _("bounded")),
    "limit_function": ("lim", ['_', (-2,)], (-3,), " = ", (-1,)),
    "continuous": (-1, r'\text_is', _("continuous")),
    "uniformly_continuous": (-1, r'\text_is', _("uniformly continuous")),
    "continuous_at": (-2, r'\text_is', _("continuous at") + " ", -1),
    "cauchy": (-1, r'\text_is', _("a Cauchy sequence")),
    "abs": ('|', -1, '|'),
    "max": ("Max", r'\parentheses', -2, ",", -1),
    "inv": ([r'\parentheses', (-1, )], [r'^', '-1']),
    "product": (-2, ".", -1),
    "image": (-1, " = ", -3, "(", -2, ")"),
    "relation_equivalence": (-1, r'\text_is', _("an equivalence relation")),
    "classe_equivalence": (r"\[", (-1, ), r"\]", ["_", (1, )]),
    "disjoint": (-2, " " + _("and") + " ", -1, " " + _("are disjoint")),
    "powerset": (r'\set_of_subsets', [r"\parentheses", (-1, )]),
    "partition": (-1, r'\text_is', _("a partition of") + " ", -2),
    "application": (-1, r'\text_is', _("an application") + " "),
    "application_bijective":  (-1, r'\text_is', _("a bijective application") + " "),
    "RealSubGroup": (r"\real", ),
    "even":  (-1,  r'\text_is', " " + _("even"))
}

# TODO: use latex_from_constant_names, éventuellement les transformer
#  automatiquement en pattern
#  ex:     "symmetric_difference": (-2, r'\Delta', -1),
#  --> "APP(CONSTANT/name=symmetric_difference, ...)": ...

generic_app_dict = {
    # The following works only for some constant, do not use:
    # "NOT(APP(CST?,...))": ((0, -1), r'\text_is_not', (0, 0)),
    # Generic app for constants
    # CST? = CONSTANT with any name
    "APP(CST?, ...)": ((-1,), [r'\text_is', (0,)]),
    # f(x):
    "APP(?0: !FUNCTION(?1, ?2), ?3: ?1)": ((0,), r"\parentheses", (1,)),
    # Replace x ↦ f(x) by f:
    "LAMBDA(?0, ?1, APP(?3, ?1))": ((2, 0),)
}


def app_pattern_from_constants():
    """
    Construct APPLICATION patterns from constant dictionary, and also their
    negations when appropriate.
    """
    latex_from_app_constant_patterns = {}
    for key, value in latex_from_constant_name.items():
        # Modify key:
        new_key = f'APP(CONSTANT/name={key}, ...)'
        # Change int into tuples in value:
        new_value = tuple((item, ) if isinstance(item, int)
                          else item
                          for item in value)
        if r'\text_is' in new_value:
            new_not_key = f"NOT(APP(CONSTANT/name={key},...))"
            new_not_value = tuple(r'\text_is_not' if item is r'\text_is' else
                                  (0, item) if isinstance(item, int) else
                                  (0, ) + item if isinstance(item, tuple)
                                  else item for item in new_value)
            latex_from_app_constant_patterns[new_not_key] = new_not_value
        latex_from_app_constant_patterns[new_key] = new_value
    latex_from_app_pattern.update(latex_from_app_constant_patterns)

    latex_from_app_pattern.update(generic_app_dict)
