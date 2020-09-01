from   deaduction.packager.package import ArchivePackage, GitPackage
from   pathlib                     import Path

from deaduction.pylib import logger

ARCHIVE_PATH     = "/home/mysterious/.deaduction/mathlib"
ARCHIVE_URL      = "https://oleanstorage.azureedge.net/mathlib/158e84ae35cbed47282545f318fb33c0ed483761.tar.xz"
ARCHIVE_CHECKSUM = "a6dcc73a42db7340dcf47c1050c1d9803a279b51"
ARCHIVE_HLIST    = "hashlist.gz"

GIT_PATH         = "/home/mysterious/.deaduction/dEAduction-lean"
GIT_URL          = "https://github.com/dEAduction/dEAduction-lean.git"
GIT_BRANCH       = "master"
GIT_COMMIT       = "9ca426a97c90b9ca36ddafd702e56b5f5f28e570"

if __name__ == "__main__":
    logger.configure()

    # Test ArchivePackage
    package = ArchivePackage(
        path             = Path(ARCHIVE_PATH),
        archive_url      = ARCHIVE_URL,
        archive_checksum = ARCHIVE_CHECKSUM,
        archive_hlist    = ARCHIVE_HLIST
    )

    package.check()
    
    # Test GitPackage
    pp = GitPackage( path          = GIT_PATH,
                     remote_url    = GIT_URL,
                     remote_branch = GIT_BRANCH,
                     remote_commit = GIT_COMMIT )

    pp.check()
