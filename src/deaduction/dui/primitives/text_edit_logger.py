"""
######################################################
# text_edit_logger.py : Provide TextEditLogger class #
######################################################

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

from PySide2.QtGui     import QFontDatabase
from PySide2.QtWidgets import QTextEdit

class TextEditLogger(QTextEdit, logging.Handler):
    """
    This class was made to display log entries from a logging module
    logger in a QTextEdit widget. Mind the double inheritance : it
    allows this class being treated directly as a QWidget while being
    directly the logger handler. Note also that no Logger object is
    declared here (as all things should be, see logging module doc. ¶
    Logger Objects): the logging cofigured somewhere else in the program
    (presumably with logging.configure()) is detected here and it is the
    one whose log entries are printed here. Inspired from
    https://stackoverflow.com/questions/28655198/
    best-way-to-display-logs-in-pyqt.

    To be instanciated, this class only needs format to display log
    entries, see self.__init__ docstring.

    This class is used when dependencies are missing at the start of
    dEAduction and the need to be installed. If the user chooses to
    install missing dependencies, an instance of this class is showed
    (in another widget TODO: which?) to display downloads logger.
    """

    def __init__(self):
        """
        Init self with a log entry format (log_format). specifying which
        info to display and in what way, for example: '%(asctime)s -
        %(levelname)s - %(message)s'.

        :param log_format: Log entries format.
        """
        QTextEdit.__init__(self)

        # QTextEdit
        self.setReadOnly(True)
        self.setMinimumHeight(400)
        self.setMinimumWidth(600)
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.setFont(font)

class TextEditLoggerHandler(logging.Handler):
    def __init__(self, log_obj: TextEditLogger, log_format: str):
        logging.Handler.__init__(self)

        self.log_obj = log_obj

        self.setFormatter(logging.Formatter(log_format))
        self.createLock()

    def emit(self, record):
        """
        This overloads logging.Handler.emit, necessary. From the
        documentation: 'Do whatever it takes to actually log the
        specified logging record. This version is intended to be
        implemented by subclasses and so raises a NotImplementedError.'.
        """

        self.acquire()
        log_message = self.format(record)
        self.log_obj.append(log_message)
        self.release()
