"""
# __init__.py : #ShortDescription #
    
    (#optionalLongDescription)

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 07 2020 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

This file is part of dEAduction.

    dEAduction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    dEAduction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

from .MathObject import          (MathObject,
                                  NO_MATH_TYPE,
                                  HAVE_BOUND_VARS)
from .context_math_object import  ContextMathObject
from .pattern_math_objects import PatternMathObject
from .proof_state import         (Goal,
                                  ProofState)
from .proof_step import          (Proof,
                                  ProofStep,
                                  NewGoal)

from .give_name import           (get_new_hyp,
                                  give_global_name,
                                  give_local_name)

from .lean_analysis import       (lean_expr_with_type_grammar,
                                  LeanEntryVisitor)

from .display_math import         Shape, latex_to_utf8, recursive_display
# from .html_display import         html_display

