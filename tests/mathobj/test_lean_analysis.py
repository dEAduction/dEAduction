"""
# test_lean_analysis.py : <#ShortDescription> #
    
    <#optionalLongDescription>

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 09 2020 (creation)
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
import deaduction.pylib.mathobj.MathObject as MathObject
import deaduction.pylib.mathobj.display_math_object as display_math_object
import pytest

def test_lean_analysis:
    pass



hypo_analysis = """¿¿¿object: LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿= PROP
¿¿¿object: LOCAL_CONSTANT¿[name: Q¿/ identifier: 0._fresh.1613.3¿]¿= PROP
¿¿¿object: LOCAL_CONSTANT¿[name: R¿/ identifier: 0._fresh.1613.5¿]¿= PROP
¿¿¿property¿[pp_type: P → P¿]: LOCAL_CONSTANT¿[name: H0¿/ identifier: 0._fresh.1613.11¿]¿= PROP_IMPLIES¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿, LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿)
¿¿¿property¿[pp_type: P ∧ Q → Q ∧ P¿]: LOCAL_CONSTANT¿[name: H0¿/ identifier: 0._fresh.1613.21¿]¿= PROP_IMPLIES¿[type: PROP¿]¿(PROP_AND¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿, LOCAL_CONSTANT¿[name: Q¿/ identifier: 0._fresh.1613.3¿]¿)¿, PROP_AND¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: Q¿/ identifier: 0._fresh.1613.3¿]¿, LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿)¿)
¿¿¿property¿[pp_type: P ∨ Q ↔ Q ∨ P¿]: LOCAL_CONSTANT¿[name: H1¿/ identifier: 0._fresh.1613.33¿]¿= PROP_IFF¿[type: PROP¿]¿(PROP_OR¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿, LOCAL_CONSTANT¿[name: Q¿/ identifier: 0._fresh.1613.3¿]¿)¿, PROP_OR¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: Q¿/ identifier: 0._fresh.1613.3¿]¿, LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿)¿)
¿¿¿property¿[pp_type: ¬¬P ↔ P¿]: LOCAL_CONSTANT¿[name: H2¿/ identifier: 0._fresh.1613.41¿]¿= PROP_IFF¿[type: PROP¿]¿(PROP_NOT¿[type: PROP¿]¿(PROP_NOT¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿)¿)¿, LOCAL_CONSTANT¿[name: P¿/ identifier: 0._fresh.1613.1¿]¿)
¿¿¿property¿[pp_type: R ∧ ¬R → false¿]: LOCAL_CONSTANT¿[name: H3¿/ identifier: 0._fresh.1613.51¿]¿= PROP_NOT¿[type: PROP¿]¿(PROP_AND¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: R¿/ identifier: 0._fresh.1613.5¿]¿, PROP_NOT¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: R¿/ identifier: 0._fresh.1613.5¿]¿)¿)¿)"""

trials = hypo_analysis.split("\\n¿¿¿")