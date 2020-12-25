"""
################################################################################
# extract_mathlib_rev.py : Temporary script to extract mathlib revision number #
################################################################################

    Note : this is dumb and will be removed as soon as the package system will
    be running.

Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : October 2020

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

import toml
import sys

from   pathlib import Path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please give leanpkg.toml file path")
        sys.exit(1)

    with Path(sys.argv[1]).resolve().open() as fhandle:
        data = toml.load(fhandle)
        print(data["dependencies"]["mathlib"]["rev"])
