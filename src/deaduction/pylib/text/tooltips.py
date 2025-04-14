"""
##########################################
# tooltips.py : set tooltips for buttons #
##########################################

Provide two public methods:
    button_symbol(name) which provides a string to be displayed on the button,
    button_tooltip(name) which provides a list of lines for tooltips.
keys are names of actions methods, e.g. 'implies' for action_implies.

Tooltips may be changed here by super-user at their convenience.
To add a new ActionButton, update
    the __tooltips dict, and
    the __compute_buttons_symbols_dict() method.

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
# from deaduction.pylib.math_display.more_display_utils import replace_dubious_characters


########################################################################
# Set tooltips and text button HERE to enable translation with gettext #
########################################################################
# Logic and proof Buttons tooltips

# We do not want translation at init but on the spot
# But we want poedit to mark those str for translation
def _(msg):
    return msg


def replace_dubious_characters(s: str) -> str:
    if not s:
        return ""
    dubious_characters = "ℕ, ℤ, ℚ, ℝ, 𝒫, ↦"
    replacement_characters: str = cvars.get("display.dubious_characters")
    if replacement_characters == dubious_characters:
        return s
    else:
        character_translation_dic = {}
        default_list = dubious_characters.split(', ')
        new_list = replacement_characters.split(',')
        if len(default_list) != len(new_list):
            return s

        for default, new in zip(default_list, new_list):
            character_translation_dic[default] = new.strip()

        new_string = ""
        for char in s:
            new_char = (character_translation_dic[char]
                        if char in character_translation_dic
                        else char)
            new_string += new_char
        return new_string


#######################
#######################
# The __tooltips dict #
#######################
#######################
# A list of lines for the tooltip of each button, with key = action name
# Modify tooltips here, add an entry for a new button
__tooltips = {
    'prove_forall':
        [_("""Prove '∀ x, P(x)' by introducing 'x'""")],
    'use_forall':
        [_("""From some 'x' and '∀ y, P(y)' get 'P(x)'""")],
    'prove_exists':
        [_("""Prove '∃ x, P(x)' by specifying some 'x'""")],
    'use_exists':
        [_("""From '∃ x, P(x)' get an 'x' and 'P(x)'""")],
    'prove_implies':
        [_("""Prove 'P ⇒ Q' by assuming 'P', and proving 'Q'""")],
    'use_implies':
        [_("""From 'P' and 'P ⇒ Q' get 'Q'""")],
    'prove_and':
        [_("Prove the property 'P AND Q' by proving separately 'P' and 'Q'")],
    'use_and':
        [_("From the property 'P AND Q', get 'P' and 'Q'")],
    'prove_or':
        [_("Prove 'P OR Q' by choosing to prove either 'P' or 'Q'")],
    'use_or':
        [_("Use property 'P OR Q' by splitting cases")],
    'not':
        [_("""Try to simplify the property 'NOT P'""")],
    'iff':
        [_("Split 'P ⇔ Q' into two implications"),
        _("From 'P ⇒ Q' and 'Q ⇒ P' get 'P ⇔ Q'")],
    'equal':
        [_("""Use an equality to substitute one term with the other""")],
    "map":
        [_("""Apply a function to an element or an equality""")],
    # 'apply':
    #     # [_("Apply an equality or an iff to substitute in another property"),
    #     _("""Apply a function to an element or an equality"""),
    'proof_methods':
        [_("""Choose some specific proof method""")],
    # + "• " + _("Case-based reasoning") + "\n"
    # + "• " + _("Proof by contrapositive") + "\n"
    # + "• " + _("Proof by contradiction"),
    'new_object':
        [_("Create a new object (e.g. 'f(x)' from 'f' and 'x'"),
        _("Create a new subgoal (a lemma)"),
        _("Create a function from X to Y from property '∀ x ∈ X, ∃ y ∈ Y, P(x,"
            "y)'")],
    # 'assumption_old':
    #     _("Terminate the proof when the target is obvious from the context"),
    'assumption':
        [_("Terminate the proof when the target is obvious from the context")],
    # 'compute':
    #     [_("Terminate the proof when target results from manipulating "
    #        "numbers")],
    'sum':
        [_('Add equalities or inequalities')],
    'triangular_inequality':
        [_('Obtain a triangular inequality adapted to a selected equality or '
           'inequality')],
        # _('(under dev) Apply the triangular inequality to some numbers')],
    'simplify': [_("Try to simplify expression")],
    'commute': [_("Use a commutativity rule")],
    "associativity": [_("Use an associativity rule")],
    "transitivity":  [_("Use a transitivity rule, e.g. for chaining "
                        "inequalities")],
    'complete': [_('Replace "..." in object, property or goal by a '
                   'suitable formula')]
}

for key in ('forall', 'exists', 'implies', 'and', 'or'):
    __tooltips[key] = __tooltips['prove_' + key] + __tooltips['use_' + key]

# Decentralized apply buttons
# this phrase will be preceded by "double click to "
# __tooltips_apply = {
#     'tooltip_apply_function':
#     _("""apply this function to a selected object or equality"""),
#     'tooltip_apply_implication':
#     _("apply this implication to a selected property, or to modify the goal"),
#     'tooltip_apply_substitute':
#     _("""use to substitute in a selected property"""),
#     'tooltip_apply_for_all':
#     _("""apply this property to a selected object"""),
#     'tooltip_apply_exists':
#     _("""get a new object in the context"""),
#     'tooltip_apply_and':
#     _("""split into two properties""")
# }

#########################
# Define button symbols #
#########################
__buttons_symbols = dict()
# Logic buttons by lines, this should determine placement in UI. FIXME
# logic_buttons = ['and', 'or', 'not', 'implies', 'iff', 'forall', 'exists',
#                  'equal', 'map']
# logic_buttons_line_1 = ["and", "or", "not", "implies", "iff"]
# logic_buttons_line_2 = ["forall", "exists", "equal", "map"]
logic_buttons_line_1 = ["forall", "exists", "implies", "and", "or"]
logic_buttons_line_2 = ["not", "iff", "equal", "map"]
compute_buttons_line = ["sum"]
# logic_buttons = logic_buttons_line_1 + logic_buttons_line_2

__logic_translation =\
    [_('FORALL'), _('EXISTS'), _('IMPLIES'), _('AND'), _('OR'),
     _('PROVE FORALL'), _('PROVE EXISTS'), _('PROVE IMPLIES'), _('PROVE AND'),
     _('PROVE OR'),
     _('USE FORALL'), _('USE EXISTS'), _('USE IMPLIES'), _('USE AND'),
     _('USE OR'),
     _('NOT'), _('IFF'), _('EQUAL'), _('MAP'),
     _('NEW OBJECT'), _('PROOF METHODS'), _('ASSUMPTION'),
     _('SUM'), _('TRANSITIVITY'), _('ASSOCIATIVITY'), _('COMMUTE'),
     _('TRIANGULAR INEQUALITY'), _('SIMPLIFY')]


def __compute_buttons_symbols_dict():
    """
    Populate the __button_symbols dict with
        keys from the logic_buttons list
        symbols from the logic_button_symbols found in config.toml.
    The keys correspond to Action's names, the values will be displayed on
    the ui's ActionButtons (after translation). The resulting dict should
    contain one entry for each possible action button.
    """
    # (0) non logic buttons
    # Add a new button here (except for logic buttons).
    non_logic_buttons_symbols = {
        # 'apply': _('Apply'),
        'proof_methods': _("Proof methods..."),
        'new_object': _('New object...'),
        # 'assumption_old': 'Goal! (old)',
        'assumption': _("Goal!"),
        'compute': _('Compute'),
        'simplify': _("Simp"),
        'triangular_inequality': "△",
        'commute': "↔",
        "associativity": "()",
        "transitivity": "<<",
        'CQFD': _('Goal!') + "+"
    }
    __buttons_symbols.update(non_logic_buttons_symbols)

    # (1) Unified logic buttons
    # Add a new logic button by modifying the config.toml entry,
    # 'display.symbols_AND_OR_NOT_IMPLIES_IFF_FORALL_EXISTS_EQUAL_MAP'.
    config_field = \
        'display.symbols_AND_OR_NOT_IMPLIES_IFF_FORALL_EXISTS_EQUAL_MAP_SUM'
    # --> Construct buttons list
    logic_buttons = config_field.split("_")[1:]
    # --> Get symbols
    logic_button_symbols = cvars.get(config_field)
    logic_button_symbols = logic_button_symbols.split(", ")
    use_symbols = cvars.get('display.use_symbols_for_logic_button')
    if not use_symbols:
        logic_button_symbols[0] = "AND"
        logic_button_symbols[1] = "OR"
        logic_button_symbols[2] = "NOT"

    for key, value in zip(logic_buttons, logic_button_symbols):
        key = key.lower()
        __buttons_symbols[key] = value
        # Add demo and use buttons
        if key in logic_buttons_line_1:
            __buttons_symbols['prove_' + key] = _('prove') + ' ' + value
            __buttons_symbols['use_' + key] = _('use') + ' ' + value


def button_symbol(name: str):
    """
    Return symbol (i.e. string to be displayed on the button in the ui)
    for the button corresponding to function action_<name>.
    e.g. action_and, action_proof_method, and so on.

    NB: translation is NOT done here, gettext translation function _ must be
     applied to the output.
    """

    __compute_buttons_symbols_dict()
    symbol = __buttons_symbols.get(name, name.capitalize().replace('_', ' '))
    symbol = replace_dubious_characters(symbol)
    return symbol


def button_tool_tip(name: str) -> [str]:
    """
    Return tool_tip for the button corresponding to function action_<name>.
    e.g. action_and, action_proof_method, and so on.
    The return format is a list of lines that should be concatenated.
    The tooltips for unified buttons (e.g. implies) are the sum of the demo
    and the use versions (e.g. implies.prove and implies.use).

    NB: translation is NOT done here.
    """
    # (1) Compute pretty name of the logic button to explicit the symbols
    pretty_name = name.upper()+':'
    pretty_name = pretty_name.replace('_', ' ')

    # (2) Get tooltip
    demo_name = name + '_proof'
    if demo_name in __tooltips:
        use_name = name + '_use'
        tooltip = __tooltips.get(demo_name) + __tooltips.get(use_name)
    else:
        tooltip = __tooltips.get(name)
    # if isinstance(tooltip, str):
    #     tooltip = [tooltip]

    # (3) Insert pretty name as a title
    if tooltip:
        if tooltip[0] != pretty_name:
            tooltip.insert(0, pretty_name)
        return tooltip

