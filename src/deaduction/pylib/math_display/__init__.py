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

from .display_data import (latex_from_node,
                           latex_to_utf8,
                           latex_to_lean,
                           plurals,
                           plural_types,
                           numbers,
                           # dic_of_first_nodes_text,
                           # couples_of_nodes_to_text,
                           new_objects,
                           new_properties
                           )
# from .display_math import (recursive_display,
#                            raw_latex_shape_from_couple_of_nodes,
#                            raw_latex_shape_from_specific_nodes,
#                            shallow_latex_to_text)
from .html_display import html_display
from .utf8_display import utf8_display
# from .display import abstract_string_to_string

# from .new_display import to_display, math_type_to_display
# from .pattern_data import pattern_latex_pairs
# from .utils import structured_display_to_string
