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


replace_missing = _('Replace missing symbols: ℕ (N), ℤ (Z), ℚ (Q), ℝ (R), '
                    '𝒫 (P), ↦ (->)')

PRETTY_NAMES = {
    'functionality': _("Functionalities"),
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
    'display.main_font_size': _("Main font size"),
    'display.statements_font_size': _("Font size for statements"),
    'display.tooltips_font_size': _("Tooltips font size"),
    'display.target_font_size': _("Target font size"),
    'display.proof_tree_font_size': _('Font size for global proof view'),
    'others.course_directory': _('Set directory for choosing courses'),
    'logs.display_level': _('Level of logs'),
    'display.use_symbols_for_logic_button': _("Use symbol for logic buttons"),
    'display.font_size_for_symbol_buttons': _("Font size for symbol buttons"),
    # 'display.linux_font_size_for_symbol_buttons': _("Font size for symbol "
    #                                                 "buttons"),
    # 'display.darwin_font_size_for_symbol_buttons': _("Font size for symbol "
    #                                                  "buttons"),
    # 'display.windows_font_size_for_symbol_buttons': _("Font size for symbol "
    #                                                  "buttons"),
    'display.display_success_messages': _("Display success messages"),
    'display.color_for_selection': _("Color for selection"),
    'display.math_font_file': _("Maths fonts"),
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
    'functionality.auto_solve_inequalities_in_bounded_quantification':
        _("Try to silently prove ε>0 when applying '∀ε>0'"),
    'functionality.ask_to_prove_premises_of_implications':
        _("Ask to prove 'P' when 'P ⇒ Q' in context"),
    'logs.save_journal': _("Save journal"),
    'display.dubious_characters': replace_missing,
    'display.short_buttons_line': _('Split logic buttons into two lines'),
    'functionality.drag_statements_to_context': _("Drag statements to context"),
    'functionality.drag_and_drop_in_context': _("Drag and drop in context"),
    'functionality.drag_context_to_statements': _("Drag context to statements"),
    'None': _('None'),
    'Beginner': _("Beginner"),
    "Intermediate": _("Intermediate"),
    "Expert": _("Expert"),
    "logic.use_bounded_quantification_notation":
        _("Denote ∀x>0, ... instead of ∀x∈ℝ, (x>0 ⇒ ...)")
}
