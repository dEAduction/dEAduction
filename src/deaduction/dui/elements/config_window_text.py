"""
# config_window_text.py : text for config_window module
    

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 07 2021 (creation)
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


# Also serves for translations
# We do not want translation at init but on the spot
# But we want poedit to mark those str for translation
def _(msg):
    return msg


PRETTY_NAMES = {
    'Display': _("Display"),
    'Logic': _("Logic"),
    'Functionalities': _("Functionalities"),
    'Language': _("Language"),
    'Advanced': _("Advanced"),
    "i18n.select_language": _("Select language"),
    "en": "English",
    'fr_FR': "Français",
    'no_language': "English",
    'display.target_display_on_top': _('Target display on top'),
    'display.target_font_size': _("target font size"),
    'others.course_directory': _('Set directory for choosing courses'),
    'logs.display_level': _('Level of logs'),
    'display.symbols_AND_OR_NOT_IMPLIES_IFF_FORALL_EXISTS_EQUAL':
                                    _("Symbols for buttons ∧ ∨ ¬ ⇒ ⇔ ∀ ∃ ="),
    'display.display_success_messages': _("Display success messages"),
    'logic.color_for_dummy_variables': _("Color for dummy variables"),
    'logic.color_for_used_properties': _("Color for used properties"),
    'functionality.target_selected_by_default': _("Target selected by "
                                                  "default"),
    'functionality.allow_proof_by_sorry': _("Allow proof by sorry"),
    # 'functionality.': _(""),
    'logs.save_journal': _("Save journal"),
    'None': _('None')
}
