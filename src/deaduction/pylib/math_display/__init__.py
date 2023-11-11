"""
# __init__.py : <#ShortDescription> #
    
    <#optionalLongDescription>

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 10 2021 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the d∃∀duction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    d∃∀duction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

# from .utils import Descendant
from .pattern_data import metanodes
# from .pattern_init import pattern_init  !! Circular import !!
from .app_pattern_data import PatternMathDisplay
from .display_data import (MathDisplay,
                           # latex_from_node,
                           # latex_to_utf8,
                           # latex_to_lean,
                           # plurals,
                           # update_plurals,
                           # plural_types,
                           # numbers,
                           new_objects,
                           new_properties
                           )

from .html_display import html_display
from .utf8_display import utf8_display
