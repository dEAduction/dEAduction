"""
##########################################
# tooltips.py : set tooltips for buttons #
##########################################

Tooltips may be changed here by user at their convenience.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 10 2020 (creation)
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

import deaduction.pylib.config.vars as cvars

########################################################################
# Set tooltips and text button HERE to enable translation with gettext #
########################################################################
# Logic and proof Buttons tooltips
# Disable translation: translation will be done on the fly
# _ = lambda message: message
# TODO: modify tooltip as a list of lines,
#  to help translation


# We do not want translation at init but on the spot
# But we want poedit to mark those str for translation
def _(msg):
    return msg


__tooltips = {
    'and':
        [_("Split a property 'P AND Q' into the two properties 'P', 'Q'"),
        _("Conversely, assemble 'P' and 'Q' to get 'P AND Q'")],
    'or':
        [_("Prove 'P OR Q' by proving either 'P' or 'Q'"),
        _("Use property 'P OR Q' by splitting cases")],
    'not':
        _("""Try to simplify the property 'NOT P'"""),
    'implies':
        [_("""Prove 'P ⇒ Q' by assuming 'P', and proving 'Q'"""),
        _("""From 'P' and 'P ⇒ Q' get 'Q'""")],
    'iff':
        [_("Split 'P ⇔ Q' into two implications"),
        _("From 'P ⇒ Q' and 'Q ⇒ P' get 'P ⇔ Q'")],
    'forall':
        [_("""Prove '∀ x, P(x)' by introducing 'x'"""),
        _("""From some 'x' and '∀ x, P(x)' get 'P(x)'""")],
    'exists':
        [_("""Prove '∃ x, P(x)' by specifying some 'x'"""),
        _("""From '∃ x, P(x)' get an 'x' and 'P(x)'""")],
    'equal':
        _("""Use an equality to substitute one term with the other"""),
    "mapsto":
        _("""Apply a function to an element or an equality"""),
    'apply':
        # [_("Apply an equality or an iff to substitute in another property"),
        _("""Apply a function to an element or an equality"""),
    'proof_methods':
        _("""Choose some specific proof method"""),
    # + "• " + _("Case-based reasoning") + "\n"
    # + "• " + _("Proof by contrapositive") + "\n"
    # + "• " + _("Proof by contradiction"),
    'new_object':
        [_("Create a new object (e.g. 'f(x)' from 'f' and 'x'"),
        _("Create a new subgoal (a lemma)"),
        _("Create a function from X to Y from property '∀ x ∈ X, ∃ y ∈ Y, P(x,"
            "y)'")],
    'assumption':
        _("Terminate the proof when the target is obvious from the context"),
    'compute':
        _("Terminate the proof when target results from manipulating numbers")
}
# Decentralized apply buttons
# this phrase will be preceded by "double click to "
__tooltips_apply = {
    'tooltip_apply_function':
    _("""apply this function to a selected object or equality"""),
    'tooltip_apply_implication':
    _("apply this implication to a selected property, or to modify the goal"),
    'tooltip_apply_substitute':
    _("""use to substitute in a selected property"""),
    'tooltip_apply_for_all':
    _("""apply this property to a selected object"""),
    'tooltip_apply_exists':
    _("""get a new object in the context"""),
    'tooltip_apply_and':
    _("""split into two properties""")
}

#########################
# Define button symbols #
#########################
__buttons_symbols = {
    'apply': _('Apply'),
    'proof_methods': _("Proof methods..."),
    'new_object': _('New object...'),
    'assumption': _('Goal!'),
    'compute': _('Compute'),
    'CQFD': _('Goal!')
}
logic_buttons = ['and', 'or', 'not', 'implies', 'iff', 'forall', 'exists',
                 'equal', 'mapsto']
logic_button_symbols = cvars.get(
    'display.symbols_AND_OR_NOT_IMPLIES_IFF_FORALL_EXISTS_EQUAL_MAPSTO')
# FIXME: in config_window, check format
symbols = logic_button_symbols.split(", ")
for key, value in zip(logic_buttons, logic_button_symbols.split(", ")):
    __buttons_symbols[key] = value


def button_symbol(name):
    """
    Return symbol for the button corresponding to function action_<name>.
    e.g. action_and, action_proof_method, and so on.
    NB: translation is NOT done here, gettext translation function _ must be
     applied to the output.
    """
    if name in __buttons_symbols:
        return __buttons_symbols[name]


def button_tool_tip(name):
    """
    Return tool_tip for the button corresponding to function action_<name>.
    e.g. action_and, action_proof_method, and so on.
    NB: translation is NOT done here.
    """
    return __tooltips[name]


def apply_tool_tip(name):
    return __tooltips_apply[name]

# TODO: unused?
# def get(k):
#     return __tooltips.get(k, None)       \
#         or __tooltips_apply.get(k, None) \
#         or __buttons[k]



