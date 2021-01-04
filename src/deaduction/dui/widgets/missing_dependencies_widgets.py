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

from typing    import Optional

from PySide2.QtCore    import ( Signal,
                                Slot )
from PySide2.QtWidgets import ( QDialog,
                                QLabel,
                                QMessageBox,
                                QPushButton,
                                QHBoxLayout,
                                QVBoxLayout )

from deaduction.dui.widgets       import TextEditLogger
from deaduction.pylib.config.i18n import _

# Tests only
import sys
from PySide2.QtWidgets import QApplication


class YesNoDialog(QMessageBox):
    # TODO: Docstring me

    def __init__(self):
        super().__init__()

        self.__yes = False
        self.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        self.button(QMessageBox.Yes).clicked.connect(self._set_yes_True)

    @Slot()
    def _set_yes_True(self):
        self.__yes = True

    @property
    def yes(self):
        return self.__yes

    @property
    def no(self):
        return not self.__yes


class WantToInstallMissingDependencies(YesNoDialog):
    # TODO: Docstring me

    def __init__(self, missing_dependencies: [str]):
        super().__init__()

        self.setText(_('Missing dependencies'))
        self.setInformativeText(_('Some dependencies are missing. Do you want'\
                                  ' to install them?'))
        self.setDetailedText('— ' + '\n— '.join(missing_dependencies))
        self.setIcon(QMessageBox.Warning)
        self.setDefaultButton(QMessageBox.Yes)


class ReallyWantToQuit(YesNoDialog):
    # TODO: Dosctring me

    def __init__(self, informative_text: str, detailed_text: Optional[str]=None):
        super().__init__()

        self.setModal(True)

        self.setText(_('Do you really want to quit?'))
        self.setInformativeText(informative_text)
        if detailed_text is not None:
            self.setDetailedText(detailed_text)
        self.setIcon(QMessageBox.Warning)
        self.setDefaultButton(QMessageBox.No)

        self.button(QMessageBox.Yes).clicked.connect(self._set_yes_True)


class InstallingMissingDependencies(QDialog):
    # TODO: Docstring me

    plz_start_deaduction = Signal()
    plz_quit             = Signal()

    def __init__(self, log_format: str):

        super().__init__()
        self.setModal(True)

        self.setWindowTitle(f"{_('Installing missing dependencies')}" \
                             " — d∃∀duction")

        self.__text_edit_logger = TextEditLogger(log_format)

        self.__confirm_quit = True

        # Buttons
        self.__quit_btn       = QPushButton(_('Quit'))
        self.__start_dead_btn = QPushButton(_('Start d∃∀duction'))
        self.__quit_btn.setAutoDefault(False)
        self.__start_dead_btn.setEnabled(False)
        self.__quit_btn.clicked.connect(self.__quit)
        self.__start_dead_btn.clicked.connect(self.plz_start_deaduction)

        # Layouts
        self.__main_layout = QVBoxLayout()
        btns_layout = QHBoxLayout()
        btns_layout.addStretch()
        btns_layout.addWidget(self.__quit_btn)
        btns_layout.addWidget(self.__start_dead_btn)
        self.__main_layout.addWidget(self.__text_edit_logger)
        self.__main_layout.addLayout(btns_layout)
        self.setLayout(self.__main_layout)

    @Slot()
    def installation_completed(self):

        self.__confirm_quit = False
        self.__text_edit_logger.setStyleSheet('background: SpringGreen;')

        self.__main_layout.insertWidget(1,
                QLabel(_('Missing dependencies installed.')))

        self.__start_dead_btn.setEnabled(True)
        self.__start_dead_btn.setDefault(True)

        self.__start_dead_btn.clicked.connect(self.plz_start_deaduction)

    @Slot()
    def __quit(self):

        if self.__confirm_quit:
            rwtq = ReallyWantToQuit(_('All downloaded data will be lost.'))
            rwtq.exec_()

            if rwtq.yes:
                self.plz_quit.emit()
        else:
            self.plz_quit.emit()


if __name__ == '__main__':
    app = QApplication()

    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    imd = InstallingMissingDependencies(log_format)
    imd.open()

    sys.exit(app.exec_())
