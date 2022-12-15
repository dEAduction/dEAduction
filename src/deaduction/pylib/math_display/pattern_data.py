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

IMPORTANT: our dictionaries are ORDERED. For instance, a sequence u is
displayed as (u_n)_{n in N} ; but a term of the sequence, say u applied to
integer n, is displayed as u_n, so we want to catch this BEFORE catching u
and deciding to display (u_n)_{n in N}_n.

----------------------
SYNTAX FOR KEYS. Let us analyze the following example:

    "LOCAL_CONSTANT:SET_FAMILY(?3, ?4)(...)"

- We first indicate the node: 'LOCAL_CONSTANT'.
- Then we give its type: ':SET_FAMILY(?3, ?4)'. Here ?3 and ?4 are
metavariables that can take any value; so the type must have two children
that can be used for displaying.
- Then (...) indicates that we do not care about children of the local constant:
any children, whatever their number, will match.

With the node we can also indicate some elements of the 'info' dict, e.g. in
    "CONSTANT/name=ℕ".

SYNTAX FOR VALUES. e.g.

    (r"\{", name, ['_', (1,)], ', ', (1,), r"\in_symbol", 3, r"\}"),
Integers refers to metavariables, tuples to children and descendants.
We use '_' or '^' to indicate subscripts or superscrits.
We can use attributes like name, value, math_type, local_constant_display,
body, bound_var, and so on.
        e.g.    '(0, 0).name', '0.math_type'
or any callable which will be applied to self, e.g. name and value.

---------------------
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

import logging

from deaduction.pylib.math_display.display_data import name, value

log = logging.getLogger(__name__)

global _
# _ = lambda x: x  # Just for debugging:


# BEWARE: do not use negative number in pattern strings!
# info may be provided within nodes, e.g. "CONSTANT/name=toto".
# Use "?" as a joker, e.g. "CONSTANT/name=?".
# In the shape values,
#       tuples point for children (generalized or not),
#       integers point to metavars.
# "global" in first position in shape means that variables will be  inserted at
# "{}". This is used for text conversion and translation.

###############
###############
# QUANTIFIERS #
###############
###############
metanodes = {'*INEQUALITY': ("PROP_<", "PROP_>", "PROP_≤", "PROP_≥",
                             "PROP_EQUAL_NOT")}

quant_pattern = {
    # NB: QUANT nodes must have 3 children, with children[1] the bound var.
    # !! Macro must be alone in their string (up to spaces) after splitting
    # We use child nbs and not metavars to indicate P(x), since this is used
    # for good parenthesing.
    "QUANT_∀(SET(...), ?0, ?1)":
    (r"\forall", (1,), r" \subset ", (0, 0), ", ", (2,)),
    "QUANT_∀(FUNCTION(...), ?0, ?1)":
    (r"\forall", (1,), r" \function_from", (0, 0), r'\to', (0, 1), ", ", (2, )),
    "QUANT_∀(PROP, ?0, ?1)":
    (r"\forall", (1,), r'\proposition', ", ", (2, )),
    "QUANT_∀(TYPE(...), ?0, ?1)":
    (r"\forall", (1,), r" \set", ", ", (2, )),
    "QUANT_∀(SEQUENCE(...), ?0, ?1)":
    (r"\forall", (1,), r" \sequence_in", (0, 1), ", ", (2, )),
    "QUANT_∀(LOCAL_CONSTANT/name=RealSubGroup, ?0, ?1)":
        (r"\forall", (1,), r'\in', r'\real', ", ", (2,)),
    # Bounded quantification: TODO = option in settings
    "QUANT_∀(?0, ?1, PROP_IMPLIES(PROP_BELONGS(?1, ?2), ?3))":
        (r"\forall", (2, 0), ", ", (2, 1)),
    "QUANT_∀(?0, ?1, PROP_IMPLIES(*INEQUALITY(?1, ?2), ?3))":
        (r"\forall", (2, 0), ", ", (2, 1)),
    "QUANT_∃(?0, ?1, PROP_∃(*INEQUALITY(?1, ?2), ?3))":
        (r"\exists", (2, 0), ", ", (2, 1))
}


def exists_patterns_from_forall():
    """
    This method creates "exists" pattern that mimic the patterns for "for all".
    """
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


# The '!' means type must match (NO_MATH_TYPE not allowed)
latex_from_pattern_string = {
    "LOCAL_CONSTANT: !SET_FAMILY(?3, ?4)(...)":
        (r"\{", name, ['_', (1,)], ', ', (1,), r"\in_symbol", 3, r"\}"),
    "LAMBDA: !SET_FAMILY(?0, ?2)(...)":
        # (r"\{", (2,), ', ', (1,), r"\in_symbol", (0,), r"\}"),
        # (r"\{", 'self.body', ', ', 'self.bound_var', r"\in_symbol",
        #  'self.bound_var_type', r"\}"),
        (r"\{", (2,), ', ', (1,), r"\in_symbol", (0,), r"\}"),
    "LOCAL_CONSTANT: !SEQUENCE(?3, ?4)(...)":
        ('(', name, ['_', (1,)], ')', ['_', (1,), r"\in_symbol", 3]),
    "LAMBDA: !SEQUENCE(?3, ?4)(...)":
        ('(', (2, ), ')', ['_', (1, ), r"\in_symbol", (0, )]),
    "LOCAL_CONSTANT/name=RealSubGroup": (r'\type_R',)
}


#########################################
#########################################
# Special text versions for quantifiers #
#########################################
#########################################
# Quantifiers need special text versions since the order of words does not
# follow the order of symbols

# NB: no parentheses will be put around property P(x)
# If parentheses are needed then we must switch to children (instead of
# metavars), e.g. (2,) for indicating P(x).
text_from_pattern_string = {
    "QUANT_∀(SET(...), ?0, ?1)":
        (_("for every subset") + " ", (1, ), _(" of "), (0, 0), ", ", 1),
    "QUANT_∀(FUNCTION(...), ?0, ?1)":
        (_("for every function") + " ", 0,
         _(" from "), (0, 0), _(" to "), (0, 1), ", ", 1),
    "QUANT_∀(PROP, ?0, ?1)": (_("for every proposition") + " ", 0, ", ", 1),
    "QUANT_∀(TYPE(...), ?0, ?1)": (_("for every set") + " ", 0, ", ", 1),
    "QUANT_∀(SEQUENCE(...), ?0, ?1)":
        ("global", _("for every sequence {} of elements of {}, {}"),
         0, (0, 1), 1),
    "QUANT_∃(SET(...), ?0, ?1)":
        ("global", _("there exists a subset {} of {} such that {}"),
         0, (0, 0), 1),
    "QUANT_∃(FUNCTION(...), ?0, ?1)":
        ("global", _("there exists a function {} from {} to {} such that {}"),
         0, (0, 0), (0, 1), 1),
    "QUANT_∃(PROP, ?0, ?1)":
        ("global", _("there exists a proposition {} such that {}"), 0, 1),
    "QUANT_∃(TYPE(...), ?0, ?1)":
        (_("there exists a set") + " ", 0, _(" such that "), 1),
    "QUANT_∃(SEQUENCE(...), ?0, ?1)":
        ("global", _("there exists a sequence {} of elements of {} such that {}"),
         0, (0, 1), 1),
    "QUANT_∃!(SET(...), ?0, ?1)":
        ("global",
         _("there exists a unique subset {} of {} such that {}"),
         0, (0, 0), 1),
    "QUANT_∃!(FUNCTION(...), ?0, ?1)":
        ("global",
         _("there exists a unique function {} from {} to {} such that {}"),
         0, (0, 0), (0, 1), 1),
    "QUANT_∃!(PROP, ?0, ?1)":
        ("global", _("there exists a unique  proposition {} such that {}"),
         0, 1),
    "QUANT_∃!(TYPE(...), ?0, ?1)":
        (_("there exists a unique set") + " ", 0, _(" such that "), 1),
    "QUANT_∃!(SEQUENCE(...), ?0, ?1)":
        ("global",
         _("there exists a unique sequence {} of elements of {} such that {}"),
         0, (0, 1), 1)
}

########################################################
########################################################
# Patterns to display math_types of ContextMathObjects #
########################################################
########################################################
# TODO: handle jokers, e.g. *INEQUALITY

latex_from_pattern_string_for_type = {
    # We need this here, otherwise it match "?: TYPE":
    "NO_MORE_GOAL": (_("All goals reached!"),),
    "PROP": (r'\proposition',),
    "SET(?0)": (r'\type_subset', (0,)),
    "SET_FAMILY(...)": (r'\type_family_subset', (1, )),
    "SEQUENCE(...)": (r'\type_sequence', (1, )),
    # TYPE... TODO (r'\type_element', name)
    "TYPE": (r'\set',),
    "FUNCTION(...)": (r'\function_from', (0, ), r'\to', (1, )),
    "CONSTANT/name=ℕ": (r'\type_N', ),  # TODO: test!!
    "CONSTANT/name=ℤ": (r'\type_Z',),
    "CONSTANT/name=ℚ": (r'\type_Q',),
    "CONSTANT/name=ℝ": (r'\type_R',),
    "LOCAL_CONSTANT/name=RealSubGroup": (r'\type_R',),
    # This is maybe too strong: any guy with undefined math_type will match!! :
    "?:TYPE": (r'\type_element', name),  # NB: TYPE is treated above
    "?:SET(?0)": (r'\type_element', 'self'),
}

