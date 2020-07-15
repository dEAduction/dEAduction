import test
from   pprint import pprint

pprint(test.__actions__)
test.negate("a")

test.__actions__["negate"].run("a")

