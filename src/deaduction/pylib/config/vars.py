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
import sys
from sys import platform
from gettext import gettext as _
import logging
from . import dirs
import toml

import deaduction.pylib.utils.dict as udict

FACTORY_CONFIG_FILE_PATH = (dirs.share / "config.toml").resolve()
USER_CONFIG_FILE_PATH    = (dirs.local / "config.toml").resolve()

__dict_factory = dict() # Loaded configuration from default config file
__dict_user    = dict() # Loaded configuration from user config.

log = logging.getLogger(__name__)


#def load():
#    global __dict_factory
#    global __dict_user
#
#    log.info(_("Loading configuration files"))
#    log.debug(_("Factory config path: {}").format(FACTORY_CONFIG_FILE_PATH))
#    log.debug(_("User config path: {}").format(USER_CONFIG_FILE_PATH))
#
#    # Load configuration file
if FACTORY_CONFIG_FILE_PATH.exists():
    # print('path exists')
    __dict_factory.update(toml.load(str(FACTORY_CONFIG_FILE_PATH)))
    # from pprint import pprint
    # pprint(__dict_factory)
else:
    # breakpoint()
    print('path DOES NOT exist')

if USER_CONFIG_FILE_PATH.exists():
    __dict_user.update(toml.load(str(USER_CONFIG_FILE_PATH)))


def save():
    global __dict_factory
    global __dict_user

    log.info(_("Saving configuration file"))
    with open(str(USER_CONFIG_FILE_PATH), "w") as fhandle:
        toml.dump(__dict_user, fhandle)


def get(k: str, default_value=None):
    """
    Return the wanted setting variable. dot get style,
    for example, calling the function with package.linux
    returns __dict["package"]["linux"]
    """
    global __dict_factory
    global __dict_user
    
    # Try in user config
    try:
        return udict.dotget(__dict_user, k)
    except KeyError:
        # Call the os specific version if it exists
        if os_name:
            if udict.dotget(__dict_factory, os_name + '.' + k,
                                    default_value="NONE") != "NONE":
                k = os_name + '.' + k
        try:
            return udict.dotget(__dict_factory, k, default_value=default_value)
        except KeyError as exc:
            raise KeyError(_("Could not get config value: ") + str(exc))


def set(k, v, if_not_exists=False ):
    """
    Sets an item in a directory with a hierarchical path.
    Creates sub directories if needed.

    :param k: The hierarchical key, separated with dots
    :param v: The value to set
    :param if_not_exists: Set value only if key doesn't exist

    :return: True if item was set, False otherwise
    """
    global __dict_user

    udict.dotset(__dict_user, k, v, if_not_exists)


def copy():
    global __dict_user
    return __dict_user.copy()


def restore(initial_cvars):
    global __dict_user
    __dict_user = initial_cvars


def update(new_settings: dict):
    if new_settings:
        for (key, value) in new_settings.items():
            set(key, value)




# Add os name; so this can be overridden in (user's) config.toml
# Otherwise, vars.get("others.os") --> "linux", "darwin" or "windows"
os_name = ""  # For first time, do not remove otherwise 'get' method crashes!
os_name = get('others.os')
if not os_name:
    os_name = ("linux" if platform.startswith("linux")
               else "darwin" if platform.startswith("darwin")
               else "windows" if (platform.startswith("cygwin") or
                                  platform.startswith("win32"))
               else "")
    set('others.os', os_name)

if __name__ == "__main__":
    from pprint import pprint

    print("############## Factory config ##############")
    for k,v in __dict_factory.items():
        print(f"→ {k} = ",end="")
        pprint(v, indent=4)

    print("\n############## User config ##############")
    for k,v in __dict_user.items():
        print(f"→ {k} = ",end="")
        pprint(v, indent=4)
