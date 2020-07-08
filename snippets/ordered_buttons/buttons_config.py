"""
##########################################
# buttons_config.py : Buttons definition #
##########################################

Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : July 2020

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

from collections       import OrderedDict
from PySide2.QtWidgets import QPushButton
from typing            import List

from functools         import partial

############################################
# Solution 1
############################################

# Each value is a constructor function to construct the wanted object. Can use
# functools.partial.
LOGIC_BUTTONS = OrderedDict({
    "NO"               : partial(QPushButton, text="NO"),
    "AND"              : partial(QPushButton, text="OR"),
    "implies"          : partial(QPushButton, text="→" ),
    "equivalence"      : partial(QPushButton, text="↔" ),
    "forall"           : partial(QPushButton, text="∀" ),
    "exists"           : partial(QPushButton, text="∃" )
})

PROOF_BUTTONS = OrderedDict({
    "p_contraposition" : partial(QPushButton, text="Proof by contraposition"),
    "p_absurd"         : partial(QPushButton, text="Proof by absurd"        ),
    "p_induction"      : partial(QPushButton, text="Proof by induction"     )
})

def build_from_config(keys:List[str], config: OrderedDict, **kwargs):
    """
    Generator giving the buttons to construct in ordered from the given list
    of keys.

    :param keys: The list of keys we want to instanciate
    :param config: Ordered dict giving the config to build a widget from the
                   given key

    :return: A generator giving each button to construct
    """

    for k,construct in filter( lambda it: it[0] in keys, config.items() ):
        yield construct(**kwargs)
