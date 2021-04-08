import deaduction.pylib.logger           as logger

from   deaduction.pylib.utils.filesystem import HashList
from   pprint                            import pprint
from   dictdiffer                        import diff

import deaduction.pylib.logger           as     logger

logger.configure()

hlist     = HashList.from_path("/tmp/mathlib")
hlist_ref = HashList.from_file("hashlist.gz")

pprint(list(hlist.diff(hlist_ref)))

#hlist.to_file("hashlist.gz")


#pprint(hlist.files)
#hlist = fs.hashlist_from_path("/tmp/mathlib")
#fs.hashlist_to_file(hlist, "hashlist.gz")
