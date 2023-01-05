"""
#####################################################
# installation.py : Manage lean server installation #
#####################################################

Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : December 2020

    TODO : Export leanpkg.toml file from config.

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

import deaduction.pylib.config.dirs      as cdirs
import deaduction.pylib.utils.filesystem as fs

from   pathlib import Path


class LeanEnvironment:
    def __init__(self, inst):
        # Check for packages
        inst.has_package("lean")
        inst.has_package("mathlib")

        # Get path information
        self.lean_path    = inst.packages["lean"].path
        self.mathlib_path = inst.packages["mathlib"].path
        self.leanpkg_path_dir = cdirs.local

    @property
    def absolute_lean_libs(self):
        """
        Construct path information to be put in leanpkg.path file.
        """
        # Respectively paths to the Lean library, the Mathlib library,
        #  the deaduction lean src.
        paths = [(self.lean_path / "lib" / "lean" / "library").resolve(),
                 (self.mathlib_path / "src").resolve(),
                 cdirs.usr_lean_src_dir]

        return paths

    @property
    def lean_libs(self):
        """
        Construct path information to be put in leanpkg.path file.
        If possible, relative paths are used, relative to dst_path.
        Note that Lean for Windows does not accept absolute paths.
        """

        abs_paths = self.absolute_lean_libs
        rel_paths = []
        for path in abs_paths:
            if path.is_relative_to(self.leanpkg_path_dir):
                rel_paths.append(path.relative_to(self.leanpkg_path_dir))
            else:
                rel_paths = None
                break
        if not rel_paths:
            print("Using absolute paths for Lean/Mathlib files")
            return abs_paths
        else:
            return rel_paths

    @property
    def lean_bin(self):
        """
        Get path to lean binary
        """
        return (self.lean_path / "bin" / "lean").resolve()

    def write_lean_path(self):
        """
        Writes the leanpkg.path file content to the file path
        self.leanpkg_path_dir. Note that the paths in the leanpkg.path file
        MUST be relative to dst_path, where that file is written.
        """

        dst_path = self.leanpkg_path_dir / "leanpkg.path"

        with open(str(fs.path_helper(dst_path)), "w") as fhandle:
            for pp in self.lean_libs:
                print(f"path {str(pp)}", file=fhandle)
