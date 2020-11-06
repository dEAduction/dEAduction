"""
##################
# __init__.py :  #
##################

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

from gettext import             gettext as  _
import                          logging
import                          pickle
from pathlib import             Path
import sys
from PySide2.QtWidgets import ( QApplication,
                                QFileDialog,
                                QInputDialog)

import deaduction.pylib.logger as               logger
from deaduction.pylib.coursedata.course import Exercise
from deaduction.dui.widgets import LauncherMainWindow

log = logging.getLogger(__name__)


def select_exercise() -> Exercise:

    launcher_main_window = LauncherMainWindow()
    exercise = None

    launcher_main_window.show()

    # TODO: Process when clicking on 'Quit' button
    while not exercise:
        exercise = launcher_main_window.selected_exercise()

    launcher_main_window.close()

    return exercise
