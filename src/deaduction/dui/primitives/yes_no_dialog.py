"""
################################################
# yes_no_dialog.py : Provide YesNoDialog class #
################################################

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

from PySide2.QtCore    import Slot, Qt, QTimer
from PySide2.QtWidgets import QMessageBox, QCheckBox, QDialogButtonBox

import deaduction.pylib.config.vars as cvars

global _


class YesNoDialog(QMessageBox):
    """
    This class is a modal QMessageBox with two buttons: Yes and No. Usr
    will be asked to make a choice (e.g. 'Do you want to install missing
    dependencies ?'). Is usr clicks on the Yes (resp. No) button, the
    dialog is closed and the property yes is set to True (resp. False).
    This property is initialized to False and is only change if usr
    clicks on the Yes button.

    This dialog is to be used with the exec_ method this way:
    >>> ynd = YesNoDialog()
    >>> ynd.setText('Voulez-vous coucher avec moi ce soir ?')
    >>> ynd.exec_()
    >>> if ynd.yes:
    >>>     self.buy_condoms()

    The same code with the open method instead of exec_ will NOT work
    because open returns immediatly and the property yes will be False
    even if usr clicked on the Yes button. To set up texts (e.g.
    detailedText) it is recommanded to inherit this class and set valued
    in __init__. See for example the class ReallyWantQuit.

    :property yes: Return self.__yes.
    :property no: Return not self.__yes.
    """

    def __init__(self):
        """
        Init self (see self docstring).
        """

        super().__init__()
        # (Bad) default title
        self.setWindowTitle(_("Yes or no? — d∃∀duction"))
        self.setModal(True)

        self.__yes = False
        # self.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        self.addButton(QMessageBox.No)
        self.addButton(QMessageBox.Yes)
        self.button(QMessageBox.Yes).clicked.connect(self._set_yes_True)
        # self.setButtonText(QMessageBox.Yes, _("Yes"))
        # self.setButtonText(QMessageBox.No, _("No"))

    @Slot()
    def _set_yes_True(self):
        """
        Set self.__yes to True. This slot is called when the Yes button
        is clicked on by usr.
        """

        self.__yes = True

    @property
    def yes(self):
        """
        Return self.__yes.
        """

        return self.__yes

    @property
    def no(self):
        """
        Return not self.__yes.
        """

        return not self.__yes


class DeaductionDialog(QMessageBox):
    """
    Generic Deaduction dialog.
    """
    def __init__(self, title="d∃∀duction", html=True, OK=True):

        super().__init__()
        self.setTextFormat(Qt.RichText)

        if not title.endswith("d∃∀duction"):
            title += " — d∃∀duction"
        self.setWindowTitle(title)
        # self.setModal(True)

        if OK:
            self.addButton(QMessageBox.Ok)


class DeaductionTutorialDialog(DeaductionDialog):
    """
    This class is a modal QMessageBox which displays a tutorial-like message.
    The message can be dismissed forever by checking the "do not play again"
    button.
    """

    def __init__(self,
                 config_name,
                 title="Tutorial — d∃∀duction",
                 text=None):
        super().__init__(title=title)

        self.config_name = config_name
        if config_name:
            show = cvars.get(config_name)
            if show is False:
                QTimer.singleShot(0, self.reject)
        if text:
            self.setText(text)

        # self.dismiss_checkbox = QCheckBox(_("Do not show again"))
        # self.addButton(self.dismiss_checkbox, QMessageBox.HelpRole)

        self.dismiss_button = self.addButton(_("Do not show again"),
                                             QMessageBox.HelpRole)

        self.dismiss_button.clicked.connect(self.dismiss)

    def dismiss(self):
        cvars.set(self.config_name, False)

