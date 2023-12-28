"""
#######################################
# lean_editor.py : provide LeanEditor #
#######################################

Author(s)      : - Kryzar <antoine@hugounet.com>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : - Kryzar <antoine@hugounet.com>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : July 2020

Copyright (c) 2020 the dEAduction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    d∃∀duction is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with d∃∀duction. If not, see <https://www.gnu.org/licenses/>.
"""


from PySide2.QtCore import (Qt, Signal, Slot, QTimer, QSettings)
from PySide2.QtWidgets import (QHBoxLayout, QPlainTextEdit, QPushButton,
                               QVBoxLayout, QSizePolicy, QWidget)

from deaduction.dui.primitives import DisclosureGroupBox

global _


class LeanEditor(QWidget):

    # TODO: use a mono font
    # TODO: add line numbers
    # TODO: add syntaxic coloration

    editor_send_lean = Signal()
    action = None  # To be set to the QAction of exercise_toolbar

    def __init__(self):
        super().__init__()
        self.setWindowTitle(_('Code sent to Lean') + " — d∃∀duction")
        self.editor = QPlainTextEdit()
        # self.editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.send_btn = QPushButton(_('Send to L∃∀N'))

        self.send_btn.clicked.connect(self.editor_send_lean)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.error_console = DisclosureGroupBox(title="Lean error messages",
                                                hidden=True)
        self.error_edit = QPlainTextEdit()

        error_lyt = QVBoxLayout()
        error_lyt.addWidget(self.error_edit)
        self.error_console.group_bx.setLayout(error_lyt)

        # Layouts
        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        main_layout.addWidget(self.editor)
        btn_layout.addStretch()
        btn_layout.addWidget(self.send_btn)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.error_console)
        self.setLayout(main_layout)

        self.error_console.title_widget.clicked.connect(self.on_hide_errors)
        # TODO: enable code sent?
        self.send_btn.setEnabled(False)
        self.set_geometry()

    def set_geometry(self, geometry=None):
        """
        Restore saved geometry if any, but adapt height to content.
        """
        settings = QSettings("deaduction")
        value = settings.value("lean_editor/geometry")
        if value:
            self.restoreGeometry(value)
        elif geometry:
            self.setGeometry(geometry)
        hidden = settings.value("lean_editor/errors_hidden")
        if not hidden:
            self.on_hide_errors()

    def closeEvent(self, event):
        # Save window geometry
        # if not self.error_console.hidden:
        #     self.on_hide_errors()
        settings = QSettings("deaduction")
        settings.setValue("lean_editor/geometry", self.saveGeometry())
        settings.setValue("lean_editor/errors_hidden",
                          self.error_console.hidden)
        self.action.setChecked(False)
        self.hide()
        event.accept()

    def fix_editor_size(self):
        self.editor.setFixedHeight(self.editor.height())
        self.editor.setFixedWidth(self.editor.width())
        QTimer.singleShot(0, self.resize_me)

    def resize_me(self):
        self.adjustSize()
        self.editor.setMaximumWidth(0)
        self.editor.setMaximumHeight(0)
        self.editor.setMaximumHeight(16777215)
        self.editor.setMaximumWidth(16777215)

    @Slot()
    def on_hide_errors(self):
        self.fix_editor_size()
        self.error_console.set_hidden()

    def code_get(self):
        return self.editor.toPlainText()

    @Slot(str)
    def code_set(self, code: str):
        """
        Set code and clear errors.
        """
        self.editor.setPlainText(code)
        self.error_edit.setPlainText("")

    @Slot()
    def toggle(self):
        self.setVisible(not self.isVisible())

    def set_error_msg(self, errors: []):
        text = '\n'.join([error.text for error in errors])
        self.error_edit.setPlainText(text)

