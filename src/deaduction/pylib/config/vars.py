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
    print('Config path DOES NOT exist!?')

if USER_CONFIG_FILE_PATH.exists():
    # __dict_user.update(toml.load(str(USER_CONFIG_FILE_PATH)))
    with open(str(USER_CONFIG_FILE_PATH), 'rb') as f:
        __dict_user.update(toml.loads(f.read().decode('utf-8')))


def get(k: str, default_value=None):
    """
    Return the wanted setting variable. dot get style,
    for example, calling the function with package.linux
    returns __dict["package"]["linux"]
    """
    global __dict_factory
    global __dict_user

    # print("Factory:")
    # print(__dict_factory)
    # print("Usr:")
    # print(__dict_user)
    # test = True
    # try:
    #     test = udict.dotget(__dict_user, "functionality.allow_induction")
    # except:
    #     pass
    # print(f"Allow_induction: {test}")
    # if not test:
    #     raise TypeError("Toto")

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


def update(new_settings: dict) -> dict:
    """
    Update user dict according to new_settings.
    new_settings keys can be in dotted format or nested dict format (or mixed).
    If value is a dict then its keys are added to key as suffixes.
    """
    # Obsolete docstring:
    # Update cvars with new_settings, a dict where keys may refer to dict using
    # the dot notation. Beware that if value is a dict then the dict will be
    # replaced by value, not updated.

    modified_settings = dict()
    dotted_settings = dict()  # Will be populated by nested dict

    if new_settings:
        for (key, value) in new_settings.items():
            print(f"{key}  --> {value}")
            old_value = get(key)
            if isinstance(value, dict) and isinstance(old_value, dict):
                for subkey, subvalue in value.items():
                    dotted_settings[key + '.' + subkey] = subvalue
            elif old_value != value:
                print(f"Modifying cvars key={key} {old_value} --> {value}")
                set(key, value)
                modified_settings[key] = old_value

        more_modified = update(dotted_settings)
        modified_settings.update(more_modified)
    return modified_settings


def recursive_update(new_settings: dict, original_usr_dic=None,
                     original_fact_dic=None, remove_id_values=True):
    """
    Adapted to format with nested dicts.

    Update cvars with new_settings.
    Return the part of cvar that have been modified.

    e.g.
    original_usr_dic = {'functionality': {'Lean_method: True, 'Toto': 0},
                    'others': 123}
    new_settings = {'functionality': {Lean_method': False, 'Jean-Pierre': 1},
                    'others': 123}

    -->
    original_usr_dic = {'functionality': {'Lean_method: False, 'Toto': 0,
                                        'Jean-Pierre': 1}
    return {'functionality': {Lean_method': True, 'Jean-Pierre': None}}

    """
    # FIXME: not used anymore
    log.info("Update cvars")
    print(f"From {original_usr_dic} to {new_settings}")
    global __dict_user
    if not original_usr_dic:
        original_usr_dic = __dict_user
    if not original_fact_dic:
        original_fact_dic = __dict_factory

    modified_original_dict = dict()
    for key, value in new_settings.items():
        if not isinstance(value, dict) or key not in original_fact_dic.keys():
            # if original_usr_dic is __dict_user:  # Also search in factory dict
            #     original_value = get(key, "none")
            #     if original_value == "none":
            #         original_value = None
            #         log.warning(f"Key {key} not found in cvars")
            # else:
            original_value = original_usr_dic.get(key)
            if original_value is None:
                original_value = original_fact_dic.get(key)
            if original_value != value:
                print(f"Modifying cvars key={key} {original_value} --> {value}")
                if value is None:
                    log.warning("VALUE is NONE")
                modified_original_dict[key] = original_value
                original_usr_dic[key] = value
        else:
            more_fact_dic = original_fact_dic[key]
            more_usr_dic = original_usr_dic.get(key)
            if not more_usr_dic:
                more_usr_dic = dict()
                original_usr_dic[key] = more_usr_dic
            more_mod_dic = recursive_update(value, more_usr_dic, more_fact_dic)
            if more_mod_dic:
                modified_original_dict[key] = more_mod_dic

    return modified_original_dict


def save():
    global __dict_factory
    global __dict_user

    log.info(_("Saving configuration file"))
    with open(str(USER_CONFIG_FILE_PATH),
              mode="w", encoding='utf-8') as fhandle:
        toml.dump(__dict_user, fhandle)


def save_single_key(key):
    """
    Add to the current USER_CONFIG_FILE_PATH a single entry.
    Does not affect the current __dict_user!
    """

    value = get(key)
    global __dict_user
    tmp_dict_user = dict()

    # Read usr config file
    if USER_CONFIG_FILE_PATH.exists():
        with open(str(USER_CONFIG_FILE_PATH), 'rb') as f:
            tmp_dict_user.update(toml.loads(f.read().decode('utf-8')))

    # Add entry to be saved
    udict.dotset(tmp_dict_user, key, value, if_not_exists=False)

    # Save new dict
    log.debug(_(f"Saving {key}:{value} in config file"))
    with open(str(USER_CONFIG_FILE_PATH),
              mode="w", encoding='utf-8') as fhandle:
        toml.dump(tmp_dict_user, fhandle)


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
