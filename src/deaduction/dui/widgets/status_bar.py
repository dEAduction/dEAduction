"""
##############################################
# status_bar.py: Provide IconStatusBar class #
##############################################


Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 12 2020 (creation)
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
import logging
from pathlib import Path

from PySide2.QtGui import     ( QPixmap )
from PySide2.QtWidgets import ( QMainWindow,
                                QLabel,
                                QStatusBar,
                                QApplication)

import deaduction.pylib.config.vars      as cvars
import deaduction.pylib.utils.filesystem as fs

log = logging.getLogger(__name__)


# TODO: Put this in exercises widgets?
class IconStatusBar(QStatusBar):
    # TODO: Docstring me

    def __init__(self, parent):
        super().__init__(parent)

        # Icon
        self.iconWidget = QLabel(self)
        icons_base_dir = cvars.get("icons.path")
        error_icon_path = fs.path_helper(icons_base_dir) / 'error_devil2.png'
        self.error_pixmap = QPixmap(str(error_icon_path.resolve()))
        self.iconWidget.setScaledContents(True)
        self.iconWidget.setMaximumSize(self.height(), self.height())
        self.iconWidget.setPixmap(self.error_pixmap)

        # Message
        self.messageWidget = QLabel("", self)

        # Insert icon and message
        self.insertWidget(0,self.iconWidget)
        self.insertWidget(1, self.messageWidget)
        self.iconWidget.hide()

    def show_error_icon(self):
        self.iconWidget.show()

    def hide_icon(self):
        self.iconWidget.hide()

    def set_message(self, message: str):
        self.messageWidget.setText(message)

    def display_status_bar_message(self, event=None, instruction=None):
        """
        Display a message in the status bar.
        :param event:       tuple of strings, (nature, content, details)
        :param instruction: 'erase' or None
        """

        status_bar = self
        if instruction == 'erase':
            status_bar.set_message("")
            status_bar.hide_icon()
        elif event:
            nature, message, details = event
            if details:
                message += ": " + details
            if nature in ('error', 'lean_error'):
                status_bar.show_error_icon()
                status_bar.set_message(message)
            else:
                status_bar.hide_icon()


if __name__ == '__main__':

    class MyWindow(QMainWindow):

        def __init__(self):
            QMainWindow.__init__(self)
            self.setWindowTitle('Trial')
            self.resize(400, 300)
            self.status_bar = IconStatusBar(self)
            self.setStatusBar(self.status_bar)

    app = QApplication(sys.argv)

    myWindow = MyWindow()
    myWindow.show()
    myWindow.status_bar.display_status_bar_message(event=('error',
                                                          'Erreur',
                                                          'TOTO pas content'))
    # # myWindow.status_bar.display_status_bar_message(instruction='erase')
    # # myWindow.status_bar.show_error_icon()
    # # myWindow.status_bar.hide_icon()
    sys.exit(app.exec_())
