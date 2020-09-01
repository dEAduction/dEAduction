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

from typing import (Callable,
                    Dict,
                    Optional)

import requests
from pathlib import Path
import tempfile
import shutil
import traceback

import logging

from gettext import gettext as _

from deaduction.pylib.utils import filesystem as fs
from tempfile import TemporaryFile
import tarfile
import git

import deaduction.pylib.config.dirs as dirs

log = logging.getLogger(__name__)

# ┌────────────────────────────────────────┐
# │ Package class                          │
# └────────────────────────────────────────┘
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

# ┌────────────────────────────────────────┐
# │ ArchivePackage class                   │
# └────────────────────────────────────────┘
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
            log.debug(traceback.format_exc())

            if self.path.exists():
                self.remove()
            self.install()


    def install(self):
        log.info(_("Installing package {} from archive").format(self.path))
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

# ┌────────────────────────────────────────┐
# │ GitPackage class                       │
# └────────────────────────────────────────┘
class GitPackage(Package):
    def __init__(self,
                 path: Path,
                 remote_url: str,
                 remote_branch: str,
                 remote_commit: Optional[str] = None ):
        super().__init__(path)

        self.remote_url    = remote_url   
        self.remote_branch = remote_branch
        self.remote_commit = remote_commit

    def _check_repo_state(self):
        log.info(_("Checking git repo state for package {}").format(str(self.path)))

        repo = git.Repo(str(self.path.resolve()))
        assert self.remote_branch == str(repo.active_branch)

        if self.remote_commit:
            assert self.remote_commit == str(repo.commit())

    def check(self):
        try:
            self._check_folder()
            self._check_repo_state()
        except Exception as e:
            log.warning(_("Failed check package {}, reinstall")
                        .format(self.path))
            log.debug(traceback.format_exc())

            if self.path.exists():
                self.remove()
            self.install()

    def install(self):
        log.info(_("Install package {} from git repo").format(self.path))

        # Create empty local repo
        empty_repo = git.Repo.init(str(self.path.resolve()))

        # Set remote and fetch
        origin     = empty_repo.create_remote('origin', self.remote_url)
        origin.fetch()

        # Create local tracking branch and checkout
        empty_repo.create_head(self.remote_branch, origin.refs[self.remote_branch])
        empty_repo.heads[self.remote_branch].set_tracking_branch(origin.refs[self.remote_branch]) # set local branch to track remote branch
        empty_repo.heads[self.remote_branch].checkout()
