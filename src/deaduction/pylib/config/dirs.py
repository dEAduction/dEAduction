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
from   gettext import gettext as _

log = logging.getLogger(__name__)

############################################
# Path objects
############################################
pkg_dir  = (Path(__file__) / "../../../").resolve()

# Share paths
share    = (pkg_dir / "share").resolve()
icons    = (share / "graphical_resources" / "icons").resolve()

# Home paths
home     = Path.home()
local    = (home / ".deaduction").resolve()

############################################
# Utilities
############################################

#def init():
#    check_dir(local)
