"""
##################################################
# exceptions.py : Exceptions for the util module #
##################################################

Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : August 2020

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

from gettext import gettext as _
from pathlib import Path

############################################
# filesystem exceptions
############################################
class FileCheckError(Exception):
    def __init__(self, path: Path, msg: str):
        super().__init__(msg)
        self.path = path

class FileDontExistError(FileCheckError):
    def __init__(self, path: Path ):
        super().__init__( path, _("File {} not found").format(str(path)) )

class FileNotDirectoryError(FileCheckError):
    def __init__(self, path: Path):
        super().__init__(path, _("Path {} is not a directory"))

class FileNotExploitableError(Exception):
    def __init__(self, path: Path):
        super().__init__(_("Path {} does not point to an exploitable file"))
