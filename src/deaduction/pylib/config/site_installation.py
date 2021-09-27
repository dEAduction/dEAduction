"""
#################################################
# platform.py : Platform installation managment #
#################################################

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

import platform
import logging
from   gettext import gettext as _

import deaduction.pylib.packager.package as package
import deaduction.pylib.config.vars      as cvars

from   deaduction.pylib.packager.exceptions import (PackageCheckError)

log = logging.getLogger(__name__)

__platform_os = platform.system().lower() # Evaluated at first module import,
                                          # should give linux, windows or
                                          # darwin (for mac osx).

packages = dict()                         # this dict. contains Package object
                                          # that are found in config.

def init():
    global packages

    # Load package config
    # merge platform-agnostic packages with platform-specific ones.
    plist    = { **cvars.get("package.all"),
                 **cvars.get(f"package.{__platform_os}") }

    for name, conf in plist.items():
        packages[name] = package.from_config(conf)


def check():
    """
    Checks for packages installation, returns list of invalid
    packages. The user can then process this list to
    install them.
    """
    global packages

    failed_checks=[]

    log.info(_("Check packages installation"))
    for pkg_name, pkg in packages.items():
        try:
            pkg.check()
        except PackageCheckError as exc:
            log.warning(_("Failed checking package {}: {}")
                            .format(pkg_name,str(exc)) )
            if exc.dbg_info: log.debug(str(exc.dbg_info))

            failed_checks.append((pkg_name, pkg, exc,))
        
    return failed_checks

def has_package(name):
    if not name in packages:
        raise RuntimeError( _("No package {} found in configuration")
                            .format(name) )
