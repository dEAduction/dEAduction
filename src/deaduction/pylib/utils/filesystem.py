"""
#########################################
# filesystem.py : File system utilities #
#########################################

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

from pathlib import Path
from io import BufferedWriter
import logging
from gettext import gettext as _
from typing import Callable
import requests
import hashlib
import gzip

from typing import List, Tuple

log = logging.getLogger(__name__)

############################################
# Some configuration variables
############################################
CHUNK_SIZE = 4096


############################################
# Hashing
############################################
def file_hash(fp: Path):
    hh = hashlib.sha1()
    hh.update(fp.read_bytes())

    return hh.hexdigest()


############################################
# Checking utilities
############################################
def check_dir(path: Path):
    """
    Checks that the directory pointed by path exists.
    Creates the folder if not existing.
    """
    log.info(_("Checking path: {}").format(str(path)))

    if path.is_file():
        raise RuntimeError(_("Path {} is a file").format(str(path)))

    elif not path.is_dir():
        log.warning(
            _("Directory {} doesn't exists, creating").format(str(path))
        )
        path.mkdir()


def hashlist_from_path(path: Path):
    """
    Computes hash list for a given path into output
    gzipped file
    """
    path   = Path(path).resolve()
    r      = []

    for fp in path.rglob("*"):
        if fp.is_file():
            hh = file_hash(fp)

            r.append((fp, hh,))

    return r


def hashlist_to_file(hlist: List[Tuple[Path, str]], path: Path):
    path = Path(path).resolve()

    with gzip.open(str(path), "wb") as fhandle:
        for pp, hh in hlist:
            line = f"{str(pp)} {str(hh)}\n".encode("utf8")
            fhandle.write(line)


def hashlist_from_file(hh_file: Path):
    """
    Loads an hashlist from the given gzipped file
    """
    hh_file = Path(hh_file).resolve()

    buff    = ""  # Line buffer
    line    = ""

    r       = []

    with gzip.open(str(hh_file), "rb") as fhandle:
        eof = False
        while not eof:
            chunk = fhandle.read(CHUNK_SIZE)
            buff += chunk.decode("utf8")

            eof   = len(chunk) < CHUNK_SIZE

            while buff.find("\n") >= 0:
                idx   = buff.find("\n")
                buff  = buff[(idx + 1):]  # idx + 1 = discard \n

                line  = buff[:idx]
                info  = line.split(" ")

                path  = Path(info[0])
                hash_ = info[1]

                r.append(path, hash_)

    return r


############################################
# Download utilities
############################################
def download(url: str, fhandle: BufferedWriter, on_progress: Callable = None):
    """
    Download a file to a specific target. Inspired from
    Patrick Massot's code in leanproject.

    :param url: HTTP(s) url to download file from (GET request)
    :param path: File path on local filesystem
    :param on_progress: callback(idx,count, progress)
                        to monitor download progress.
    :return: the sha1 checksum of the downloaded file
    """

    # TODO(florian): better error handling ?
    # -> ConnectionError raised by requests.get
    # -> HTTPError raised by raise_for_status

    sha1 = hashlib.sha1()

    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise HTTPError if any

    tot_len = response.headers.get("content-length", 0)

    if not tot_len:
        fhandle.write(response.content)
        sha1.update(response.content)
    else:
        dl_size  = 0
        tot_len  = int(tot_len)

        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            dl_size += len(chunk)
            fhandle.write(chunk)
            sha1.update(chunk)

            progress = (100 * (dl_size / tot_len))
            log.info(_("Progress : {:03d}%").format(int(progress)))

            if on_progress is not None:
                on_progress(dl_size, tot_len, progress)

    return sha1.hexdigest()


def download_to_file(url: str, dest: Path, on_progress: Callable = None):
    dest = Path(dest).resolve()

    log.info(_("Download from {} to {}").format(url, str(dest)))

    with open(str(dest), "wb") as fhandle:
        return download(url, fhandle, on_progress)
