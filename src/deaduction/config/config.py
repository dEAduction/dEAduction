"""
# config.py : handle the configuration and the global variables
    
The configuration is stored in config.ini, IN THE SAME DIRECTORY

Use: from deaduction.config.config import user_config, Global
and then: allow_proof_by_sorry = user_config.getboolean('allow_proof_by_sorry')


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
import configparser
import logging
import os
from pathlib import Path
import gettext

log = logging.getLogger(__name__)


################################
# A class for global variables #
################################
class Global:
    """
    all Python global vars should be given throught attrobutes of instances
     of this class
    Example if syntax =
    EXERCISE.PROPERTY_COUNTER
    """
    pass


EXERCISE = Global()  # class for global variables whose lifetime = exercise
COURSE = Global()  # class for global variables whose lifetime = 1 course
SESSION = Global()  # class for global variables whose lifetime = a session

################################
# Reading configuration values #
################################
config = configparser.ConfigParser()

# reading file config.ini, assuming it is in the same directory as config.py
config_file_path = os.path.join(os.path.dirname(__file__)) + '/config.ini'
config.read(config_file_path)

# in case no config file is found
try:
    user_config = config['USER']
except KeyError:
    try:
        user_config = config['DEFAULT']
    except KeyError:
        config['DEFAULT'] = {'alert_target_solved': True,
                             'depth_of_unfold_statements': 1,
                             'allow_proof_by_sorry': True,
                             'show_lean_name_for_statements': False
                             }
        config['USER'] = {}
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)
        user_config = config['USER']


################
# Set language #
################
available_languages = user_config.get('available_languages')
available_languages = available_languages.split(', ')
select_language = user_config.get('select_language')

if available_languages == '':
    available_languages = ['en']
if select_language == '':
    select_language = 'en'

# done = False
# for key_ in ['LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG']:
#     if key_ in os.environ.keys():
#         os.environ[key_] = select_language
#         done = True
# if not done:
#     os.environ['LANG'] = select_language

log.debug(f"Setting language to {select_language}")
language_dir_path = Path.cwd() / 'share/locales'
#gettext.bindtextdomain("deaduction", str(language_dir_path))
#gettext.textdomain("deaduction")
fr = gettext.translation('deaduction',
                         localedir=language_dir_path,
                         languages=[select_language])
fr.install()
_ = fr.gettext
# _ = gettext.gettext

test_language = gettext.gettext("Proof by contrapositive")
log.debug(f"test: {test_language}")

###############################################################
# set tooltips and text button HERE FOR POTENTIAL TRANSLATION #
###############################################################
# Logic and proof Buttons tooltips
tooltips = {
    'tooltip_and':
        _("""• Split a property 'P AND Q' into the two properties 'P', 'Q'
• Inversely, assembles 'P' and 'Q' to get 'P AND Q'"""),
    'tooltip_or':
        _("""• Prove 'P OR Q' by proving either 'P' or 'Q'
• Use the property 'P OR Q' by splitting the cases when P is
True and Q is True"""),
    'tooltip_not':
        _("""Try to simplify the property 'NOT P'"""),
    'tooltip_implies':
        _("""Prove 'P ⇒ Q' by assuming 'P', and proving 'Q'"""),
    'tooltip_iff':
        _("""Split 'P ⇔ Q' into two implications"""),
    'tooltip_forall':
        _("""Prove '∀ a, P(a)' by introducing 'a'"""),
    'tooltip_exists':  # TODO: possibility to 'APPLY' '∃ x, P(x)'
        _("""Prove '∃ x, P(x)' by specifying some 'x' and proving P(x)"""),
    'tooltip_apply':
        _("""• Apply to a property '∀ a, P(a)' and some 'a' to get 'P(a)' 
• Apply to a property 'P ⇒ Q' and 'P' to get 'Q'
• Apply to an equality to substitute in another property
• Apply a function to an element or an equality"""),
    'tooltip_proof_methods':
        _("""Choose some specific proof method"""),
    'tooltip_choice':
        _(
            "From a property '∀ a ∈ A, ∃ b ∈ B, P(a,b)', get a function from A to B"),
    'tooltip_new_object':
        _("""• Create a new object (e.g. 'f(x)' from 'f' and 'x')
• Create a new subgoal (a lemma) which will be proved, and added to the context"""
          ),
    'tooltip_assumption':
        _(
            """Terminate the proof when the target is obvious from the context""")
}
# decentralized apply buttons
tooltips_apply = {}  # TODO

# Text for buttons
buttons = {
    'logic_button_texts': _("AND, OR, NOT, IMPLIES, IFF, FORALL, EXISTS, "
                            "APPLY"),
    'proof_button_texts': _(
        "PROOF METHODS, CREATE FUNCTION, NEW OBJECT, QED")
}
# sad thoughts for "¯\_(ツ)_/¯", I loved you so much...

config['DEFAULT'].update(tooltips)
config['DEFAULT'].update(tooltips_apply)
config['DEFAULT'].update(buttons)


if __name__ == "__main__":
    # boolean = user_config.getboolean('fold_statements')
    # text_boolean = user_config.get('fold_statements')
    # print(boolean, text_boolean)

    #####################
    # Print config file #
    #####################
    for sect in config.sections():
        print('Section:', sect)
        for k, v in config.items(sect):
            print(f' {k} = {v}')
