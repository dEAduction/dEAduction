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
# from PySide2.QtGui import     ( QColor, QBrush, QKeySequence )
from PySide2.QtGui import       QTextCursor
from PySide2.QtWidgets import ( QComboBox,
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
    stop_exercise = Signal()

    def __init__(self):
        super().__init__()
        settings = QSettings("deaduction")
        if settings.value("test_window/geometry"):
            self.restoreGeometry(settings.value("test_window/geometry"))

        self.setWindowTitle(_("Test console"))

        # Console

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setLineWrapMode(QTextEdit.NoWrap)

        # Buttons
        self.suspend_btn = QCheckBox('Suspend')
        self.mode_btn = QComboBox()
        self.mode_btn.addItems(['Step by step',
                                'Exercise by exercise',
                                'Uninterrupted'])
        self.next_step_button = QPushButton(_("Next step"))
        self.stop_exercise_btn = QPushButton("Stop this test")
        self.scroll_to_end_btn = QCheckBox(_("Scroll to end"))

        # Btns signals
        self.suspend_btn.stateChanged.connect(self.change_suspension)
        self.mode_btn.currentIndexChanged.connect(self.change_mode)
        self.next_step_button.clicked.connect(self.process_next_step)
        self.stop_exercise_btn.clicked.connect(self.stop_exercise)

        # Btns layout
        btn_status_layout = QVBoxLayout()
        btn_status_layout.addWidget(self.scroll_to_end_btn)
        btn_status_layout.addWidget(self.suspend_btn)
        btn_status_layout.addWidget(self.mode_btn)

        btn_process_layout = QVBoxLayout()
        btn_process_layout.addWidget(self.stop_exercise_btn)
        btn_process_layout.addWidget(self.next_step_button)

        btn_layout = QHBoxLayout()
        btn_layout.addLayout(btn_status_layout)
        btn_layout.addStretch()
        btn_layout.addLayout(btn_process_layout)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.console)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        self.freeze()

    def closeEvent(self, event):
        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("test_window/geometry", self.saveGeometry())
        event.accept()
        self.hide()

    @property
    def step_by_step(self):
        return self.mode_btn.currentIndex() == 0
        # return self.step_by_step_btn.isChecked()

    @property
    def exercise_by_exercise(self):
        return self.mode_btn.currentIndex() == 1

    @property
    def uninterrupted(self):
        return self.mode_btn.currentIndex() == 2

    @property
    def is_suspended(self):
        return self.suspend_btn.isChecked()

    @property
    def txt(self):
        return self.console.toPlainText()

    @Slot()
    def change_suspension(self):
        if self.is_suspended:
            for btn in (self.next_step_button,
                        self.mode_btn):
                btn.setEnabled(False)
        else:
            for btn in (self.next_step_button,
                        self.mode_btn):
                btn.setEnabled(True)

    @Slot()
    def change_mode(self):
        if self.uninterrupted:
            self.mode_btn.setEnabled(True)
            self.next_step_button.setEnabled(False)
            self.process_next_step.emit()
        elif self.exercise_by_exercise:
            self.mode_btn.setEnabled(True)
            self.next_step_button.setEnabled(True)
            self.next_step_button.setDefault(True)
            self.process_next_step.emit()
        else:
            self.mode_btn.setEnabled(True)
            self.next_step_button.setEnabled(True)
            self.next_step_button.setDefault(True)

    def display(self, txt, color=None):
        txt += '<br>'
        if color:
            intro = f'<font color="{color}">'
            outro = '</font>'
            txt = intro + txt + outro
        # self.console.moveCursor(QTextCursor.End)
        # self.console.insertHtml(txt)
        self.console.append(txt)
        if self.scroll_to_end_btn.isChecked():
            self.console.ensureCursorVisible()

    def freeze(self):
        if self.step_by_step:
            self.setEnabled(False)
        else:
            # Step by step is off, user must be able to put it again
            self.next_step_button.setEnabled(False)

    def unfreeze(self):
        self.setEnabled(True)
        if self.step_by_step or self.exercise_by_exercise:
            self.next_step_button.setEnabled(True)
            self.next_step_button.setDefault(True)
        else:
            self.next_step_button.setEnabled(False)

