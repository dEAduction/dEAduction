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
                                QEvent)
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
# Each valeu of CONFIGS is a list of tuples:
# (1) srt: ref in cvars,
# (2) list of predefined values (or None),
# (3) bool: False if freeze (not implemented yet)
CONFIGS["Display"] = [("display.target_display_on_top", None, True),  # bool
                      ("display.target_font_size", None, True),
                      ("display.context_font_size", None, True),
                      ('display.tooltips_font_size', None, True),
                      ('display.mathematics_font', None, True),
                      ('display.use_logic_button_symbols', None, True)]       # str
CONFIGS["Logic"] = [
    ('logic.color_for_used_properties', ['None', 'red', 'blue', 'purple'],
     False),
    ('logic.color_for_dummy_variables', ['None', 'red', 'blue', 'purple'],
     False)]
CONFIGS['Functionalities'] = [
    ('functionality.target_selected_by_default', None, True),
    ('functionality.allow_proof_by_sorry', None, True),
    ('functionality.expanded_apply_button', None, False),
    ('functionality.automatic_intro_of_variables_and_hypotheses', None, False),
    ('functionality.allow_forall_with_implicit_universal_prop', None, False),
    ('functionality.treat_intersections_as_ands', None, False),
    ('functionality.treat_unions_as_ors', None, False)]

CONFIGS["Language"] = [("i18n.select_language", ["en", "fr_FR"], True)]
CONFIGS["Advanced"] = [
    ('logs.save_journal', None, True),
    ('logs.display_level', ['error', 'info', 'debug'], True)]

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
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setModal(True)
        self.__windows = []  # List of sub-windows, one for each tab

        self.applied = Signal()

        self.setWindowTitle(_("Preferences"))
        layout = QVBoxLayout()
        self.setLayout(layout)
        tabs = QTabWidget()
        for tab_name in CONFIGS:
            window = ConfigWindow(tab_name)
            tabs.addTab(window, tab_name)
            self.__windows.append(window)
        layout.addWidget(tabs)

        # Buttons Apply, Cancel, OK
        button_box = QDialogButtonBox()
        self.apply_btn = QDialogButtonBox.Apply
        self.ok_btn = QDialogButtonBox.Ok
        button_box.setStandardButtons(self.ok_btn |
                                      self.apply_btn |
                                      QDialogButtonBox.Cancel)

        layout.addWidget(button_box)

        button_box.rejected.connect(self.cancel)
        button_box.clicked.connect(self.clicked)
        button_box.accepted.connect(self.accept)

        # TODO: add save/restore initial values
        # TODO: connect apply to something!
        # TODO: apply changes

    def clicked(self, btn):
        """
        Called when a button is clicked.
        Emit the 'applied' signal if needed.
        """
        # ERROR: 'QPushButton' object has no attribute 'ButtonRole'
        # if btn.ButtonRole() == QDialogButtonBox.ApplyRole or \
        #         btn.ButtonRole() == QDialogButtonBox.AcceptRole:
        #     self.applied.emit()

    def cancel(self):
        """
        Restore initial values and close window.
        """
        for window in self.__windows:
            window.modified_settings = dict()
        # for setting in self.initial_settings:
        #     value = self.initial_settings[setting]
        #     cvars.set(setting, value)
        self.reject()

    # def OK(self):
    #     """
    #     Apply changes and close window.
    #     """
    #     self.apply()
    #     self.accept()
    #
    # def apply(self):
    #     """
    #     Apply changes by updating ui.
    #     """
    #     # TODO

    @property
    def initial_settings(self):
        """
        Union of initial_settings of self.subwindows
        """
        initial_settings = dict()
        for window in self.__windows:
            initial_settings.update(window.initial_settings)
        return initial_settings

    @property
    def modified_settings(self):
        """
        Union of initial_settings of self.subwindows
        """
        modified_settings = dict()
        for window in self.__windows:
            modified_settings.update(window.modified_settings)
        return modified_settings


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
        self.initial_settings = dict()
        self.modified_settings = dict()
        settings = CONFIGS.get(name)
        layout = QFormLayout()
        for setting, setting_list, enabled in settings:
            setting_initial_value = cvars.get(setting)
            # print(setting, setting_list, setting_initial_value)
            if setting_initial_value:
                self.initial_settings[setting] = setting_initial_value
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
                if setting_initial_value:
                    initial_index = setting_list.index(setting_initial_value)
                    widget.setCurrentIndex(initial_index)

                widget.currentIndexChanged.connect(self.combo_box_changed)

            # ───────── Case of bool: check box ─────────
            elif isinstance(setting_initial_value, bool):
                widget = QCheckBox()
                widget.setting = setting
                if setting_initial_value:
                    widget.setChecked(setting_initial_value)
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

            # print("Adding wdgt", widget)
            widget.setEnabled(enabled)
            layout.addRow(title, widget)

        self.setLayout(layout)

    # Handle choices
    @Slot()
    def combo_box_changed(self):
        combo_box = self.sender()
        self.modified_settings[combo_box.setting] = combo_box.setting_list[
                                                    combo_box.currentIndex()]
        # cvars.set(combo_box.setting, combo_box.setting_list[
        #     combo_box.currentIndex()])
        # print("New setting: ", combo_box.setting, combo_box.setting_list[
            # combo_box.currentIndex()])

    @Slot()
    def check_box_changed(self):
        cbox = self.sender()
        self.modified_settings[cbox.setting] = bool(cbox.checkState())
        # cvars.set(cbox.setting, bool(cbox.checkState()))
        # print("New setting: ", cbox.setting, bool(cbox.checkState()))

    @Slot()
    def line_edit_changed(self):
        line_edit = self.sender()
        self.modified_settings[line_edit.setting] = line_edit.text()
        # cvars.set(line_edit.setting, line_edit.text())
        # print("New setting: ", line_edit.setting, line_edit.text())


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
