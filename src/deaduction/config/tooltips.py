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
from .set_language import _
########################################################################
# set tooltips and text button HERE to enable translation with gettext #
########################################################################
# Logic and proof Buttons tooltips
__tooltips = {
    'tooltip_and':
        _("""• Split a property 'P AND Q' into the two properties 'P', 'Q'
• Inversely, assembles 'P' and 'Q' to get 'P AND Q'"""
          ),
    'tooltip_or':
        _("""• Prove 'P OR Q' by proving either 'P' or 'Q'
• Use the property 'P OR Q' by splitting the cases when P is True and Q is True"""
          ),
    'tooltip_not':
        _("""Try to simplify the property 'NOT P'"""),
    'tooltip_implies':
        _("""Prove 'P ⇒ Q' by assuming 'P', and proving 'Q'"""),
    'tooltip_iff':
        _("""Split 'P ⇔ Q' into two implications"""),
    'tooltip_forall':
        _("""Prove '∀ a, P(a)' by introducing 'a'"""),
    'tooltip_exists':  # TODO: possibility to 'APPLY' '∃ x, P(x)'
        _("""• Prove '∃ a, P(a)' by specifying some 'a' and proving P(a)
• Apply '∃ a, P(a)' to get an 'a' satisfying 'P(a)'"""
          ),
    'tooltip_apply':
        _("""• Apply to a property '∀ a, P(a)' and some 'a' to get 'P(a)' 
• Apply a property 'P ⇒ Q' to 'P' to get 'Q'
• Apply an equality or a logical equivalence to substitute in another property
• Apply a function to an element or an equality"""
          ),
    'tooltip_proof_methods':
        _("""Choose some specific proof method: 
• Case-based reasoning
• Proof by contrapositive
• Proof by contradiction"""
          ),
    'tooltip_new_object':
        _("""• Create a new object (e.g. 'f(a)' from 'f' and 'a')
• Create a new subgoal (a lemma) which will be proved, and added to the context
• From a property '∀ a ∈ A, ∃ b ∈ B, P(a,b)', create a new function from A to B"""
          ),
    'tooltip_assumption':
        _(
            """Terminate the proof when the target is obvious from the context"""
        )
}
# decentralized apply buttons
__tooltips_apply = {
    'tooltip_apply_function':
        _("""apply function to a selected object or equality"""),
    'tooltip_apply_implication':
        _("""apply to a selected property, or to modify the goal"""),
    'tooltip_apply_substitute':
        _("""substitute in a selected property"""),
    'tooltip_apply_for_all':
        _("""apply to a selected object"""),
    'tooltip_apply_exists':
        _("""get a new object in the context"""),
    'tooltip_apply_and':
        _("""Split into two properties""")
}  # TODO

# Text for buttons
__buttons = {
    'logic_button_texts': _("AND, OR, NOT, ⇒, ⇔, ∀, ∃"),
    'proof_button_texts': _("Apply, Proof Methods, New Object, QED")
}
# sad thoughts for "¯\_(ツ)_/¯", I loved you so much...
