"""
# config_window.py : a window for user config #

To add a parameter for config:
- add an entry to the relevant CONFIG sub-dictionary,
- add an entry in config_window_text.PRETTY_NAMES for translation,
- if relevant, add an entry in SETTINGS_AFFECTING_UI so that UI is updated
when the value of the parameter is modified
- make sure that the parameter's value is taken into account on the spot
when UI is updated.

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

# TODO:
#  - remove useless "update" functions
#  - add color...
#  - add restore factory values


import sys
import logging
from importlib import reload

from PySide2.QtCore import (    Signal,
                                Slot)
from PySide2.QtWidgets import ( QApplication,
                                QDialog,
                                QTabWidget,
                                QCheckBox,
                                QComboBox,
                                QLineEdit,
                                QVBoxLayout,
                                QFormLayout,
                                QDialogButtonBox,
                                QPushButton,
                                QFileDialog)

from deaduction.pylib.config.i18n import init_i18n
import deaduction.pylib.config.vars      as      cvars
from deaduction.pylib                            import logger


from .config_window_text import PRETTY_NAMES

log = logging.getLogger(__name__)
global _

######################
# Settings to be set #
######################
# TO ADD A NEW SETTING: cf file documentation

CONFIGS = dict()
# Each value of CONFIGS is a list of tuples:
# (1) string = ref in cvars,
# (2) list of predefined values (or None),
# (3) bool: False if freeze (not implemented yet)
CONFIGS["Display"] = [
    ("display.target_display_on_top", None, True),  # bool
    ("display.target_font_size", None, True),
    ("display.main_font_size", None, True),
    ("display.tooltips_font_size", None, True),
    ('display.use_symbols_for_logic_button', None, True),
    ('display.font_size_for_symbol_buttons', None, True)
    # ('display.font_for_mathematics', "font", True)
    ]
# ('display.mathematics_font', None, True),
# ('display.symbols_AND_OR_NOT_IMPLIES_IFF_FORALL_EXISTS_EQUAL_MAP',
#  None, False)

CONFIGS["Logic"] = [
    ("display.display_success_messages", None, True),
    ("logic.use_color_for_variables", None, True),
    ("logic.use_color_for_dummy_variables", None, True)]

CONFIGS['Functionalities'] = [
    ('functionality.target_selected_by_default', None, True),
    ('functionality.allow_proof_by_sorry', None, True),  # tested
    # ('functionality.expanded_apply_button', None, False),
    ('functionality.automatic_intro_of_variables_and_hypotheses', None, True),
    ('functionality.allow_implicit_use_of_definitions', None, True)]

CONFIGS["Language"] = [("i18n.select_language", ["en", "fr_FR"], True)]

CONFIGS["Advanced"] = [
    ('others.course_directory', 'dir', True),
    ('logs.save_journal', None, True),  # checked, untested
    ('logs.display_level', ['debug', 'info', 'warning'], True),
    ('functionality.save_solved_exercises_for_autotest', None, True)]

SETTINGS_AFFECTING_UI = ["display.target_display_on_top",
                         "display.target_font_size",
                         "display.main_font_size",
                         "display.tooltips_font_size",
                         "logic.use_color_for_variables",
                         "logic.use_color_for_dummy_variables",
                         "EXISTS_EQUAL_MAP",
                         'display.use_symbols_for_logic_button',
                         'display.font_size_for_symbol_buttons',
                         'logic.color_for_used_properties',
                         'functionality.allow_proof_by_sorry',
                         'functionality.allow_implicit_use_of_definitions',
                         "i18n.select_language"
                         ]


class ConfigMainWindow(QDialog):
    """
    A window for handling configuration.
    Uses one tabs for each key in CONFIGS, and creates a
    corresponding ConfigWindow.
    """
    applied = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setModal(True)
        self.__windows = []  # List of sub-windows, one for each tab

        self.setWindowTitle(_("Preferences"))
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.__tabs = QTabWidget()
        for tab_name in CONFIGS:
            window = ConfigWindow(tab_name)
            self.__tabs.addTab(window, _(tab_name))
            self.__windows.append(window)
        layout.addWidget(self.__tabs)

        # Save preferences btn
        self.save_btn = QCheckBox(_("Save preferences for next session"))
        layout.addWidget(self.save_btn)

        # Buttons Apply, Cancel, OK
        button_box = QDialogButtonBox()

        # button_box.setStandardButtons(QDialogButtonBox.Ok) |
                                      # QDialogButtonBox.Cancel)
        # button_box.setStandardButtons()
        self.ok_btn = button_box.addButton(QDialogButtonBox.Ok)
        self.cancel_btn = button_box.addButton(QDialogButtonBox.Cancel)
        self.apply_btn = button_box.addButton(QDialogButtonBox.Apply)

        self.ok_btn.setText(_("Ok"))
        self.cancel_btn.setText(_("Cancel"))
        self.apply_btn.setText(_("Apply"))
        # self.save_btn = button_box.addButton(QDialogButtonBox.Save)

        layout.addWidget(button_box)

        button_box.rejected.connect(self.cancel)
        button_box.clicked.connect(self.clicked)
        button_box.accepted.connect(self.accept)

    def clicked(self, btn):
        """
        Called when a button is clicked, e.g. the "Apply" button.
        """
        if btn == self.apply_btn:
            self.apply()

    def save(self):
        """
        Store new settings in  cvars and save cvars in the config.toml file
        """
        # Store new settings in cvars
        for setting in self.modified_settings:
            cvars.set(setting, self.modified_settings[setting])
        # Save
        log.info("Saving preferences in config.toml")
        cvars.save()

    def apply(self):
        """
        Store new settings in cvars, and emit the applied signal,
        so that the ui can make the relevant changes.
        """
        # store new settings in cvars
        for setting in self.modified_settings:
            cvars.set(setting, self.modified_settings[setting])
        ##########################
        # Specific modifications #
        ##########################
        if "i18n.select_language" in self.modified_settings:
            init_i18n()  # UI needs to be updated
            import deaduction.pylib.math_display.display_data
            reload(deaduction.pylib.math_display.display_data)

        if 'logs.display_level' in self.modified_settings:
            display_level = self.modified_settings['logs.display_level']
            logger.configure(display_level)

        # UI modifications will be applied by ExerciseMainWindow
        pertinent_ui_settings = [setting for setting in self.modified_settings
                                 if setting in SETTINGS_AFFECTING_UI]
        self.applied.emit(pertinent_ui_settings)

    def cancel(self):
        """
        Restore initial values and close window.
        """
        # Adapt modified_settings (= those settings which have been modified
        # AND applied, so after cancelling they will have to be modified back)
        for window in self.__windows:
            new_modified_settings = dict()
            for setting in window.modified_settings:
                real_setting = cvars.get(setting)
                if real_setting != window.initial_settings[setting]:
                    new_modified_settings[setting] = \
                        window.initial_settings[setting]
                    # if modified setting has been applied, it will have to
                    # be modified back
            window.modified_settings = new_modified_settings
        # Restore initial settings
        self.apply()  # Apply backwards
        # for setting in self.initial_settings:
        #     cvars.set(setting, self.initial_settings[setting])
        # Emit the 'applied' signal to modify back in case modified settings
        # had been applied before cancelling
        # self.applied.emit(self.modified_settings)
        # Bye
        self.reject()

    def accept(self):
        # print("accept")
        self.apply()
        if self.save_btn.isChecked():
            # print("saving")
            self.save()
        self.close()

    @property
    def initial_settings(self):
        """
        Union of initial_settings of self's sub-windows.
        """
        initial_settings = dict()
        for window in self.__windows:
            initial_settings.update(window.initial_settings)
        return initial_settings

    @property
    def modified_settings(self):
        """
        Union of initial_settings of self's sub-windows.
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
            setting_initial_value = cvars.get(setting, default_value="none")
            if setting_initial_value == "none":
                setting_initial_value = None  # Avoid KeyError
            # print(setting, setting_list, setting_initial_value)
            # if setting_initial_value:
            self.initial_settings[setting] = setting_initial_value
            title = _(PRETTY_NAMES[setting]) if setting in PRETTY_NAMES \
                else get_pretty_name(setting)
            title = title + _(":")

            # ───────── Case of file: browse directories button ───────── #
            if setting_list == 'dir':
                widget = QPushButton(_("Browse directories"), self)
                widget.clicked.connect(self.browse_dir)
                widget.setting = setting

            # ───────── Case of choice into a list: combo box ─────────
            elif setting_list:
                pretty_setting_list = [_(PRETTY_NAMES[setting])
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

    @Slot()
    def browse_dir(self):
        widget = self.sender()
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            directory = dialog.selectedFiles()[0]
            self.modified_settings[widget.setting] = directory

    @Slot()
    def check_box_changed(self):
        cbox = self.sender()
        self.modified_settings[cbox.setting] = bool(cbox.checkState())

    @Slot()
    def line_edit_changed(self):
        line_edit = self.sender()
        self.modified_settings[line_edit.setting] = line_edit.text()


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
