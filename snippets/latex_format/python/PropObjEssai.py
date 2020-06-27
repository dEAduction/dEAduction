"""
#######################################################
# PropObjEssai.py : tentative classes for math object #
#######################################################

    (#optionalLongDescription)

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 06 2020 (creation)
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
import dataclass as dataclass


@dataclass
class MathObjects:
    pass

@dataclass
class MathTypes(MathObject):
    list_ = []

@dataclass
class LeanType(MathTypes):
    pass


@dataclass
class Universe(MathTypes):
    Type: LeanType


@dataclass
class Set(MathTypes):
    universe: MathTypes


@dataclass
class Function(MathTypes):
    source: MathTypes
    target: MathTypes

class Sequence(Function):
    def __init__(self, set):
        self.source = Nat
        self.target = set

class SetFamily(Function):
    def __init__(self, index: MathTypes, universe: Universe):
        self.source = index
        self.target = universe

@dataclass
class PropObj:
    """
    Python representation of mathematical entities,
    both objects (sets, elements, functions, ...)
    and properties ("a belongs to A", ...)
    """
    nature: dict   # keys = ["node": str, "complement": str or nat ?, "type": MathTypes]
    args: list          # list of PO
    latex_rep: str

@dataclass
class ProofStatePO(PropObj):
    """
    Objects and Propositions of the proof state
    """
#    is_goal: bool
    lean_data: dict        # keys =["identifier", "name", "leann_pp_type"]
#    lean_name: str               # the Lean user access the object/prop
#    latex_type : str        # for Obj only. Identical to lean_name?
#    P_lean_pp_type: str     # for Prop only, mostly for debugging
    dict_ = {}              #dictionary (identifier,PropObj) of all instances

    nature_nodes_list = ["PROP_AND", "PROP_OR", "PROP_IFF", "PROP_NOT", "PROP_IMPLIES",
                   "QUANT_∀", "QUANT_∃", "PROP_∃",
                   "SET_INTER", "SET_UNION", "SET_INTER+", "SET_UNION+",
                   "PROP_INCLUDED", "PROP_BELONGS", "SET_COMPLEMENT"
                   "SET_IMAGE", "SET_INVERSE",
                   "PROP_EQUAL", "PROP_EQUAL_NOT",
                   "PROP_<", "PROP_>", "PROP_≤", "PROP_≥",
                   "MINUS", "+",
                   "APPLICATION_FUNCTION", "VAR"]
    # APPLICATION ?
    nature_leaves_list = ["PROP", "TYPE", "SET", "ELEMENT",
                           "FUNCTION", "SEQUENCE", "SET_FAMILY",
                           "TYPE_NUMBER", "NUMBER", "VAR"]  # VAR should not be used any more
