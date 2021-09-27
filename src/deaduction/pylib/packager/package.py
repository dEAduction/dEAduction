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

from typing import (Callable, Dict, Optional)
import requests
from   pathlib import Path
import tempfile
import shutil
import traceback

import logging

from gettext import gettext as _

from deaduction.pylib.utils import filesystem as fs
from tempfile import TemporaryFile
import os.path
#import git

from .exceptions import (PackageCheckError)

import tarfile
import zipfile

import deaduction.pylib.config.dirs as dirs
from functools import partial

from deaduction.pylib.utils.exceptions import (FileCheckError)


log = logging.getLogger(__name__)

# ┌────────────────────────────────────────┐
# │ Package class                          │
# └────────────────────────────────────────┘
class Package:
    def __init__(self, path: Path):
        self.path   = fs.path_helper(path)

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
        if not str(self.path).startswith(str(dirs.local)):
            log.warning(_("Directory should be $HOME/.deaduction folder !!!"))
            # raise RuntimeError( _("invalid directory, must be "
            #                       "in $HOME/.deaduction folder !!!"))

        if self.path.exists(): # remove only if path exists
            shutil.rmtree(str(self.path.resolve()))

    ############################################
    # Protected utilities functions
    ############################################
    def _check_folder(self):
        log.info(_("Checking package folder for {}").format(self.path))
        try: fs.check_dir(self.path, exc=True)
        except FileCheckError as e:
            raise PackageCheckError(self,
                                    _("Failed to check for folder at {}")
                                        .format(str(self.path)),
                                        dbg_info=e )

# ┌────────────────────────────────────────┐
# │ ArchivePackage class                   │
# └────────────────────────────────────────┘
class ArchivePackage(Package):
    def __init__(self, path: Path,
                 archive_url: str,
                 archive_checksum: str = None,
                 archive_hlist: Path   = None,
                 archive_root: Path    = None,        # Root folder
                 archive_type: str     = "tar"):      # can be "tar" or "zip"
                 

        super().__init__(path)

        self.archive_url      = archive_url
        self.archive_checksum = archive_checksum
        self.archive_hlist    = fs.path_helper(archive_hlist)
        self.archive_root     = archive_root
        self.archive_type     = archive_type

    def _check_files(self):
        """
        For dict differ:
            * Non existing file:
                [('add', '', [(PosixPath('lib/lean/library/tools/debugger/default.lean'), ('556dcaa5ae2481d30712ecce863dc7ac3c8cfc0f', '644'))])]

            * Modified file (not the same hash):
                [('change', [PosixPath('lib/lean/library/tools/debugger/default.lean')], (('23e56aa980901f09eb093a31711e505ec5b99542', '644'), ('556dcaa5ae2481d30712ecce863dc7ac3c8cfc0f', '644')))]

            * Modified permissions:
                [('change', [PosixPath('lib/lean/library/tools/debugger/default.lean')], (('556dcaa5ae2481d30712ecce863dc7ac3c8cfc0f', '744'), ('556dcaa5ae2481d30712ecce863dc7ac3c8cfc0f', '644')))]

            * File that shouldn't exixt:
                [('remove', '', [(PosixPath('bin/prout'), ('da39a3ee5e6b4b0d3255bfef95601890afd80709', '644'))]]

            Example dict differ:
                [('change',
                  [PosixPath('lib/lean/library/tools/debugger/default.lean')],
                  (('556dcaa5ae2481d30712ecce863dc7ac3c8cfc0f', '744'),
                   ('556dcaa5ae2481d30712ecce863dc7ac3c8cfc0f', '644'))),
                 ('remove',
                  '',
                  [(PosixPath('bin/prout'),
                    ('da39a3ee5e6b4b0d3255bfef95601890afd80709', '644')),
                   (PosixPath('bin/prout2'),
                    ('da39a3ee5e6b4b0d3255bfef95601890afd80709', '644'))])]

                → File lib/lean/library/tools/debugger/default.lean has changed permissions
                → File bin/prout and bin/prout2 shouldn't exist in the folder
                → This example illustrates how changes of the same category are grouped
                  in the result from dictdiffer.

            Another example
                [('change',
                  [PosixPath('lib/lean/library/tools/debugger/default.lean')],
                  (('556dcaa5ae2481d30712ecce863dc7ac3c8cfc0f', '744'),
                   ('556dcaa5ae2481d30712ecce863dc7ac3c8cfc0f', '644'))),
                 ('add',
                  '',
                  [(PosixPath('bin/leanpkg'),
                    ('6f96e5ae74c7b26e9bd72a3b8c8ed71be8bfb8ca', '755')),
                   (PosixPath('bin/lean'),
                    ('430051c09e3d8604edf110c93d8829ce6def4a24', '755'))]),
                 ('remove',
                  '',
                  [(PosixPath('bin/prout'),
                    ('da39a3ee5e6b4b0d3255bfef95601890afd80709', '644')),
                   (PosixPath('bin/prout2'),
                    ('da39a3ee5e6b4b0d3255bfef95601890afd80709', '644'))])]
        """

        if self.archive_hlist is not None:
            log.info(_("Checking files for {}").format(self.path))
            hlist_ref  = fs.HashList.from_file(self.archive_hlist)
            hlist_dest = fs.HashList.from_path(self.path)

            diff       = list(hlist_dest.diff(hlist_ref))

            for dd in diff:
                # Shape: ('add', '', [ (path, data), (path, data), ... ] )
                if   dd[0] == "add":
                    raise PackageCheckError( self, _("Missing files {}, reinstalling package!").format(dd[2]))

                # Shape: ('remove', '', [ (path, data), (path, data), ... ] )
                elif dd[0] == "remove":
                    log.warning(_("Additional file {} found in "
                                  "directory").format(str(self.path)))

                # Shape: ('change', [path], (data_now, data_orig))
                elif dd[0] == "change":
                    path                = dd[1][0]
                    data_now            = dd[2][0]
                    data_orig           = dd[2][1]

                    hash_now,perm_now   = data_now
                    hash_orig,perm_orig = data_orig

                    # Compare hashes
                    if hash_now != hash_orig:
                        raise PackageCheckError( self, _("File {} is invalid, reinstalling package").format(str(path)) )

                    # Change permissions
                    else: 
                        log.warning(_("File {} has permissions {}, excepted {}, updating").format(str(path), perm_now, perm_orig))
                        (self.path / path).chmod(int(perm_orig,8))

                else:
                    raise PackageCheckError( self, _("Uknown dict differ {}, reinstalling package").format(dd) )

    def check(self):
        self._check_folder()
        self._check_files()

        #try:
        #    self._check_folder()
        #    self._check_files()
        #except Exception as e:
        #    log.warning(_("Failed check package {}, reinstall")
        #                .format(self.path))
        #    log.debug(traceback.format_exc())

        #    if self.path.exists():
        #        self.remove()
        #    self.install() # TODO # if error, only raise exception, don't
        #                   #  install !!!

    def install(self, on_progress: Callable = None):
        """
        Downloads and extracts the archive in the destination directory.

        Please note the following regarding archive_root :
            → the archive is extracted into a temporary folder.
            → Then, if archive_root is given, the whole temp path is moved to
            the destination, else, it is only the component given by
            archive_root that is moved.
        """
        self.remove()

        log.info(_("Installing package {} from archive").format(self.path))
        with TemporaryFile() as fhandle:
            checksum = fs.download(self.archive_url, fhandle, on_progress)
            if self.archive_checksum and (self.archive_checksum != checksum):
                raise AssertionError(_("Invalid checksum: {}, expected {}").format(
                    checksum, self.archive_checksum))

            fhandle.seek(0)

            log.info(_("Extract file to {}").format(self.path))

            # Create destination folder
            #self.path.mkdir(exist_ok=True) # exist_ok=True → Don't bother if
            #                               # path already exists

            # Get correct archiving module to extract the file
            archive_open_fkt    = { "tar": lambda x: tarfile.open(fileobj=x),
                                    "zip": lambda x: zipfile.ZipFile(x) }

            if not self.archive_type in archive_open_fkt:
                raise KeyError(_("Invalid archive type {}")
                               .format(self.archive_type))
            archive_module = archive_open_fkt[self.archive_type]

            # Create temporary directory
            tpath = Path(tempfile.mkdtemp()).resolve()
            log.debug(_("Temporary path is {}").format(tpath))

            with archive_module(fhandle) as tf:
                tf.extractall(path=str(tpath))

                if self.archive_root:
                    tpath = (tpath / self.archive_root).resolve()

                log.info(_("→ Move {} to {}").format(tpath, self.path))
                shutil.move(str(tpath), str(self.path))


        try:
            self.check()
        except PackageCheckError as e:
            log.error(_("Failed to install Package to {}: {}").format(str(self.path), str(e)))
            raise e

        log.info(_("Installed Package to {}").format(self.path))

# ┌────────────────────────────────────────┐
# │ GitPackage class                       │
# └────────────────────────────────────────┘
#class GitPackage(Package):
#    def __init__(self,
#                 path: Path,
#                 remote_url: str,
#                 remote_branch: str,
#                 remote_commit: Optional[str] = None ):
#        super().__init__(path)
#
#        self.remote_url    = remote_url   
#        self.remote_branch = remote_branch
#        self.remote_commit = remote_commit
#
#    def _check_repo_state(self):
#        log.info(_("Checking git repo state for package {}").format(str(self.path)))
#
#        repo = git.Repo(str(self.path.resolve()))
#        assert self.remote_branch == str(repo.active_branch)
#
#        if self.remote_commit:
#            assert self.remote_commit == str(repo.commit())
#
#    def check(self):
#        try:
#            self._check_folder()
#            self._check_repo_state()
#        except Exception as e:
#            log.warning(_("Failed check package {}, reinstall")
#                        .format(self.path))
#            log.debug(traceback.format_exc())
#
#            if self.path.exists():
#                self.remove()
#            self.install()
#
#    def install(self):
#        log.info(_("Install package {} from git repo").format(self.path))
#
#        # Create empty local repo
#        empty_repo = git.Repo.init(str(self.path.resolve()))
#
#        # Set remote and fetch
#        origin     = empty_repo.create_remote('origin', self.remote_url)
#        origin.fetch()
#
#        # Create local tracking branch and checkout
#        empty_repo.create_head(self.remote_branch, origin.refs[self.remote_branch])
#        empty_repo.heads[self.remote_branch].set_tracking_branch(origin.refs[self.remote_branch]) # set local branch to track remote branch
#        empty_repo.heads[self.remote_branch].checkout()

# ┌────────────────────────────────────────┐
# │ FolderPackage class                    │
# └────────────────────────────────────────┘
class FolderPackage(Package):
    def __init__( self,
                  path: Path,
                  hlist: Path = None ):
        super().__init__(path)
        self.hlist = hlist

    def _check_files(self):
        if self.hlist is not None:
            log.info(_("Checking files for {}").format(self.path))
            hlist_ref  = fs.HashList.from_file(self.hlist)
            hlist_dest = fs.HashList.from_path(self.path)

            diff = list(hlist_dest.diff(hlist_ref))
            if len(diff) > 0:
                raise PackageCheckError(self,
                                        _("Found differences in files, reinstall."),
                                        diff)

    def check(self):
        self._check_folder()
        self._check_files()

# ┌────────────────────────────────────────┐
# │ Load from config                       │
# └────────────────────────────────────────┘
def from_config(conf: Dict[str, any]):
    """
    Loads a specific package information from info given
    in config.

    :param conf: a key/pair value giving config insight. must contain the
    "type attribute"
    :return: a Package subclass (FolderPackage, ArchivePackage, GitPackage)
    with the correct settings.
    """

    package_types = { "folder" : FolderPackage,
                      #"git"    : GitPackage,
                      "archive": ArchivePackage }
    
    if not "type" in conf:
        raise KeyError(_("Excepted \"type\" key in package config."))
    
    ttype = conf["type"]
    if not ttype in package_types:
        raise KeyError( _("Uknown package type {}, excepted {}")
                         .format(ttype, ",".join(package_types.keys())) )

    del conf["type"] # Remove type entry from config

    # Construct package class with remaining parameters
    return package_types[ttype](**conf) 
