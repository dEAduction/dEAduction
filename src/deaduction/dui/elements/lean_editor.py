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


from PySide2.QtCore import (    Qt,
                                Signal,
                                Slot)
from PySide2.QtWidgets import ( QHBoxLayout,
                                QPlainTextEdit,
                                QPushButton,
                                QVBoxLayout,
                                QWidget)


class LeanEditor(QWidget):

    # TODO: use a mono font
    # TODO: add line numbers
    # TODO: add syntaxic coloration

    editor_send_lean = Signal()

    def __init__(self):
        super().__init__()
        self.editor = QPlainTextEdit()
        self.send_btn = QPushButton(_('Send to L∃∀N'))

        self.send_btn.clicked.connect(self.editor_send_lean)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        # Layouts
        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        main_layout.addWidget(self.editor)
        btn_layout.addStretch()
        btn_layout.addWidget(self.send_btn)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        # TODO: enable code sent?
        self.send_btn.setEnabled(False)

    ###########
    # Methods #
    ###########

    def closeEvent(self, event):
        event.accept()
        self.hide()

    def code_get(self):
        return self.editor.toPlainText()

    #########
    # Slots #
    #########

    @Slot(str)
    def code_set(self, code: str):
        self.editor.setPlainText(code)
    
    @Slot()
    def toggle(self):
        self.setVisible(not self.isVisible())
