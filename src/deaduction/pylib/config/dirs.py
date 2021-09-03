"""
###############################
# dirs.py : Directories links #
###############################

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

import logging
from   pathlib import Path
import os

import deaduction.pylib.utils.filesystem as fs

log = logging.getLogger(__name__)

############################################
# Path objects
############################################
pkg_dir  = (Path(__file__) / "../../../").resolve()

# Share paths
share          = (pkg_dir / "share").resolve()
icons          = (share / "graphical_resources" / "icons").resolve()
courses        = (share / "courses").resolve()


# Home paths
home     = Path.home()
if os.getenv("DEADUCTION_DEV_MODE", '0') == '1':
    local = ( home / ".deaduction-dev" ).resolve()
else:
    local = (home / ".deaduction").resolve()
journal        = (local / "deaduction_journal").resolve()
test_exercises = (local / "test_exercises").resolve()
all_courses_ipf_dir = (local / "initial_proof_states").resolve()


############################################
# Utilities
############################################
def init():
    fs.check_dir(local, create=True)
    fs.check_dir(all_courses_ipf_dir, create=True)