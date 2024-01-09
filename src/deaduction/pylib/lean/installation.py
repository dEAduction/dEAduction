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

from pathlib import Path
from shutil import copy


class LeanEnvironment:
    def __init__(self, inst):
        # Check for packages
        inst.has_package("lean")
        inst.has_package("mathlib")

        # Get path information
        self.lean_path    = inst.packages["lean"].path
        self.mathlib_path = inst.packages["mathlib"].path
        self.leanpkg_path_dir = cdirs.local

    def absolute_lean_libs(self) -> [Path]:
        """
        Construct path information to be put in leanpkg.path file.
        """
        # Respectively paths to the Lean library, the Mathlib library,
        #  the deaduction lean src.
        usr_dir = cdirs.usr_lean_exercises_dir
        usr_subdirs = [x for x in usr_dir.iterdir() if x.is_dir()]
        tests_dir = cdirs.usr_tests_dir
        tests_subdirs = [x for x in tests_dir.iterdir() if x.is_dir()]
        paths = ([(self.lean_path / "lib" / "lean" / "library").resolve(),
                  (self.mathlib_path / "src").resolve(),
                  cdirs.usr_lean_src_dir,
                  usr_dir, tests_dir, cdirs.history.resolve()]
                 + usr_subdirs + tests_subdirs)

        return paths

    def lean_libs(self, additional_abs_path=None):
        """
        Construct path information to be put in leanpkg.path file.
        If possible, relative paths are used, relative to dst_path.
        Note that Lean for Windows does not accept absolute paths.
        """

        abs_paths = self.absolute_lean_libs()
        if additional_abs_path:
            abs_paths.append(additional_abs_path)
        rel_paths = []
        for path in abs_paths:
            # From Python3.9 use is_relative_to()
            try:
                rel_paths.append(path.relative_to(self.leanpkg_path_dir))
            except ValueError:
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

    def write_lean_path(self, additional_abs_path=None):
        """
        Writes the leanpkg.path file content to the file path
        self.leanpkg_path_dir. Note that the paths in the leanpkg.path file
        MUST be relative to dst_path, where that file is written.
        """

        dst_path = self.leanpkg_path_dir / "leanpkg.path"

        with open(str(fs.path_helper(dst_path)), "w") as fhandle:
            for pp in self.lean_libs(additional_abs_path=additional_abs_path):
                print(f"path {str(pp)}", file=fhandle)

    def all_lean_exercises_files(self):
        """
        Return the list fo lean files in all dirs of the lean_path.
        """

        files = []
        for directory in self.lean_libs():
            files.extend(directory.glob('*.lean'))
        return files

    def other_file_with_same_name(self, abs_path: Path):
        """
        Return True if a file in self.all_lean_exercises_files(), distinct
        from abs_path, has the same name.
        """

        name = abs_path.name
        for other in self.all_lean_exercises_files():
            if name == other.name and other != abs_path:
                return other

    def is_in_leanpath(self, abs_path) -> bool:
        """
        Return True if abs_path points to a file accessible to Lean.
        """

        new_dir = (abs_path if abs_path.is_dir()
                   else abs_path.parent)

        return new_dir in self.absolute_lean_libs()

    def check_file_path(self, abs_path):
        """
        If abs_path is not in one of the directories in the leanpath,
        then copy file in cdirs.tmp_exercises_dir.
        """
        if not self.is_in_leanpath(abs_path):
            new_file = cdirs.tmp_exercises_dir / abs_path.name
            copy(abs_path, new_file)


