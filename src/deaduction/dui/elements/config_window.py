"""
# config_window.py : a window for user config #

To add a parameter for config:
- add an entry to the relevant CONFIG sub-dictionary,
- add an entry in config_window_text.PRETTY_NAMES for translation,
- if relevant, add an entry in SETTINGS_AFFECTING_UI so that UI is updated
when the value of the parameter is modified. These modified settings are sent to
the ExerciseMainWindow.apply_new_settings() method.
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
                                QRadioButton,
                                QVBoxLayout,
                                QHBoxLayout,
                                QFormLayout,
                                QFrame,
                                QDialogButtonBox,
                                QPushButton,
                                QFileDialog,
                                QMessageBox,
                                QLabel,
                                QSizePolicy)

from deaduction.pylib.config.i18n import init_i18n
import deaduction.pylib.config.vars      as      cvars
from deaduction.pylib                            import logger
from deaduction.dui.primitives.font_config import deaduction_fonts

from deaduction.pylib.math_display import MathDisplay

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
PRE_DEFINED = dict()
# Dictionary whose keys are keys of CONFIGS.

CONFIGS["Display"] = {
    "display.target_display_on_top": (None, True, ""),
    "display.target_font_size": (None, True, ""),
    "display.main_font_size": (None, True, ""),
    "display.statements_font_size": (None, True, ""),
    # "display.proof_tree_font_size": (None, True),  # FIXME: hard to modify
    "display.tooltips_font_size": (None, True, ""),
    'display.use_symbols_for_logic_button': (None, True, ""),
    'display.font_size_for_symbol_buttons': (None, True, ""),
    'display.dubious_characters': (None, True, ""),
    'display.short_buttons_line': (None, False, ""),
    'display.color_for_selection': (None, True, "")
    # ('display.use_system_fonts', None, True),
    # ('display.use_system_fonts_for_maths', None, True),
    # ('display.maths_fonts', ["system", "Latin Modern"], True)
    # ('display.font_for_mathematics', "font", True)
}

# # Font size specific to os:
# os_name = cvars.get('others.os', "linux")
# if os_name:
#     os_name += '_'
# font_size_key = 'display.' + os_name + 'font_size_for_symbol_buttons'
# CONFIGS["Display"].append((font_size_key, None, True))

CONFIGS["Logic"] = {
    "display.display_success_messages": (None, True, ""),
    "logic.button_use_or_prove_mode": (['display_switch', 'display_both',
                                        'display_unified'], True, ""),
    "logic.use_color_for_variables": (None, True,
        _("The variables of the context are displayed in color")),
    "logic.use_color_for_dummy_variables": (None, True,
        _("The dummy variables (bound by a quantifier) are displayed in "
          "color")),
    "logic.use_color_for_applied_properties": (None, True,
        _("The context properties are shaded after the first time they are "
          "used")),
    "logic.use_bounded_quantification_notation": (None, True,
        _("Display properties using bounded quantification"))}

CONFIGS['Functionalities'] = {
    'functionality.allow_sorry': (None, True,
        _("'Admit current sub-goal!' is available with the Proof methods "
          "button")),
    'functionality.automatic_intro_of_exists': (None, True,
        _("When an existence property appears in the context, "
          "the ∃ button is operated automatically")),
    'functionality.target_selected_by_default': (None, True,
        _("Buttons act on the target if no context object is selected")),
    'functionality.allow_implicit_use_of_definitions': (None, True,
        _("e.g. the ∀ button applies on properties like 'A⊂B', which is a "
          "universal property by implicitly applying the definition of "
          "inclusion")),
    'functionality.auto_solve_inequalities_in_bounded_quantification':
        (None, False, _("e.g. when applying '∀ε>0, P(ε)' to some ε, "
                        "the computer tries to prove ε>0")),
    'functionality.drag_and_drop_in_context': (None, True,
        _("Objects and properties of the context may be dragged and dropped "
          "on each other, e.g. drag and drop 'x∈A' on 'A⊂B' to get 'x∈B'")),
    'functionality.drag_context_to_statements': (None, True,
        _("Properties of the context may be dragged and dropped on "
          "statements, typically a definition, e.g. drag and drop 'A⊂B' on "
          "the definition of inclusion")),
    'functionality.drag_statements_to_context': (None, True,
        _("Statements may be dragged and dropped in the context properties "
          "area, where they become a context property that may be applied "
          "with more precision")),
    'functionality.ask_to_prove_premises_of_implications': (None, False,
        _("When an implication 'P ⇒ Q' appears in the context, the computer "
          "asks user if she wants to prove P as a sub-goal")),
    'functionality.automatic_intro_of_variables_and_hypotheses': (None, True,
        _("The ∀ and ⇒ buttons are operated automatically when the "
          "target is a universal property or an implication")),
}

PRE_DEFINED['Functionalities'] = {
    'selected_level': 'functionality.default_functionality_level',
    'Beginner': {'functionality.allow_proof_by_sorry': True,
                 'functionality.automatic_intro_of_exists': True,
                 'functionality.target_selected_by_default': False,
                 'functionality.allow_implicit_use_of_definitions': False,
                 'functionality.auto_solve_inequalities_in_bounded_quantification': False,
                 'functionality.drag_and_drop_in_context': False,
                 'functionality.drag_context_to_statements': False,
                 'functionality.drag_statements_to_context': False,
                 'functionality.ask_to_prove_premises_of_implications': True,
                 'functionality.automatic_intro_of_variables_and_hypotheses': False
                 },
    'Intermediate': {'functionality.allow_proof_by_sorry': True,
                     'functionality.automatic_intro_of_exists': True,
                     'functionality.target_selected_by_default': True,
                     'functionality.allow_implicit_use_of_definitions': True,
                     'functionality.auto_solve_inequalities_in_bounded_quantification': True,
                     'functionality.drag_and_drop_in_context': False,
                     'functionality.drag_context_to_statements': False,
                     'functionality.drag_statements_to_context': False,
                     'functionality.ask_to_prove_premises_of_implications': True,
                     'functionality.automatic_intro_of_variables_and_hypotheses': False
                     },
    'Advanced': {'functionality.allow_proof_by_sorry': True,
                 'functionality.automatic_intro_of_exists': True,
                 'functionality.target_selected_by_default': True,
                 'functionality.allow_implicit_use_of_definitions': True,
                 'functionality.auto_solve_inequalities_in_bounded_quantification': True,
                 'functionality.drag_and_drop_in_context': True,
                 'functionality.drag_context_to_statements': True,
                 'functionality.drag_statements_to_context': True,
                 'functionality.ask_to_prove_premises_of_implications': True,
                 'functionality.automatic_intro_of_variables_and_hypotheses': False
                 },
    'Expert':   {'functionality.allow_proof_by_sorry': True,
                 'functionality.automatic_intro_of_exists': True,
                 'functionality.target_selected_by_default': True,
                 'functionality.allow_implicit_use_of_definitions': True,
                 'functionality.auto_solve_inequalities_in_bounded_quantification': True,
                 'functionality.drag_and_drop_in_context': True,
                 'functionality.drag_context_to_statements': True,
                 'functionality.drag_statements_to_context': True,
                 'functionality.ask_to_prove_premises_of_implications': False,
                 'functionality.automatic_intro_of_variables_and_hypotheses': True
                 }
}

CONFIGS["Language"] = {"i18n.select_language": (["en", "fr_FR"], True, "")}

CONFIGS["Advanced"] = {
    'others.course_directory': ('dir', True, ""),
    'others.Lean_request_method': (['automatic', 'normal',
                                    'from_previous_proof_state'], True, ''),
    'logs.save_journal': (None, True, ""),  # checked, untested
    'logs.display_level': (['debug', 'info', 'warning'], True, ""),
    # 'functionality.save_solved_exercises_for_autotest': (None, True, ""),
    'functionality.save_history_of_solved_exercises': (None, False, "")}

SETTINGS_AFFECTING_UI = ["display.target_display_on_top",
                         # Fonts
                         "display.target_font_size",
                         "display.main_font_size",
                         "display.statements_font_size",
                         "display.tooltips_font_size",
                         'display.math_font_file',
                         'display.proof_tree_font_size',
                         # DnD
                         'functionality.drag_statements_to_context',
                         'functionality.drag_and_drop_in_context',
                         'functionality.drag_context_to_statements',
                         "logic.use_color_for_variables",
                         "logic.use_color_for_dummy_variables",
                         # Action buttons
                         "symbols_AND_OR_NOT_IMPLIES_IFF_FORALL_EXISTS_EQUAL_MAP",
                         'display.use_symbols_for_logic_button',
                         'display.font_size_for_symbol_buttons',
                         'functionality.allow_implicit_use_of_definitions',
                         # FIXME: this is handled by resetting a whole new ecw
                         #  cf ecw.apply_new_settings()
                         # 'logic.use_color_for_applied_properties',
                         # 'functionality.allow_proof_by_sorry',
                         "i18n.select_language",
                         "logic.use_bounded_quantification_notation",
                         "logic.button_use_or_prove_mode"
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
        self.set_math_fonts_list()
        # self.setModal(True)
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
        self.ok_btn.setDefault(True)
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

    @staticmethod
    def set_math_fonts_list():
        syst = "System fonts" + " (" + deaduction_fonts.system_fonts_name + ")"
        fonts_name = [syst] + deaduction_fonts.math_fonts_file_names
        CONFIGS["Display"]["display.math_font_file"] = (fonts_name, True)

    def clicked(self, btn):
        """
        Called when a button is clicked, e.g. the "Apply" button.
        """
        if btn == self.apply_btn:
            if not self.check_settings():
                return
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
            # import deaduction.pylib.math_display.display_data
            # reload(deaduction.pylib.math_display.display_data)
            MathDisplay.update_dict()

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
                real_setting = cvars.get(setting, False)
                if real_setting != window.initial_settings[setting]:
                    new_modified_settings[setting] = \
                        window.initial_settings[setting]
                    # if modified setting has been applied, it will have to
                    # be modified back
            window.modified_settings = new_modified_settings
        # Restore initial settings
        self.apply()  # Apply backwards

        self.reject()

    def accept(self):
        """
        Called when usr clicks the "OK" button.
        """
        if not self.check_settings():
            return

        self.apply()
        if self.save_btn.isChecked():
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

    def check_settings(self) -> bool:
        """
        Check that the modified settings meet some requirements.
        This method should be called before accepting changes.
        """

        info = ""
        for window_ in self.__windows:
            info += window_.check_settings()

        if info:
            title = _("Wrong settings!")
            dialog = QMessageBox()
            dialog.setText(title)
            dialog.setInformativeText(info)
            dialog.setIcon(QMessageBox.Warning)
            dialog.exec()
            self.set_all_values()
            return False

        return True

    def set_all_values(self):
        """
        Set values in all widgets for display.
        """
        for window_ in self.__windows:
            window_.set_values()


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
        self.widgets = dict()  # keys = settings, value = QWidget
        self.settings = CONFIGS.get(name)
        self.predefined_settings_dict = PRE_DEFINED.get(name, {})

        self.layout = QFormLayout()
        if self.predefined_settings_dict:
            self.main_layout = QVBoxLayout()
            self.create_level_widgets()
            self.create_widgets()
            self.main_layout.addLayout(self.layout)
            self.setLayout(self.main_layout)
        else:
            self.create_widgets()
            self.setLayout(self.layout)

    @property
    def selected_level(self):
        """
        Return the predefined level if any, e.g.'beginner'.
        """
        level_key = self.predefined_settings_dict.get('selected_level', False)
        if level_key:
            return cvars.get(level_key, "Free settings")
        else:
            return "Free settings"

    def set_selected_level(self, level):
        level_key = self.predefined_settings_dict.get('selected_level')
        if level_key:
            cvars.set(level_key, level)

    def create_level_widgets(self):
        """
        Create radio buttons to select a set of predefined values corresponding
        to some level, e.g. 'beginner'.
        The selected level is in cvars(key) where
            key = self.predefined_settings_dict['selected_level']
        """
        if not self.predefined_settings_dict:
            return

        pre_defined_lyt = QHBoxLayout()

        # Pre-defined level widgets
        for setting in self.predefined_settings_dict:
            if setting != 'selected_level':
                widget = QRadioButton(_(setting))
                widget.level = setting
                pre_defined_lyt.addWidget(widget)
                if setting == self.selected_level:
                    widget.toggle()
                widget.toggled.connect(self.pre_defined_changed)

        # Free settings widget
        free_settings_widget = QRadioButton(_("Free settings"))
        free_settings_widget.level = "Free settings"
        free_settings_widget.toggled.connect(self.pre_defined_changed)
        pre_defined_lyt.addWidget(free_settings_widget)
        if self.selected_level == "Free settings":
            # Toggle Free settings
            free_settings_widget.toggle()

        self.main_layout.addLayout(pre_defined_lyt)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        self.main_layout.addWidget(separator)

    def create_widgets(self):

        for setting, info in self.settings.items():
            if len(info) == 2:
                (setting_list, enabled) = info
                tooltip = ''
            elif len(info) == 3:
                (setting_list, enabled, tooltip) = info
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
                widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            # ───────── Case of choice into a list: combo box ─────────
            elif setting_list:
                widget = QComboBox()
                widget.setting = setting
                if setting_list and setting_list != 'dir':
                    pretty_setting_list = [_(PRETTY_NAMES[setting])
                                           if setting in PRETTY_NAMES
                                           else setting
                                           for setting in setting_list]
                    widget.setting_list = setting_list
                    widget.addItems(pretty_setting_list)
                    if setting_initial_value and setting_initial_value in \
                            setting_list:
                        initial_index = setting_list.index(
                            setting_initial_value)
                        widget.setCurrentIndex(initial_index)
                widget.currentIndexChanged.connect(self.combo_box_changed)
                widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                # widget.has_been_initialised = False

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
            if widget:
                widget.setEnabled(enabled)
                title_wdg = QLabel(title)
                if tooltip:
                    widget.setToolTip(tooltip)
                    title_wdg.setToolTip(tooltip)
                self.layout.addRow(title_wdg, widget)
                self.widgets[setting] = widget

        # Set initial values
        self.set_values()

    def set_value(self, setting, setting_list, setting_value,
                  predefined=False):
        """
        Set value corresponding to setting.
        """
        widget = self.widgets[setting]
        widget.setEnabled(True)

        # ───────── Case of choice into a list: combo box ─────────
        if setting_list and setting_list != 'dir':
            if setting_value and setting_value in setting_list:
                index = setting_list.index(setting_value)
            else:
                index = 0
            widget.setCurrentIndex(index)

        # ───────── Case of bool: check box ─────────
        elif isinstance(setting_value, bool):
            if setting_value is not None:
                widget.setChecked(setting_value)

        # ───────── Case of str: QLineEdit ─────────
        elif isinstance(setting_value, str):
            if setting_value:
                initial_string = setting_value
                widget.setText(initial_string)

        if predefined:
            widget.setEnabled(False)

    def set_values(self):
        """
        Set widgets' values for display according to modified_settings
        (or to initial_settings for unmodified settings)
        (or to predefined_settings if pertinent).
        """
        level = self.selected_level
        # Values are pre_defined?
        predefined = ({} if level == "Free settings"
                      else self.predefined_settings_dict[level])

        for setting, info in self.settings.items():
            if len(info) == 2:
                (setting_list, enabled) = info
            else:
                (setting_list, enabled, tooltip) = info
            if setting in predefined:
                setting_value = predefined[setting]
            elif setting in self.modified_settings:
                setting_value = self.modified_settings[setting]
            else:
                setting_value = cvars.get(setting, default_value="none")

            if setting_value == "none":
                setting_value = None  # Avoid KeyError

            self.initial_settings[setting] = setting_value

            # The following is useful in case predefined setting is !=
            #  from cvars value.
            if setting_value != cvars.get(setting, default_value="none"):
                self.modified_settings[setting] = setting_value

            self.set_value(setting, setting_list, setting_value,
                           predefined=bool(predefined))
            # widget = self.widgets[setting]
            # if predefined:
            #     widget.freeze()
            #
            # if setting_value == "none":
            #     setting_value = None  # Avoid KeyError
            # self.initial_settings[setting] = setting_value
            #
            # # ───────── Case of choice into a list: combo box ─────────
            # if setting_list and setting_list != 'dir':
            #     if setting_value and setting_value in setting_list:
            #         index = setting_list.index(setting_value)
            #     else:
            #         index = 0
            #     widget.setCurrentIndex(index)
            #
            # # ───────── Case of bool: check box ─────────
            # elif isinstance(setting_value, bool):
            #     if setting_value:
            #         widget.setChecked(setting_value)
            #
            # # ───────── Case of str: QLineEdit ─────────
            # elif isinstance(setting_value, str):
            #     if setting_value:
            #         initial_string = setting_value
            #         widget.setText(initial_string)

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

    @Slot()
    def pre_defined_changed(self):
        """
        Called when usr change the predefined-settings radio button.
        """
        level_widget = self.sender()
        if not level_widget.isChecked():
            return

        self.set_selected_level(level_widget.level)
        if self.selected_level == "Free settings":
            # Unfreeze all, and that's all:
            for setting, toto in self.settings.items():
                if setting in self.widgets:
                    self.widgets[setting].setEnabled(True)
            return

        predefined_dict = self.predefined_settings_dict[self.selected_level]

        for setting, (setting_list, enabled, t) in self.settings.items():
            if setting in predefined_dict:
                setting_value = predefined_dict[setting]
                self.set_value(setting, setting_list, setting_value,
                               predefined=(predefined_dict is not None))

                # This is automatically done by slots:
                # if setting_value != self.initial_settings[setting]:
                #     self.modified_settings[setting] = setting_value

    def check_settings(self) -> str:
        """
        Check that the modified settings meet some requirements.
        This method should be called before accepting changes.
        """

        info = ""
        to_be_canceled: [str] = []
        # System fonts for maths
        if 'display.math_font_file' in self.modified_settings:
            index = self.modified_settings['display.math_font_file']

        # Dubious characters
        if 'display.dubious_characters' in self.modified_settings:
            default: str = self.initial_settings['display.dubious_characters']
            new = self.modified_settings['display.dubious_characters']
            nb = default.count(',')
            if nb != new.count(','):
                info = _("Missing characters: Enter exactly {} strings "
                         "separated by commas").format(nb)
                to_be_canceled.append('display.dubious_characters')
                widget = self.widgets['display.dubious_characters']
                widget.setText(default)
        # Cancel settings:
        for item in to_be_canceled:
            self.modified_settings[item] = self.initial_settings[item]
            # TODO: change value in widget!

        return info


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
