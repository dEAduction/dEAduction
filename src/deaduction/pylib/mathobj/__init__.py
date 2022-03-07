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

from deaduction.pylib.mathobj.math_object import MathObject
from .context_math_object import                 ContextMathObject
from .pattern_math_objects import                (PatternMathObject,
                                                  mvars_assign,
                                                  mvars_assign_some,
                                                  first_unassigned_mvar)
from .proof_step import          (ProofStep,
                                  NewGoal)

from .give_name import           (get_new_hyp,
                                  give_global_name,
                                  names_for_types)

from .lean_analysis import       (lean_expr_with_type_grammar,
                                  LeanEntryVisitor)

