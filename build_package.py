"""
##################################################
# build_package.py : dEAduction package builder #
##################################################

Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : April 2021

    Inspired from https://github.com/pypa/pep517

Copyright (c) 2021 the dEAduction team

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

from deaduction.pylib import logger
logger.configure(debug=True)

import os
import toml
import logging

from pathlib         import Path
from pep517.wrappers import Pep517HookCaller

log = logging.getLogger(__name__)

# ┌────────────────────────────────────────┐
# │ Global configuration                   │
# └────────────────────────────────────────┘
SRC_PATH   = (Path(__file__) / "..").resolve()
SHARE_PATH = (SRC_PATH / "src/share")
BUILD_PATH = (SRC_PATH / "build").resolve()

# ┌────────────────────────────────────────┐
# │ Utilities                              │
# └────────────────────────────────────────┘
def build_manifest():
    """
    List all the regular files in the SHARE
    path, and builds the according MANIFEST.in
    file to include them in the generated wheel
    package.
    """

    log.info("Building MANIFEST.in file")

    files_list = filter( lambda f: f.is_file(), SHARE_PATH.rglob("*") )

    with open("MANIFEST.in", "w") as fhandle:
        for fpath in files_list:
            log.info("Prout")
            print(f"include {fpath}", file=fhandle)

def build_wheel():
    """
    Build the wheel package
    """

    log.info("Building the wheel package")

    # ────── Retrieve build system info. ───── #
    with open(str(SRC_PATH / "pyproject.toml")) as fhandle:
        data      = toml.load(fhandle)
        build_sys = data['build-system']

    print(build_sys['requires'])

    # ─────────── Init build hooks ─────────── #
    hooks = Pep517HookCaller( SRC_PATH,
                              build_backend = build_sys['build-backend'],
                              backend_path  = build_sys.get('backend-path') )

    config_options = {}
    print(hooks.get_requires_for_build_wheel(config_options))

    # ───────────── Launch build! ──────────── #
    whl_filename = hooks.build_wheel(str(BUILD_PATH), config_options)
    assert os.path.isfile(str(BUILD_PATH / whl_filename))

# ┌────────────────────────────────────────┐
# │ Main procedure                         │
# └────────────────────────────────────────┘

# ──────── Build MANIFEST.in file ──────── #
#build_manifest()
build_wheel()

