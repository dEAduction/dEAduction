"""
#######################################################
# help_msgs.py : set msgs for help on context objects #
#######################################################

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
def _(msg):
    return msg


use = dict()
prove = dict()

# Param children[0]
use["forall"] = (_("This is a universal property, which tells something about "
                 "every element of {}."),
                 _("To use this property, press the ∀ button after selecting "
                   "an element of {}."),
                 _("To use this property, you need some element of {}. Is "
                   "there any in the context? If not, can you create some?"))


prove["forall"] = (_("This is a universal property, which tells something "
                     "about every element of {}."),
                   _("To start a proof of this property, press the ∀ "
                     "button."),
                   "")

use_exists = (_("This is an existential property, which asserts the "
                "existence of an element of {} satisfying a precise "
                "property."),
              _("To use this property, just press the ∃ button."),
              "")

prove_exists = (_("This is an existential property, which asserts the "
                  "existence of an element of {} satisfying a precise "
                  "property."),
                _("To prove this property, press the ∃ button after selecting"
                  "the element of {} that satisfies the wanted property."),
                _("Is there some element of {} in the context? If this is "
                  "so, does it suits your needs? If not, can you create "
                  "some?"))

use_or = (_("This property is a disjunction."),
          _("Press the ∨ (OR) button to engage in a proof by cases; you will "
            "successively examine the case when {} holds and the case when {}"
            "holds."),
          _("Would it help you to know which one of the two properties hold?"
            "If so, then you could consider engaging in a proof by cases."))


prove_or = (use_or[0],
            _("Press the ∨ (OR) button to simplify the goal by deciding which "
              "one of the two properties you will prove. You may forget about"
              "the other one!"),
            _("Do you have enough information in the context to prove one of "
              "these two properties? \\If this is so, then choose this "
              "property with the ∨ (OR) button. \\If not, you should first "
              "get more information (maybe by engaging in a proof by cases)."))

#  ¬
use_and = (_("This property is a conjunction."),
           _("Press the ∧ (AND) button to separate both properties."),
           _(""))


prove_and = (use_and[0],
             _("Press the ∧ (AND) button to prove separately and successively "
               "each property."),
             _("Note that you will have to prove <em> both </em> "
               "properties, as opposed to disjunction for which you may "
               "choose which property you prove."))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


use = (_(""),
       _(""),
       _(""))


