"""
# config_window.py : a window for user config #

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

import sys

from PySide2.QtCore import (    Signal,
                                Slot,
                                QEvent )
from PySide2.QtWidgets import ( QApplication,
                                QDialog,
                                QTabWidget,
                                QCheckBox,
                                QComboBox,
                                QLineEdit,
                                QVBoxLayout,
                                QFormLayout,
                                QDialogButtonBox)

from deaduction.pylib.config.i18n       import   _
import deaduction.pylib.config.vars      as      cvars

# TODO: cancel process. Need to be able to copy cvars.


######################
# Settings to be set #
######################

CONFIGS = dict()
CONFIGS["Display"] = [("display.target_display_on_top", None),  # bool
                      ("display.target_font_size", None),
                      ("display.context_font_size", None),
                      ('display.tooltips_font_size', None),
                      ('display.mathematics_font', None),
                      ('display.use_logic_button_symbols', None)]       # str
CONFIGS["Logic"] = [
    ('logic.color_for_used_properties', ['None', 'red', 'blue', 'purple']),
    ('logic.color_for_dummy_variables', ['None', 'red', 'blue', 'purple'])]
CONFIGS['Functionalities'] = [
    ('functionality.target_selected_by_default', None),
    ('functionality.allow_proof_by_sorry', None),
    ('functionality.expanded_apply_button', None),
    ('functionality.allow_forall_with_implicit_universal_prop', None),
    ('functionality.treat_intersections_as_ands', None),
    ('functionality.treat_unions_as_ors', None)]

CONFIGS["Language"] = [("i18n.select_language", ["en", "fr_FR"])]
CONFIGS["Advanced"] = [
    ('journal.save', None),
    ('logs.display_level', ['error', 'info', 'debug'])]

# Also serves as for translations
PRETTY_NAMES = {
    'Display': _("Display"),
    'Logic': _("Logic"),
    'Functionalities': _("Functionalities"),
    'Language': _("Language"),
    'Advanced': _("Advanced"),
    "en": "English",
    'fr_FR': "Français",
    'target_display_on_top': _('Target display on top')}


class ConfigMainWindow(QDialog):
    """
    A window for handling configuration.
    Uses one tabs for each key in CONFIGS, and creates a
    corresponding ConfigWindow.
    """
    def __init__(self):
        super().__init__()
        self.cvars = cvars
        # Save cvars for cancellation
        self.__initial_cvars = self.cvars.copy()

        self.setWindowTitle(_("Preferences"))
        layout = QVBoxLayout()
        self.setLayout(layout)
        tabs = QTabWidget()
        for tab_name in CONFIGS:
            window = ConfigWindow(tab_name)
            tabs.addTab(window, tab_name)
        layout.addWidget(tabs)
        self.button_box = QDialogButtonBox()
        self.button_box.setStandardButtons(QDialogButtonBox.Ok |
                                   QDialogButtonBox.Apply |
                                   QDialogButtonBox.Cancel)
        layout.addWidget(self.button_box)
        self.button_box.accepted.connect(self.OK)
        self.button_box.rejected.connect(self.cancel)

        # TODO: add save/restore initial values
        # TODO: connect apply to something!
        # TODO: apply changes

    def cancel(self):
        """
        Restore initial values and close window.
        """
        # TODO: less radical method, keep track of modified vars
        self.cvars.restore(self.__initial_cvars)
        self.reject()

    def OK(self):
        """
        Apply changes and close window.
        """
        self.apply()
        self.accept()

    def apply(self):
        """
        Apply changes by updating ui.
        """
        # TODO


class ConfigWindow(QDialog):
    """
    A window corresponding to a group of settings, one for each key in CONFIGS,
    e.g. 'Display'.
    For each entry in the settings list (e.g. CONFIGS['Display']), creates
        - a combo box for a list of choices,
        - a checkbox for a boolean choice
        - a QLineEdit for a string choice.
    """
    # TODO: add integer choice?

    def __init__(self, name):
        super().__init__()
        settings = CONFIGS.get(name)
        layout = QFormLayout()
        for setting, setting_list in settings:
            setting_initial_value = cvars.get(setting)
            print(setting, setting_list, setting_initial_value)
            title = PRETTY_NAMES[setting] if setting in PRETTY_NAMES \
                else get_pretty_name(setting)
            title = title + _(":")
            # ───────── Case of choice into a list: combo box ─────────
            if setting_list:
                pretty_setting_list = [PRETTY_NAMES[setting]
                                       if setting in PRETTY_NAMES
                                       else setting
                                       for setting in setting_list]
                widget = QComboBox()
                widget.addItems(pretty_setting_list)
                widget.setting_list = setting_list
                widget.setting = setting
                # more_layout = QFormLayout()
                # more_layout.addRow(title, widget)
                if setting_initial_value:
                    initial_index = setting_list.index(setting_initial_value)
                    widget.setCurrentIndex(initial_index)

                widget.currentIndexChanged.connect(self.combo_box_changed)

            # ───────── Case of bool: check box ─────────
            elif isinstance(setting_initial_value, bool):
                widget = QCheckBox()
                widget.setting = setting

                widget.toggled.connect(self.check_box_changed)

            # ───────── Case of str: QLineEdit ─────────
            elif isinstance(setting_initial_value, str):
                widget = QLineEdit()
                widget.setting = setting
                if setting_initial_value:
                    initial_string = setting_initial_value
                    widget.setText(initial_string)

                widget.textChanged.connect(self.line_edit_changed)
            else:
                widget = None

            print("Adding wdgt", widget)
            layout.addRow(title, widget)

        self.setLayout(layout)

    # Handle choices
    @Slot()
    def combo_box_changed(self):
        combo_box = self.sender()
        cvars.set(combo_box.setting, combo_box.setting_list[
            combo_box.currentIndex()])
        print("New setting: ", combo_box.setting, combo_box.setting_list[
            combo_box.currentIndex()])

    @Slot()
    def check_box_changed(self):
        cbox = self.sender()
        cvars.set(cbox.setting, bool(cbox.checkState()))
        print("New setting: ", cbox.setting, bool(cbox.checkState()))

    @Slot()
    def line_edit_changed(self):
        line_edit = self.sender()
        cvars.set(line_edit.setting, line_edit.text())
        print("New setting: ", line_edit.setting, line_edit.text())


def get_pretty_name(setting: str) -> str:
    """
    e.g. "i18n.select_language"  -> "Select language"
    """
    _, name = setting.split('.')
    name = name.replace('_', ' ').capitalize()
    return name


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigMainWindow()
    window.show()
    sys.exit(app.exec_())
