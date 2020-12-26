"""
########################################
# dict.py : Utilities for dict objects #
########################################

Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : December 2020

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

def dotset( r, k, v, if_not_exists=False ):
    """
    Sets an item in a directory with a hierarchical path. Creates sub directories
    if needed

    :param r: The destination dict
    :param k: The hierarchical key, separated with dots
    :param v: The value to set
    :param if_not_exists: Set value only if key doesn't exist

    :return: True if item was set, False otherwise
    """

    # Test cases :
    # 1 : default case (no depth)
    # 2 : subdict (2 levels of depth)
    # 3 : Excepted dict value exception
    # 5 : if_not_exists don't overwrite

    if not isinstance(r,dict): raise TypeError("Excepted dict value")

    keys = list(k.split("."))
    dst  = r # Destination
    for idx in range(0,len(keys)-1):
        kp = keys[idx]
        if not kp in dst : dst[kp] = dict()
        dst = dst[kp]

    # If key not in last subdict, so the item doesn't exist yet
    klast = keys[-1]
    if (not klast in dst) or (not if_not_exists) :
        dst[klast] = v
        return True
    else : return False

def dotget( r, k ):
    """
    Returns an object in a dictionnary, given its name
    hierarchy. for example, root.child.leaf
    """
    
    try:
        keys = list(k.split("."))
        rp = r
        for idx in range(0, len(keys)-1):
            rp = rp[keys[idx]]
        return rp[keys[-1]]
    except KeyError as e : raise KeyError( "%s in %s" % (str(e), k))

def flatten( r ):
    """
    Returns a generator that gives each last level item as kall,k,v. Can be used as some kind
    of view. Recursive style. I do like StackOverflow. Oh wait, not this one...

    kall means name with levels separated by dots. Like root.child.leaf
    """
    name_stack = []
    def rr( vv ):
        for k,v in vv.items():
            name_stack.append( k )
            if isinstance( v, dict ) : yield from rr( v )
            else: yield (".".join(name_stack),k,v)
            name_stack.pop()

    yield from rr(r)
