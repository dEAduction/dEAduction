prelude
import init.data.nat.basic init.data.string.basic

def lean.version : nat × nat × nat :=
(3, 16, 5)

def lean.githash : string :=
"101e2ca571cc503bc7ff5d06addeff037b352a96"

def lean.is_release : bool :=
1 ≠ 0

/-- Additional version description like "nightly-2018-03-11" -/
def lean.special_version_desc : string :=
""
