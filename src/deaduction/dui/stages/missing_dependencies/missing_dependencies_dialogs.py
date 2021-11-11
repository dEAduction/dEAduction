"""
###############################################
# missing_dependencies_dialogs.py : see below #
###############################################

    Provide dialogs that ask usr if they want to install missing
    dependencies. At its start, dEAduction checks if some of its
    dependencies are missing. If it's the case, usr is asked whether
    they want to install them or not. The dialogs used for this are
    written in this module. Provided classes:
        - InstallingMissingDependencies,
        - WantInstallMissingDependencies.

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

import logging
from   logging.handlers import (QueueHandler,
                                QueueListener)

from queue import Queue
from typing    import Optional

from PySide2.QtCore    import ( Signal,
                                Slot )
from PySide2.QtWidgets import ( QDialog,
                                QLabel,
                                QMessageBox,
                                QPushButton,
                                QHBoxLayout,
                                QVBoxLayout )

from deaduction.dui.primitives    import ( TextEditLogger,
                                           TextEditLoggerHandler,
                                           YesNoDialog )
# from deaduction.pylib.config.i18n import _

from deaduction.dui.stages.quit_deaduction import ( ReallyWantQuit )

# Tests only
import sys
from PySide2.QtWidgets import QApplication


class WantInstallMissingDependencies(YesNoDialog):
    """
    A YesNoDialog (see YesNoDialog docstring to know how to use this
    class) to ask if usr wants to install missing dependencies.
    dEaduction checks for missing dependencies at each start and this is
    when this dialod may be shown.
    """

    def __init__(self, missing_dependencies: [str]):
        """
        Init self with the list of missing dependencies (to be
        displayed).

        :param missing_dependencies: List of missing dependencies to be
                                     displayed.
        """
        # @Florian: If you want I can do some more formatting for the
        # list of dependencied

        super().__init__()

        self.setText(_('Missing dependencies'))
        self.setInformativeText(_('Some dependencies are missing. Do you want'\
                                  ' to install them?'))
        self.setDetailedText('— ' + '\n— '.join(missing_dependencies))
        self.setIcon(QMessageBox.Warning)
        self.setDefaultButton(QMessageBox.Yes)


class InstallingMissingDependencies(QDialog):
    """
    At start, dEaduction checks if some dependencies are missing. If
    some indeed are, usr is asked is they want to install them
    (WantInstallMissingDependencies). If they do, download begins and this
    dialog is shown showing a logger of the installation.

    When the download is completed, the 'Start dEAduction' button is
    activated (method installation_completed) and usr may click on it.
    If they do, the signal plz_start_deaduction is emitted. Furthermore,
    the usr may want to quit (by clicking the 'Quit' button). If they do
    so during the installation, they are asked for confirmation (see
    __quit method) and if they confirm, the signal plz_quit is emitted.

    The logger is displayed with the class TextEditLogger.
    """

    plz_start_deaduction = Signal()
    plz_quit             = Signal()

    def __init__(self, log_format: str = '%(asctime)s - %(levelname)s - %(message)s'):
        """
        Init self with a logger formater (so specify the layout of the
        log entries, see logging module documentation), e.g.
        '%(asctime)s - %(levelname)s - %(message)s'.

        :param log_format: Logger formatter for the log entries.
        """

        super().__init__()
        self.setModal(True)

        self.setWindowTitle(f"{_('Installing missing dependencies')}" \
                             " — d∃∀duction")
        self.__text_edit_logger = TextEditLogger()
        self.__confirm_quit     = True

        # Buttons
        self.__quit_btn       = QPushButton(_('Quit'))
        self.__start_dead_btn = QPushButton(_('Start d∃∀duction'))
        self.__quit_btn.setAutoDefault(False)
        self.__start_dead_btn.setEnabled(False)
        self.__quit_btn.clicked.connect(self.__quit)
        self.__start_dead_btn.clicked.connect(self.plz_start_deaduction)

        # Layouts
        self.__main_layout = QVBoxLayout()
        btns_layout        = QHBoxLayout()
        btns_layout.addStretch()
        btns_layout.addWidget(self.__quit_btn)
        btns_layout.addWidget(self.__start_dead_btn)
        self.__main_layout.addWidget(self.__text_edit_logger)
        self.__main_layout.addLayout(btns_layout)
        self.setLayout(self.__main_layout)

        # Logging facilities, avoid some segfault and thread-related nastyness
        self.__text_edit_logger_handler = TextEditLoggerHandler(self.__text_edit_logger, log_format)
        self.__log_queue     = Queue(-1)
        self.__queue_handler = QueueHandler(self.__log_queue)
        self.__queue_listener= QueueListener(self.__log_queue, self.__text_edit_logger_handler)

    def log_attach(self, log_obj: logging.Logger):
        log_obj.addHandler(self.__queue_handler)

    def log_dettach(self, log_obj: logging.Logger):
        log_obj.removeHandler(self.__queue_handler)

    def log_start(self):
        self.__queue_listener.start()

    def log_stop(self):
        self.__queue_listener.stop()

    @Slot()
    def installation_completed(self):
        """
        This function is to be called when dependencies are all
        downloaded and the installation is completed:
        - it indicates all went good;
        - it allows usr to click on the 'Start dEAduction button';
        - it sets self.__confirm_quit to False, which implies that if
          usr wants to quit instead of starting dEAduction, confirmation
          will *not* be asked.

        It is recommanded (to comply with Qt's style) to connect this
        method to a slot and not call it directly.
        """

        self.__confirm_quit = False
        self.__text_edit_logger.setStyleSheet('background: SpringGreen;')
        self.__main_layout.insertWidget(1,
                QLabel(_('Missing dependencies installed.')))
        self.__start_dead_btn.setEnabled(True)
        self.__start_dead_btn.setDefault(True)
        self.__start_dead_btn.clicked.connect(self.plz_start_deaduction)

    @Slot()
    def __quit(self):
        """
        This slot is called when usr clicks on the 'Quit' button. If
        downloads and installation are not completed, confirmation is
        asked by executing ReallyWantQuit dialog. In the end, if usr
        really wants to quit, the signal plz_quit is emitted (here is
        not the place to quit).
        """

        if self.__confirm_quit:
            rwtq = ReallyWantQuit(_('All downloaded data will be lost.'))
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
