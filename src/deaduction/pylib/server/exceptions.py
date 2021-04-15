"""
##################################################
# exceptions.py : Exceptions for ServerInterface #
##################################################

Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
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

from pprint import                        pformat
from deaduction.pylib.config.i18n import _
from deaduction.pylib.memory import EventNature, JournalEvent


class FailedRequestError(Exception):
    def __init__(self, errors, lean_code):
        super().__init__(f"Failed request to server with errors : \n"
                         f"{pformat(errors, indent=4)}")
        if lean_code and lean_code.error_message:
            self.message = lean_code.error_message
        else:
            self.message = _('Error')

        details = ""
        for error in errors:
            details += "\n" + error.text
        self.info = {'details': details}