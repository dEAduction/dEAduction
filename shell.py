"""
#####################################################
# shell.py : Simple shell for testing and debugging #
#####################################################

Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
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

import deaduction.pylib.logger                   as log
import deaduction.pylib.config.environ           as cenv
import deaduction.pylib.config.dirs              as cdirs
import deaduction.pylib.config.vars              as cvars
import deaduction.pylib.config.site_installation as inst

# Stuff init
log.configure()
cvars.load()
cenv.init()
cdirs.init()
inst.init()

print("Welcome to the d∃∀duction shell !!!")
