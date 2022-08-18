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

from PySide2.QtWidgets import QDialog, QRadioButton, QVBoxLayout, QHBoxLayout,\
    QTextEdit, QLabel, QDialogButtonBox, QWidget

from PySide2.QtCore import Qt, Slot, QSettings

from typing import Optional

from deaduction.dui.primitives import DeaductionFonts

from deaduction.pylib.mathobj import ContextMathObject

global _


class HelpWindow(QWidget):
    """
    A class for a window displaying a help msg, with maybe a small set of
    possible user actions.
    """

    def __init__(self, math_object: Optional[ContextMathObject] = None,
                 target=False):
        super().__init__()

        self.setWindowTitle(_("Help"))
        self.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.main_txt, self.detailed_txt, self.hint = None, None, None
        self.target = target

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

        if math_object:
            self.set_math_object(math_object, target=target)

    def set_geometry(self, geometry):
        settings = QSettings("deaduction")
        if settings.value("help/geometry"):
            self.restoreGeometry(settings.value("help/geometry"))
        elif geometry:
            self.setGeometry(geometry)

    def closeEvent(self, event):
        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("help/geometry", self.saveGeometry())
        event.accept()
        self.hide()

    def set_text(self):
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
        self.set_text()

    def set_math_object(self, math_object: ContextMathObject, target=False):

        msgs = (math_object.help_target_msg() if target else
                math_object.help_context_msg())

        self.math_label.setText(math_object.math_type_to_display())
        self.set_msgs(msgs)

    @Slot()
    def toggle_hint(self):
        self.hint_btn.setChecked(True)
        self.set_text()

    @Slot()
    def toggle_description(self):
        self.description_btn.setChecked(True)
        self.set_text()
