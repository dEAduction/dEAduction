from   deaduction.packager.package import ArchivePackage
from   pathlib                     import Path

from deaduction.pylib import logger

ARCHIVE_PATH     = "/home/mysterious/.deaduction/mathlib"
ARCHIVE_URL      = "https://oleanstorage.azureedge.net/mathlib/158e84ae35cbed47282545f318fb33c0ed483761.tar.xz"
ARCHIVE_CHECKSUM = "a6dcc73a42db7340dcf47c1050c1d9803a279b51"
ARCHIVE_HLIST    = "hashlist.gz"

if __name__ == "__main__":
    logger.configure()

    package = ArchivePackage(
        path             = Path(ARCHIVE_PATH),
        archive_url      = ARCHIVE_URL,
        archive_checksum = ARCHIVE_CHECKSUM,
        archive_hlist    = ARCHIVE_HLIST
    )

    package.check()
