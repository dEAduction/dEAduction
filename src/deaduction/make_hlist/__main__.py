import deaduction.pylib.logger as logger
from deaduction.pylib.utils.filesystem import HashList

import sys

logger.configure()

hlist = HashList.from_path(sys.argv[1])
hlist.to_file(sys.argv[2])
