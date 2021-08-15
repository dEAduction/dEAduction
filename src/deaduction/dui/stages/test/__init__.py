"""
################
# __init__.py  #
################

Author(s)      : Frédéric Le Roux <frederic.le-roux@imj-prg.fr>

Maintainers(s) : Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
Date           : April 2021

Copyright (c) 2021 the dEAduction team

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

import sys
import logging
from typing import Union
from PySide2.QtCore import    ( Qt, Signal, Slot, QSettings )
from PySide2.QtGui import     ( QColor, QBrush, QKeySequence )
from PySide2.QtWidgets import (
                                QToolTip,
                                QApplication,
                                QWidget,
                                QTextEdit,
                                QPushButton,
                                QCheckBox,
                                QVBoxLayout,
                                QHBoxLayout)

global _

class QTestWindow(QWidget):
    """
    A widget for managing tests.
    """

    process_next_step = Signal()

    def __init__(self):
        super().__init__()
        settings = QSettings("deaduction")
        if settings.value("test_window/geometry"):
            self.restoreGeometry(settings.value("test_window/geometry"))


        # Console
        self.txt_for_console = ""
        self.test_msgs_console = QTextEdit()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.step_by_step_btn = QCheckBox(_("Step by step"))
        self.next_step_button = QPushButton("Next step")
        self.step_by_step_btn.clicked.connect(self.enable_next_button)
        self.next_step_button.clicked.connect(self.process_next_step)
        self.step_by_step_btn.setChecked()

        btn_layout.addWidget(self.step_by_step)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.test_msgs_console)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def closeEvent(self, event):
        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("test_window/geometry", self.saveGeometry())
        event.accept()
        self.hide()

    @property
    def step_by_step(self):
        return self.step_by_step_btn.isChecked()

    def enable_next_button(self):
        self.next_step_button.setEnabled(self.step_by_step_btn.isChecked())

    def display_in_console(self, txt):
        self.txt_for_console += '\n' + txt
        self.test_msgs_console.setText(self.txt_for_console)


