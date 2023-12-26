"""
#######################################################
# help_msgs.py : set msgs for help on context objects #
#######################################################

Note that msgs are not translated here, to handle the case when usr changes
language. They must be translated when used.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 08 2022 (creation)
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

import deaduction.pylib.config.vars as cvars
# from deaduction.pylib.math_display.utils import replace_dubious_characters
from .tooltips import button_symbol


# We do not want translation at init but on the spot
# But we want poedit to mark those str for translation
# And we want to remember _ for translation à la volée
# (see def get_help_msg() below)
global _

tr = _


def translate(string):
    """
    This is a hack: we want to delay the translation until excution.
    """
    return tr(string) if string else ""


def _(msg):
    """
    This is a hack: we want to delay the translation until excution.
    """
    return msg


# def single_to_every(an_object: str) -> str:
#     """
#     Replace "an object", e.g. "an element", by "every object", e.g. "every
#     element".
#     """
#     from deaduction.pylib.math_display.display_data import every
#     for key, value in every.items():
#         if an_object.find(key) != -1:
#             every_object = an_object.replace(key, value)
#             return every_object

def current_button_name(name: str, mode='display_unified') -> str:
    """
    Return a phrase pointing at the actual button corresponding to name.
    e.g. forall -> "the '∀' button", if mode == 'display_unified'
                -> "the '∀' button in prove mode", if mode == 'display_switch'
                -> "the 'prove ∀' button", if mode == 'display_both'
    """
    use_or_prove, name = name.split('_')

    mode = cvars.get('logic.button_use_or_prove_mode')
    symbol = button_symbol(name)
    if name == 'or':
        symbol = '∨' + ' (' + translate('OR') + ')'
    elif name == 'and':
        symbol = '∧' + ' (' + translate('AND') + ')'

    current_name = ""
    if mode == 'display_unified':
        current_name = _("the '{}' button")
    elif mode == 'display_switch' and use_or_prove == 'prove':
        current_name = _("the '{}' button in prove mode")
    elif mode == 'display_both' and use_or_prove == 'prove':
        current_name = _("the 'prove {}' button")
    elif mode == 'display_switch' and use_or_prove == 'use':
        current_name = _("the '{}' button in use mode")
    elif mode == 'display_both' and use_or_prove == 'use':
        current_name = _("the 'use {}' button")
    # Translate string, e.g. "the '{}' button", and then incorporate symbol
    return tr(current_name).format(symbol)


use = dict()
prove = dict()

prop_types = {"forall": _("universal property"),
              "exists": _("existential property"),
              "implies": _("implication"),
              "and": _("conjunction"),
              "or": _("disjunction"),
              "not": _("negation"),
              "iff": _("logical equivalence"),
              "equal": _("equality"),
              "function": "function"}

phrase = {"this_is": _("This is"),
          "this_property_is": _("This property is"),
          "this_will_become": _("Applying definition {def_name} will turn "
                                "this into"),
          "to_use": _("To use this property"),
          "to_start_proof": _("To start a proof of this property"),
          "to_use_directly": _("To use this property directly"),
          "to_start_proof_directly": _("To start a proof of this property "
                                       "directly"),
          "press": _("press"),
          "pressing": _("pressing"),
          "after_selecting_it": _("after selecting it"),
          "or_drag_element_to_property": (', ', _("or drag the element and "
                                                  "drop it onto the property")),
          "or_drag_premise": (', ', _("or drag the premise and drop it onto "
                                      "the property")),
          "or_drag_to_equality": (', ', _("or drag the property and drop it "
                                          "onto the equality")),
          "or_drag_to_function": (', ', _("or drag the element or the equality "
                                          "and drop it onto the function")),
          "or_drag_to_def": (', ', _("or drag the property and drop it onto "
                                     "the definition")),
          "deaduction": "D∃∀duction"
          }

use["forall"] = (_("{this_is} a universal property, which tells something "
                   "about {every_element_of_type_}."),
                 "{to_use}, {press} {use_forall} {after_selecting_it}.",
                 # "{an_element_of_type_}{or_drag_element_to_property}."),
                 _("{to_use}, you need {an_element_of_type_}. Is "
                   "there any in the context? If not, can you create some?"))


prove["forall"] = (use["forall"][0],
                   _("{to_start_proof}, press {prove_forall}."),
                   # _("Pressing {prove_forall} will introduce an element of {"
                   #   "type_} in the context, and simplify the target.<br>"
                   _("It is generally a good idea to simplify the target as "
                     "much as possible by introducing all variables and "
                     "hypotheses in the context."))

use["implies"] = (_("{this_is} an implication, which asserts that some property"
                    " P, the <b>premise</b>:<CENTER>{ch0},</CENTER>"
                    " implies some other property Q, the <b>conclusion</b>:"
                    "<CENTER>{ch1}.<CENTER>"),
                  _("{to_use}, {press} {use_implies} {after_selecting_it}"
                    " and another property which match the premise"
                    + "{or_drag_premise}" + "." + "<p>" +
                    "If the premise is not in the context, you can start "
                    "proving it by selecting only this implication"
                    " and {pressing} " + "{use_implies}" + "." + "</p>"),
                  _("{to_use}, you need property {ch0}. Does it "
                    "appear in the context?"))

prove["implies"] = (use["implies"][0],
                    _("{to_start_proof}, press {prove_implies}."),
                    (prove['forall'][2],  # " ",
                     _('Note that an implication may also be proved by '
                       'contraposition (see the "Proof methods" button).')))
# "Pressing {prove_implies} will introduce the premise in "
#                       "the context, and the target will become the "
#                       "conclusion.<br>"

use["exists"] = (_("{this_is} an existential property, which asserts the "
                   "existence of {an_element_of_type_} satisfying a precise "
                   "property."),
                 _("{to_use}, just press {use_exists}."),
                 "")

prove["exists"] = (use["exists"][0],
                   _("{to_start_proof}, press {prove_exists} "
                     "to enter an element that satisfies this property."),
                   # "after selecting {an_element_of_type_}."),  # " ",
                   #  _("Then you will have to prove that this element "
                   #      "satisfies the wanted property.")),
                   _("Is there {an_element_of_type_} in the context? If this "
                     "is so, does it suits your needs? If not, how can you "
                     "create some?"))

use["or"] = (_("{this_property_is} a disjunction."),
             _("Press {use_or} to engage in a proof by cases; you "
               "will successively examine the case when {ch0} holds and the "
               "case when {ch1} holds."),
             (_("Would it help you to know which one of the two properties "
                "hold?"),  # + " " +
              _("<p>If so, then you could consider engaging in a proof by "
                "cases.</p>")))


prove["or"] = (use["or"][0],
               _("Press {prove_or} to simplify the goal by deciding "
                 "which one of the two properties you will prove. You may "
                 "forget about the other one!"),
               (_("Do you have enough information in the context to prove one "
                  "of these two properties?"), "<ul><li>",
                _("If this is so, then choose this property with the ∨ (OR) "
                   "button."), "</li><li>",
                _("If not, you should first get more information."),
                "</li></ul>"))

use["and"] = (_("{this_property_is} a conjunction."),
              _("Press {use_and} to separate both properties."),
              "")


prove["and"] = (use["and"][0],
                _("Press {prove_and} to prove separately and "
                  "successively each property."),
                _("Note that you will have to prove <b> both </b> "
                  "properties, as opposed to disjunction for which you may "
                  "choose which property you prove."))

use["not"] = (_("{this_property_is} a negation."),
              _("Press the ¬ (NOT) button to try to simplify the property."),
              "")

prove["not"] = use["not"]

use["not_non_pushable"] = (use["not"][0],
                           _("I do not know how to simplify this negation "
                             "directly."),
                           "")
prove["not_non_pushable"] = use["not_non_pushable"]

use["iff"] = (_("{this_property_is} a logical equivalence."),
                 (_('You can use the ⇔ ("IF AND ONLY IF") button <ul>'),
                  _('<li>to split it into two implications,</li>'),
                  _('<li>or to substitute {ch0} for {ch1}, or vice-versa, '
                    'in the target or in some other property of the context.'
                    '</li></ul>')),
                 "")

prove["iff"] = (use["iff"][0],
                   _('Press the ⇔ ("IF AND ONLY IF") button, to split the '
                     'proof into the proofs of the direct and reverse '
                     'implications. You may also use {prove_and}.'),
                   "")

use['equal'] = (_("{this_is} an equality between two {elements_of_ch0_type}."),
                (_('You may use this equality to substitute {ch0} for '
                   '{ch1}, or vice-versa, in the target or in some other '
                   'property of the context.'),
                 _('<p>To do this, press the "=" ( EQUAL) button after selecting'
                   ' the other property{or_drag_to_equality}.</p>')),
                "")

prove['equal'] = (use['equal'][0], "", "")

use["function"] = (_("{this_is} a function from {ch0} to {ch1}."),
                   (_("You may apply this function to some element of {ch0}, "
                      "or to an equality between two elements of {ch0}."),
                    _("<p>For this, press the ↦ (MAP) button after selecting "
                      "an element or an equality{or_drag_to_function}.</p>")),
                   "")

prove['belong'] = (_("{this_is} a belonging property."),
                   _("There is no obvious way to further simplify this "
                     "target. Maybe you should now work on the context, "
                     "trying to get this property."),
                   "")

use["definition"] = (_('This matches the definition {def_name}.'),
                     _("To apply a definition, "
                       "click on it in the Statements area{or_drag_to_def}."),
                     "")

prove["definition"] = use["definition"]

use["definitions"] = (_('This matches definitions {def_names}.'),
                      use['definition'][1],
                      "")

prove["definitions"] = use["definitions"]

use["goal!"] = (_("This property obviously entails the current goal."),
                (_('Use the "Goal!" button when you think the target is '
                   'obvious from the context.'),
                 _('Maybe {deaduction} will still need a little help...')),
                "")

prove["goal!"] = (_("This target follows obviously from context "
                    "property {solving_obj}."),
                  use['goal!'][1],
                  "")
# use["obvious_goal!"] = (_("This property is exactly the current goal."),
#                         use['goal!'][1], use['goal!'][2])
#
#
# prove["obvious_goal!"] = (_("This target is identical to context "
#                           "property {solving_obj}."),
#                           prove['goal!'][1], prove['goal!'][2])

become = _("Applying definition {def_name} will turn this into")
implicit_dic = {"{this_is}": become,
                "{this_property_is}": become,
                "to_use": "to_use_directly",
                "to_start_proof": "to_start_proof_directly"}


def make_implicit(msg: str) -> str:
    """
    Rephrase msg to become meaningful in an implicit def context.        
    """
    for key, value in implicit_dic.items():
        msg = msg.replace(key, translate(value))
    return msg


def conc_n_trans(msgs) -> str:
    """
    msgs is either s string, or a tuple of strings.
    """

    joining_str = ' '  # or '<br>' for line breaks
    msg = (joining_str.join([translate(msg) for msg in msgs])
           if isinstance(msgs, tuple) else translate(msgs))
    return msg


def get_help_msgs(key: str, target=False) -> []:
    """
    Return the content of the use and prove dict after concatenation into 3
    msgs, and translations.
    """
    dic = prove if target else use
    msgs = dic.get(key, [])
    tr_msgs = []
    for msg in msgs:
        tr_msgs.append(conc_n_trans(msg))
    return tr_msgs


# TODO:
#  - formule atomique à montrer (appartenance, inégalité, négation d'un truc
#    élémentaire, etc)
#  - elements (comment les utiliser ?)
#  - This can also be used for substitution with the = / <=> button
#    (or for implication with the => button).
#  Et surtout, erreurs --> bouton aide


