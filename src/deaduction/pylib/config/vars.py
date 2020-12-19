"""
#########################################
# vars.py : Get configuration variables #
#########################################

Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : July 2020

    The configuration variables are stored primarly in two files :
        -> The user end configuration is in ~/.deaduction/config.toml
        -> The factory configuration is in <deaduction package>/share/config.toml.

    By default, user configuration has precedence over factory configuration.
    the user should not have its own configuration, unless it is an advanced
    user who wish to mess with that stuff.

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
import logging
from . import dirs

FACTORY_CONFIG_FILE_PATH = (dirs.share / "config.toml").resolve()
USER_CONFIG_FILE_PATH    = (dirs.local / "config.toml").resolve()

dict_ = dict() # Contains loaded configuration

log = logging.getLogger(__name__)

def load():
    log.info(_("Loading configuration files"))

    # Load configuration file
    dict_ = toml.load(str(FACTORY_CONFIG_FILE_PATH))
    dict_.update(toml.load(str(USER_CONFIG_FILE_PATH)))

def save():
    log.info(_("Saving configuration file"))
    toml.dump(dict_, CONFIG_FILE_PATH)

def get(name: str):
    return dict_[name]

def set(name: str, value: any):
    dict_[name] = value


