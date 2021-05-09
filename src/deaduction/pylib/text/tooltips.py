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

from deaduction.pylib.config.i18n import _

########################################################################
# Set tooltips and text button HERE to enable translation with gettext #
########################################################################
# Logic and proof Buttons tooltips
__tooltips = {
    'tooltip_and':
    "• " + _("Split a property 'P AND Q' into the two properties 'P', 'Q'")
    + "\n" + "• " + _("Conversely, assemble 'P' and 'Q' to get 'P AND Q'"),
    'tooltip_or':
    "• " + _("Prove 'P OR Q' by proving either 'P' or 'Q'") + "\n"
    + "• " + _("Use property 'P OR Q' by splitting cases"),
    'tooltip_not':
        _("""Try to simplify the property 'NOT P'"""),
    'tooltip_implies':
        "• " + _("""Prove 'P ⇒ Q' by assuming 'P', and proving 'Q'""") + "\n"
    + "• " + _("""From 'P' and 'P ⇒ Q' get 'Q'"""),
    'tooltip_iff':
        "• "+_("Split 'P ⇔ Q' into two implications") + "\n"
    + "• " + _("From 'P ⇒ Q' and 'Q ⇒ P' get 'P ⇔ Q'"),
    'tooltip_forall':
    "• " + _("""Prove '∀ x, P(x)' by introducing 'x'""") + "\n"
    + "• " + _("""From some 'x' and '∀ x, P(x)' get 'P(x)'"""),
    'tooltip_exists':
    "• " + _("""Prove '∃ x, P(x)' by specifying some 'x'""") + "\n"
    + "• " + _("""From '∃ x, P(x)' get an 'x' and 'P(x)'""") + "\n"
    + "• " + _("""From some 'x' and 'P(x)' get '∃ x, P(x)'"""),
    'tooltip_apply':
    "• " + _("Apply an equality or an iff to substitute in another property")
    + "\n" + "• " + _("""Apply a function to an element or an equality""")
    + "\n" + "• " + _("""(... try it to find other uses)"""),
    'tooltip_proof_methods':
        _("""Choose some specific proof method:""") + "\n"
    + "• " + _("Case-based reasoning") + "\n"
    + "• " + _("Proof by contrapositive") + "\n"
    + "• " + _("Proof by contradiction"),
    'tooltip_new_object':
    "• " + _("Create a new object (e.g. 'f(x)' from 'f' and 'x'") + "\n"
    + "• " + _("Create a new subgoal (a lemma)") + "\n" + "• "
    + _("Create a function from X to Y from property '∀ x ∈ X, ∃ y ∈ Y, P(x,"
        "y)'"),
    'tooltip_assumption':
        _("Terminate the proof when the target is obvious from the context"),
    'tooltip_compute':
        _("Terminate the proof when target results from manipulating numbers")
}
# decentralized apply buttons
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

# Text for buttons
__buttons = {
    'logic_button_texts': _("AND, OR, NOT, ⇒, ⇔, ∀, ∃"),
    'proof_button_texts': _("Apply")
                          + ", " + _("Proof Methods")
                          + ", " + _("New Object"),
    'magic_button_texts': _('Compute') + ', ' + _('Goal!')
}
# Sad thoughts for "¯\_(ツ)_/¯", I loved you so much...


def get(k):
    return __tooltips.get(k, None)       \
        or __tooltips_apply.get(k, None) \
        or __buttons[k]
