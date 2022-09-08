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

# import deaduction.pylib.config.vars as cvars
# from deaduction.pylib.math_display.utils import replace_dubious_characters


# We do not want translation at init but on the spot
# But we want poedit to mark those str for translation
# And we want to remember _ for translation à la volée
# (see def get_help_msg() below)
global _

tr = _


def translate(string):
    return tr(string) if string else ""


def _(msg):
    return msg


def single_to_every(an_object: str) -> str:
    """
    Replace "an object", e.g. "an element", by "every object", e.g. "every
    element".
    """
    from deaduction.pylib.math_display.display_data import every
    for key, value in every.items():
        if an_object.find(key) != -1:
            every_object = an_object.replace(key, value)
            return every_object


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
                 _("{to_use}, press the ∀ button after selecting "
                   "{an_element_of_type_}{or_drag_element_to_property}."),
                 _("{to_use}, you need {an_element_of_type_}. Is "
                   "there any in the context? If not, can you create some?"))


prove["forall"] = (use["forall"][0],
                   _("{to_start_proof}, press the ∀ "
                     "button."),
                   # _("Pressing the ∀ button will introduce an element of {"
                   #   "type_} in the context, and simplify the target.<br>"
                   _("It is generally a good idea to simplify the target as "
                     "much as possible by introducing all variables and "
                     "hypotheses in the context."))

use["implies"] = (_("{this_is} an implication, which asserts that some property"
                    " P:<CENTER>{ch0},</CENTER>"
                    "the <em>premise</em>, implies some other property "
                    "Q:<CENTER>{ch1},<CENTER>"
                    " the <em>conclusion</em>."),
                  _("{to_use}, press the ⇒ button after selecting "
                    "another property which match the premise"
                    "{or_drag_premise}."),
                  _("{to_use}, you need property {ch0}. Does it "
                    "appear in the context?"))

prove["implies"] = (use["implies"][0],
                    _("{to_start_proof}, press the ⇒ button."),
                    (prove['forall'][2],  # " ",
                     _('Note that an implication may also be proved by '
                       'contraposition (see the "Proof methods" button).')))
# "Pressing the ⇒ button will introduce the premise in "
#                       "the context, and the target will become the "
#                       "conclusion.<br>"

use["exists"] = (_("{this_is} an existential property, which asserts the "
                   "existence of {an_element_of_type_} satisfying a precise "
                   "property."),
                 _("{to_use}, just press the ∃ button."),
                 "")

prove["exists"] = (use["exists"][0],
                   (_("{to_start_proof}, press the ∃ button "
                      "after selecting {an_element_of_type_}."),  # " ",
                    _("Then you will have to prove that this element "
                        "satisfies the wanted property.")),
                   _("Is there {an_element_of_type_} in the context? If this "
                     "is so, does it suits your needs? If not, how can you "
                     "create some?"))

use["or"] = (_("{this_property_is} a disjunction."),
             _("Press the ∨ (OR) button to engage in a proof by cases; you "
               "will successively examine the case when {ch0} holds and the "
               "case when {ch1} holds."),
             (_("Would it help you to know which one of the two properties "
                "hold?"),  # + " " +
              _("If so, then you could consider engaging in a proof by "
                "cases.")))


prove["or"] = (use["or"][0],
               _("Press the ∨ (OR) button to simplify the goal by deciding "
                 "which one of the two properties you will prove. You may "
                 "forget about the other one!"),
               (_("Do you have enough information in the context to prove one "
                  "of these two properties?"), "<ul><li>",
                _("If this is so, then choose this property with the ∨ (OR) "
                   "button."), "</li><li>",
                _("If not, you should first get more information."),
                "</li></ul>"))

use["and"] = (_("{this_property_is} a conjunction."),
              _("Press the ∧ (AND) button to separate both properties."),
              "")


prove["and"] = (use["and"][0],
                _("Press the ∧ (AND) button to prove separately and "
                  "successively each property."),
                _("Note that you will have to prove <em> both </em> "
                  "properties, as opposed to disjunction for which you may "
                  "choose which property you prove."))

use["not"] = (_("{this_property_is} a negation."),
              _("Press the ¬ (NOT) button to try to simplify the property."),
              "")

prove["not"] = use["not"]

use[_("iff")] = (_("{this_property_is} a logical equivalence."),
                 (_('You can use the ⇔ ("IF AND ONLY IF") button <ul>'),
                  _('<li>to split it into two implications,</li>'),
                  _('<li>or to substitute {ch0} for {ch1}, or vice-versa, '
                    'in the target or in some other property of the context.'
                    '</li></ul>')),
                 "")

prove[_("iff")] = (use["iff"][0],
                   _('Press the ⇔ ("IF AND ONLY IF") button, to split the '
                     'proof into the proofs of the direct and reverse '
                     'implications. You may also use the ∧ (AND) button.'),
                   "")

use['equal'] = (_("{this_is} an equality between two {elements_of_ch0_type}."),
                (_('You may use this equality to substitute {ch0} for '
                   '{ch1}, or vice-versa, in the target or in some other '
                   'property of the context.'),
                 _('To do this, press the "=" ( EQUAL) button after selecting'
                   ' the other property{or_drag_to_equality}.')),
                "")

prove['equal'] = (use['equal'][0], "", "")

use["function"] = (_("{this_is} a function from {ch0} to {ch1}."),
                   (_("You may apply this function to some element of {ch0}, "
                      "or to an equality between two elements of {ch0}."),
                    _("For this, press the ↦ (MAP) button after selecting "
                      "an element or an equality{or_drag_to_function}.")),
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

use["goal!"] = (_("This property seems to solve the current goal."),
                (_('Use the "Goal!" button when you think the target is '
                   'obvious from the context.'),
                 _('Maybe {deaduction} will still need a little help...')),
                "")

prove["goal!"] = (_("This target seems to be obvious from context "
                    "property {solving_obj}."),
                  use['goal!'][1],
                  "")


def conc_n_trans(msgs) -> str:
    """
    msgs is either s string, or a tuple of strings.
    """
    msg = (" ".join([translate(msg) for msg in msgs])if isinstance(msgs, tuple)
           else translate(msgs))
    return msg


def get_helm_msgs(key: str, target=False) -> []:
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


# use["unfold_implicit_def"] = _("To see this property explicitly as a {"
#                                "prop_type}, you may apply definition {"
#                                "def_name} by clicking on it in the Statements "
#                                "area.")

# TODO:
#  - bounded quantification
#  - Defs implicites qui sont des forall : suggérer aussi d'aller voir la déf
#  - formule atomique à montrer (appartenance, inégalité, négation d'un truc
#    élémentaire, etc)
#  - elements (comment les utiliser ?)
#  - This can also be used for substitution with the = / <=> button
#    (or for implication with the => button).
#  Et surtout, erreurs --> bouton aide

#
# use = (_(""),
#        _(""),
#        _(""))
#
#
# use = (_(""),
#        _(""),
#        _(""))
#
#
# use = (_(""),
#        _(""),
#        _(""))
#
#
# use = (_(""),
#        _(""),
#        _(""))
#
#
# use = (_(""),
#        _(""),
#        _(""))
#
#
# use = (_(""),
#        _(""),
#        _(""))
#
#
# use = (_(""),
#        _(""),
#        _(""))


