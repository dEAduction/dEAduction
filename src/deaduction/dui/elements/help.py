"""
########################
# help.py: Help window #
########################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 04 2022 (creation)
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

from PySide2.QtCore import Qt, Slot, QSettings

from PySide2.QtWidgets import QDialog, QRadioButton, QVBoxLayout, QHBoxLayout,\
    QTextEdit, QLabel, QDialogButtonBox, QWidget

from PySide2.QtGui import QIcon

from typing import Union, Optional

import deaduction.pylib.config.vars as cvars
from deaduction.dui.primitives import DeaductionFonts

from deaduction.pylib.mathobj import ContextMathObject
from deaduction.dui.elements import MathObjectWidgetItem

global _


class HelpWindow(QWidget):
    """
    A class for a window displaying a help msg, with maybe a small set of
    possible user actions.
    """

    action = None  # Set by exercise_main_window

    def __init__(self):
        super().__init__()

        self.setWindowTitle(_("Help"))
        # Window stay on top of parent:
        self.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.main_txt, self.detailed_txt, self.hint = None, None, None
        self.target = False
        self.math_wdg_item: Optional[MathObjectWidgetItem] = None
        self.math_object: Optional[ContextMathObject] = None

        # Display math_object
        self.math_label = QLabel()
        self.math_label.setTextFormat(Qt.RichText)

        # Display help msgs
        self.help_wdg = QTextEdit()
        self.help_wdg.setReadOnly(True)

        # Fonts
        fonts = DeaductionFonts(self)
        text_font = self.help_wdg.font()
        main_size = fonts.main_font_size
        text_font.setPointSize(main_size)
        self.help_wdg.setFont(text_font)

        target_size = fonts.target_font_size
        label_font = self.math_label.font()
        label_font.setPointSize(target_size)
        self.math_label.setFont(label_font)

        # Layout
        self.lyt = QVBoxLayout()
        self.lyt.addWidget(self.math_label)
        self.lyt.addWidget(self.help_wdg)
        self.lyt.setAlignment(self.math_label, Qt.AlignHCenter)

        # Buttons
        self.description_btn = QRadioButton(_("Description"))
        self.hint_btn = QRadioButton(_("Hint"))
        self.description_btn.clicked.connect(self.toggle_description)
        self.hint_btn.clicked.connect(self.toggle_hint)
        self.description_btn.setChecked(True)

        self.radio_btns = QVBoxLayout()
        self.radio_btns.addWidget(self.description_btn)
        self.radio_btns.addWidget(self.hint_btn)

        self.btns = QHBoxLayout()
        self.btns.addLayout(self.radio_btns)

        self.lyt.addLayout(self.btns)

        self.setLayout(self.lyt)
        self.empty_content()

        self.set_geometry()
        # if math_object:
        #     self.set_math_object(math_object, target=target)

    def set_geometry(self, geometry=None):
        settings = QSettings("deaduction")
        if settings.value("help/geometry"):
            # pass
            self.restoreGeometry(settings.value("help/geometry"))
        elif geometry:
            self.setGeometry(geometry)

    def closeEvent(self, event):
        # Save window geometry
        self.unset_item()
        settings = QSettings("deaduction")
        settings.setValue("help/geometry", self.saveGeometry())
        self.toggle(yes=False)
        # if self.action:
        #     self.action.setChecked(False)
        event.accept()

    @property
    def icon(self):
        if self.action:
            return self.action.icon()
        else:
            return None

    def empty_content(self):
        """
        Empty all content by displaying a general msg.
        """
        self.math_label.setText("<em>" + _("No object selected") + "</em>")
        self.math_label.setStyleSheet("")
        self.help_wdg.setHtml("<em>" + _("Double click on context or target "
                                         "to get some help.") + "</em>")

    def display_text(self):
        text = ""
        if self.description_btn.isChecked():
            if self.main_txt:
                text = self.main_txt + """

                                        """ + self.detailed_txt
            else:
                text = "<em> " + _("No help available.") + "</em>"

        elif self.hint_btn.isChecked():
            if self.hint:
                text = "<em> <b>" + _("Hint: ") + "</b>" + self.hint + "</em>"
            else:
                text = "<em> " + _("No hint available.") + "</em>"

        self.help_wdg.setHtml(text)

    def set_msgs(self, msgs: (str, str, str)):
        self.main_txt, self.detailed_txt, self.hint = msgs
        self.display_text()

    def display_math_object(self):
        if self.math_object.math_type.is_prop():  # target and context props
            math_text = self.math_object.math_type_to_display()
        else:  # context objects
            lean_name = self.math_object.to_display()
            math_expr = self.math_object.math_type_to_display()
            math_text = f'{lean_name} : {math_expr}'

        self.math_label.setText(math_text)
        color = cvars.get("display.color_for_highlight_in_proof_tree",
                          "yellow")
        self.math_label.setStyleSheet(f"background-color: {color};")

    def unset_item(self):
        if self.math_wdg_item:
            try:  # Maybe context has changed and object no longer exists
                self.math_wdg_item.highlight(yes=False)
                # self.math_wdg_item.select()
                # self.math_wdg_item.setIcon(QIcon())
            except RuntimeError:
                pass
            self.math_wdg_item = None
        self.math_object = None
        self.empty_content()

    def set_math_object(self,
                        item: Union[MathObjectWidgetItem, ContextMathObject],
                        target=False):
        """
        Display a help msg on a new ContextMathObject. Unselect previous item
        if any.
        """

        self.unset_item()
        if hasattr(item, 'select') and hasattr(item, 'highlight'):
            item.select(yes=False)
            item.highlight()
            # if self.icon:
            #     item.setIcon(self.icon)
            self.math_wdg_item = item
            self.math_object = item.math_object
        elif isinstance(item, ContextMathObject):
            self.math_object = item

        if self.math_object:
            msgs = (self.math_object.help_target_msg() if target else
                    self.math_object.help_context_msg())

            self.display_math_object()
            self.set_msgs(msgs)

    @Slot()
    def toggle(self, yes=None):
        """
        Toggle window, and unset item if hidden.
        """
        if yes is None:  # Change state to opposite
            yes = not self.isVisible()
        if yes:
            self.set_geometry()
            self.setVisible(True)
        else:
            self.unset_item()
            settings = QSettings("deaduction")
            settings.setValue("help/geometry", self.saveGeometry())
            self.setVisible(False)

        self.action.setChecked(self.isVisible())

    @Slot()
    def hide(self):
        self.toggle(yes=False)

    @Slot()
    def toggle_hint(self):
        self.hint_btn.setChecked(True)
        self.display_text()

    @Slot()
    def toggle_description(self):
        self.description_btn.setChecked(True)
        self.display_text()
