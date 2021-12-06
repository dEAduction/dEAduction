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
    'display.use_symbols_for_logic_button': _("Use symbol for logic buttons"),
    'display.font_size_for_symbol_buttons': _("Font size for symbol buttons"),
    'display.display_success_messages': _("Display success messages"),
    'logic.use_color_for_variables': _("Use color for variables"),
    'logic.use_color_for_dummy_variables': _("Use color for dummy variables"),
    'logic.use_color_for_applied_properties': _("Use color for applied "
                                                "properties"),
    'functionality.target_selected_by_default': _("Target selected by "
                                                  "default"),
    'functionality.allow_proof_by_sorry': _("Allow proof by sorry"),
    'functionality.allow_implicit_use_of_definitions':
        _("Allow implicit use of definitions"),
    'functionality.automatic_intro_of_variables_and_hypotheses':
        _("Automatic intro of variables and hypotheses"),
    'functionality.automatic_intro_of_exists':
        _("Automatic intro of existence properties"),
    'functionality.save_solved_exercises_for_autotest':
        _("Save exercises for autotest"),
    'logs.save_journal': _("Save journal"),
    'display.main_font_size': _("Main font size"),
    'display.tooltips_font_size': _("Tooltips font size"),
    'display.dubious_characters': _('Replace missing characters') +
                              ': ℕ (N), ℤ (Z), ℚ (Q), ℝ (R), 𝒫 (P), ↦ (->)',
    'None': _('None')
}
