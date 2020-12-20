"""
#########################################################
# environ.py : Environment variables used in dEAduction #
#########################################################

Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : December 2020

    This file defines various environment variables that can be
    used in d∃∀duction config files. for example, to give a
    path to a package, the user can indicate :

    [package.linux.mathlib]
    type="archive"
    path="$DEADUCTION_HOME/mathlib"

    Then, when the config is loaded, the environment variable will
    be expanded.

    The environment variables are defined here as the program can be
    executed both from a python package installation, or from some
    other form of setup (for example on windows).

    This module must be imported at least one time in the program, at
    the beginning.

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

import deaduction.pylib.config.dirs as dirs

import os

os.environ["DEADUCTION_PKG"]   = str(dirs.pkg_dir)
os.environ["DEADUCTION_HOME"]  = str(dirs.local)
os.environ["DEADUCTION_SHARE"] = str(dirs.share)
