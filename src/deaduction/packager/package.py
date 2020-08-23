"""
############################################
# package.py : Manage package installation #
############################################

Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : August 2020

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

import requests
from pathlib import Path
from typing import Callable
import tempfile
import shutil

import logging

from gettext import gettext as _
from typing import Dict

from deaduction.pylib.utils import filesystem as fs
from tempfile import TemporaryFile
import tarfile

import deaduction.pylib.config.dirs as dirs

log = logging.getLogger(__name__)

############################################
# Package class definition
############################################

class Package:
    def __init__(self, path: Path):
        self.path   = Path(path).resolve()

    ############################################
    # Public interface to be implemented
    ############################################
    def check(self):
        pass

    def install(self):
        pass

    def remove(self):
        """
        Remove package directory
        """
        self.path = self.path.resolve()

        if not str(self.path).startswith(str(dirs.local)):
            raise RuntimeError( _("invalid directory, must be "
                                  "in $HOME/.deaduction folder !!!"))
        shutil.rmtree(str(self.path.resolve()))

    ############################################
    # Protected utilities functions
    ############################################
    def _check_folder(self):
        log.info(_("Checking package folder for {}").format(self.path))
        fs.check_dir(self.path)


class ArchivePackage(Package):
    def __init__(self, path: Path,
                 archive_url: str,
                 archive_checksum: str = None,
                 archive_hlist: Path = None):

        super().__init__(path)

        self.path             = path

        self.archive_url      = archive_url
        self.archive_checksum = archive_checksum
        self.archive_hlist    = archive_hlist

    def _check_files(self):
        if self.archive_hlist is not None:
            log.info(_("Checking files for {}").format(self.path))
            hlist_ref  = fs.HashList.from_file(self.archive_hlist)
            hlist_dest = fs.HashList.from_path(self.path)

            diff = list(hlist_dest.diff(hlist_ref))
            if len(diff) > 0:
                raise RuntimeError("Found differences in files, reinstall.")

    def check(self):
        try:
            self._check_folder()
            self._check_files()
        except Exception as e:
            log.warning(_("Failed check package {}, reinstall")
                        .format(self.path))

            if self.path.exists():
                self.remove()
            self.install()


    def install(self):
        log.info(_("Installing package {}").format(self.path))
        with TemporaryFile() as fhandle:
            checksum = fs.download(self.archive_url, fhandle)
            if self.archive_checksum and (self.archive_checksum != checksum):
                raise AssertionError(_("Invalid checksum: {}, expected {}").format(
                    checksum, self.archive_checksum))

            fhandle.seek(0)

            log.info(_("Extract file to {}").format(self.path))
            with tarfile.open(fileobj=fhandle) as tf:
                tf.extractall(path=str(self.path))

        log.info(_("Installed Package to {}").format(self.path))
