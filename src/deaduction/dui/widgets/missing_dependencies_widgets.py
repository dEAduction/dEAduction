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

from PySide2.QtWidgets import ( QMessageBox,
                                QPushButton,
                                QVBoxLayout,
                                QWidget )

from deaduction.dui.widgets       import TextEditLogger
from deaduction.pylib.config.i18n import _


class WannaInstallMissingDependencies(QMessageBox):
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
