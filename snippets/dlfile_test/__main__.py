import deaduction.pylib.utils.filesystem as fs
import deaduction.pylib.logger           as logger

import tarfile
from pathlib import Path

import logging
from tempfile import TemporaryFile

URL        = "https://oleanstorage.azureedge.net/mathlib/158e84ae35cbed47282545f318fb33c0ed483761.tar.xz"
CHECKSUM   = "a6dcc73a42db7340dcf47c1050c1d9803a279b51"

DESTDIR    = Path("/tmp/mathlib")

log = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.configure()

    fs.check_dir(DESTDIR)

    with TemporaryFile() as fhandle:

        log.info("Download file")
        checksum = fs.download(URL, fhandle)

        print(checksum, CHECKSUM)
        assert checksum == CHECKSUM

        fhandle.seek(0)

        log.info(f"Extract file to {str(DESTDIR)}")
        with tarfile.open(fileobj=fhandle) as tf:
            tf.extractall(path=str(DESTDIR))
