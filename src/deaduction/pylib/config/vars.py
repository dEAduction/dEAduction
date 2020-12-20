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

def get(k: str):
    """
    Return the wanted setting variable. dot get style,
    for example, calling the function with package.linux
    returns → _dict["package"]["linux"]
    """
    try:
        keys = list(k.split("."))
        rp = _dict
        for idx in range(0, len(keys)-1):
            rp = rp[keys[idx]]
        return rp[keys[-1]]
    except KeyError as e : raise KeyError( "%s in %s" % (str(e), k))

def set( k, v, if_not_exists=False ):
    """
    Sets an item in a directory with a hierarchical path. Creates sub directories
    if needed

    :param r: The destination dict
    :param k: The hierarchical key, separated with dots
    :param v: The value to set
    :param if_not_exists: Set value only if key doesn't exist

    :return: True if item was set, False otherwise
    """

    # Test cases :
    # 1 : default case (no depth)
    # 2 : subdict (2 levels of depth)
    # 3 : Excepted dict value exception
    # 5 : if_not_exists don't overwrite

    keys = list(k.split("."))
    dst  = _dict # Destination
    for idx in range(0,len(keys)-1):
        kp = keys[idx]
        if not kp in dst : dst[kp] = dict()
        dst = dst[kp]

    # If key not in last subdict, so the item doesn't exist yet
    klast = keys[-1]
    if (not klast in dst) or (not if_not_exists) :
        dst[klast] = v
        return True
    else : return False
