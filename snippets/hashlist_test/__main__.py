import deaduction.pylib.logger           as logger
import deaduction.pylib.utils.filesystem as fs

hlist = fs.hashlist_from_path("/tmp/mathlib")
fs.hashlist_to_file(hlist, "hashlist.gz")
