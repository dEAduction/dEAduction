"""
######################################################
# really_want_quit.py : provide ReallyWantQuit class #
######################################################

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
Date           : January 2021

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

from typing                       import Optional

from PySide2.QtWidgets            import QMessageBox

# from deaduction.pylib.config.i18n import _
from deaduction.dui.primitives    import YesNoDialog


class ReallyWantQuit(YesNoDialog):
    """
    A YesNoDialog (see YesNoDialog docstring to know how to use this
    class, I insist, do it) to ask if usr *really* wants to quit. This
    is a generall class that may be used anywhere in the program. It is
    initiated with an informative text and may also receive a
    detailed text. See an example in
    InstallingMissingDependencies.__quit for example.
    """

    def __init__(self, informative_text: str,
                 detailed_text: Optional[str] = None):
        """
        Init self (see self docstring).

        :param informative_text: Qt's informativeText, e.g. 'All data
                will be lost'.
        :param detailed_text: Qt's detailedText, e.g. a detailed list of
                stuff that usr does not necessarly need to know but may
                whant to know.
        """
        super().__init__()

        self.setText(_('Do you really want to quit?'))
        self.setInformativeText(informative_text)
        if detailed_text is not None:
            self.setDetailedText(detailed_text)
        self.setIcon(QMessageBox.Warning)
        self.setDefaultButton(QMessageBox.No)

        self.button(QMessageBox.Yes).clicked.connect(self._set_yes_True)
