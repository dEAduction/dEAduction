"""
###############################################
# missing_dependencies_widgets.py : see below #
###############################################

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
Date           : December 2020

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
# TODO: Docstring me

from typing import Optional

from PySide2.QtCore    import ( Signal,
                                Slot )
from PySide2.QtWidgets import ( QDialog,
                                QMessageBox,
                                QPushButton,
                                QHBoxLayout,
                                QVBoxLayout )

from deaduction.dui.widgets       import TextEditLogger
from deaduction.pylib.config.i18n import _

# Tests only
import sys
from PySide2.QtWidgets import QApplication


class WantToInstallMissingDependencies(QMessageBox):
    # TODO: Docstring me

    def __init__(self, missing_dependencies: [str]):
        super().__init__()

        self.setText(_('Missing dependencies'))
        self.setInformativeText(_('Some dependencies are missing. Do you want'\
                                  ' to install them?'))
        self.setDetailedText('— ' + '\n— '.join(missing_dependencies))
        self.setIcon(QMessageBox.Warning)
        self.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        self.setDefaultButton(QMessageBox.Yes)


class ReallyWantToQuit(QMessageBox):
    # TODO: Dosctring me

    def __init__(self, informative_text: str, detailed_text: Optional[str]=None):
        super().__init__()

        self.setModal(True)
        self.__yes = False

        self.setText(_('Do you really want to quit?'))
        self.setInformativeText(informative_text)
        if detailed_text is not None:
            self.setDetailedText(detailed_text)
        self.setIcon(QMessageBox.Warning)
        self.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        self.setDefaultButton(QMessageBox.No)

        self.button(QMessageBox.Yes).clicked.connect(self.__set_yes_True)

    @Slot()
    def __set_yes_True(self):
        self.__yes = True

    @property
    def yes(self):
        return self.__yes


class InstallingMissingDependencies(QDialog):
    # TODO: Docstring me

    usr_wants_start_deaduction = Signal()

    def __init__(self, log_format: str):

        super().__init__()

        self.setModal(True)
        self.setWindowTitle(f"{_('Installing dependencies')} — d∃∀duction")

        text_edit_logger = TextEditLogger(log_format)

        self.__quit_btn = QPushButton(_('Quit'))
        self.__start_dead_btn = QPushButton(_('Start d∃∀duction'))
        self.__quit_btn.setAutoDefault(False)
        self.__start_dead_btn.setEnabled(False)

        self.__start_dead_btn.clicked.connect(self.usr_wants_start_deaduction)
        self.__quit_btn.clicked.connect(self.__quit_btn_clicked)

        main_layout = QVBoxLayout()
        btns_layout = QHBoxLayout()
        btns_layout.addStretch()
        btns_layout.addWidget(self.__quit_btn)
        btns_layout.addWidget(self.__start_dead_btn)
        main_layout.addWidget(text_edit_logger)
        main_layout.addLayout(btns_layout)
        self.setLayout(main_layout)

    def enable_startdeaduction_btn(self):
        self.__start_dead_btn.setEnabled(True)
        self.__start_dead_btn.setDefault(True)

    @Slot()
    def __quit_btn_clicked(self):
        rwtq = ReallyWantToQuit('')
        rwtq.exec_()

        if rwtq.yes:
            # Do something
            pass

if __name__ == '__main__':
    app = QApplication()

    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    imd = InstallingMissingDependencies(log_format)
    imd.open()

    sys.exit(app.exec_())
