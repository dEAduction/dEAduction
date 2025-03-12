"""
#########################################################
# statusbar.py : provide DeaductionStatusbar #
#########################################################

Author(s)      : - Frederic Le Roux
Maintainers(s) : - Frederic Le Roux
Date           : February 2025

Copyright (c) 2025 the dEAduction team

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

from PySide2.QtCore import Slot, QTimer
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import (QStatusBar,
                               QPushButton,
                               QLabel)

import deaduction.pylib.utils.filesystem as fs
import deaduction.pylib.config.vars as cvars

global _


class DeaductionStatusBar(QStatusBar):
    """
    A pending msg can be displayed after a timeout.
    This is used to display msgs about the structure of the proof
    (e.g. "Proof of first implication").
    Pending msgs are stored in the LILO list self.pending_msgs.
    A pending msg may be cancelled: if a user action happens before timeout,
    the msg is replaced by "". Note that a new pending msgs may be added by
    the action, with a new timeout ; this is why the cancelled msgs is
    erased but a blank msg stays in the list.
    """

    pending_msg_time_interval = 5000

    def __init__(self, parent):
        super().__init__(parent)

        # Waiting timer
        self.waiting_timer = QTimer(self)

        # Pending msgs
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.show_pending_msgs)
        # self.pending_msgs = []
        self.proof_msg: callable = None  # This will be set from outside

        # Icon
        self.iconWidget = QLabel(self)
        icons_base_dir = cvars.get("icons.path")
        error_icon_path = fs.path_helper(icons_base_dir) / 'cancel.png'
        success_icon_path = fs.path_helper(icons_base_dir) / 'checked.png'
        self.error_pixmap = QPixmap(str(error_icon_path.resolve()))
        self.success_pixmap = QPixmap(str(success_icon_path.resolve()))
        self.iconWidget.setScaledContents(True)
        self.iconWidget.setMaximumSize(self.height(), self.height())

        # Message
        self.messageWidget = QLabel("", self)

        # Help button
        self.help_button = QPushButton(_("Help"))

        # Insert icon and message
        self.insertWidget(0, self.iconWidget)
        self.insertWidget(1, self.messageWidget)

        self.addWidget(self.help_button)
        self.help_button.hide()
        self.show_success_icon()  # Trick: the status bar adapts its height
        self.hide_icon()

    @property
    def txt(self):
        return self.messageWidget.text()

    @Slot()
    def add_point(self):
        """
        Add a point (.) at the end of the msg.
        """
        msg = self.messageWidget.text()
        self.messageWidget.setText(msg + '.')

    def display_thinking_bar(self):
        self.set_message(_("    Thinking"))
        self.messageWidget.setStyleSheet("font-style: italic")
        self.waiting_timer.start(1000)

    def display_initializing_bar(self):
        self.set_message(_("    Initializing"))
        self.messageWidget.setStyleSheet("font-style: italic")
        self.waiting_timer.start(500)

    def stop_thinking(self):
        self.waiting_timer.stop()
        self.messageWidget.setStyleSheet("font-style: normal")

    def show_pending_msgs(self):
        """
        This method is called by the timer, when there is a permanent
        msg (e.g. a new_goal msg) to display, which take the place of the tmp msg
         (e.g. the usual success/error msgs).
        """

        self.erase()
        proof_msg = self.proof_msg()
        if proof_msg:
            self.show_normal_msg(proof_msg)

    def show_error_icon(self):
        self.iconWidget.setPixmap(self.error_pixmap)
        self.iconWidget.show()

    def show_success_icon(self):
        self.iconWidget.setPixmap(self.success_pixmap)
        self.iconWidget.show()

    def show_error_msg(self, tmp_msg):
        self.show_error_icon()
        self.set_message(tmp_msg)

    def show_success_msg(self, tmp_msg):
        self.show_success_icon()
        self.set_message(tmp_msg)

    def hide_icon(self):
        self.iconWidget.hide()

    def set_message(self, msg: str):
        self.stop_thinking()
        self.messageWidget.setText(msg)
        return

    def erase(self):
        self.set_message("")
        self.hide_icon()

    @Slot()
    def show_normal_msg(self, msg):
        # log.debug("StatusBar: show " + msg)
        self.hide_icon()
        self.set_message(msg)

    def stop_timer(self):
        # print(f"Timer remaining {self.timer.remainingTime()}, stopped?")
        if self.timer.isActive():
            self.timer.stop()

    def show_tmp_msg(self, msg: str, duration=None):
        """
        Show msg and start the timer that will call show_pending_msgs().
        """
        if not duration:
            duration = self.pending_msg_time_interval
        self.timer.setInterval(duration)
        self.set_message(msg)
        self.timer.start()
        # self.timer.singleShot(duration, self.erase)
        # self.timer.singleShot(duration, self.show_pending_msgs)
