"""
#############################################################
# variables_baptism.py : attribute a name to new variables  #
#############################################################
    
When a new mathematical object is instanciated, this object has to be given a name.
The function baptism provides this functionality.
The function init_name_scheme determines the name_scheme for variables of a given math_type.

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

import PropObj as PO


def baptism(math_type: PO.PropObj, list_of_names=None) -> str:
    """
    Provide a name for a new mathematical object
    NB : math_type should be the "real mathematical type", e.g.
    if the variable has type X but it is immediately defined as a member of A : set X,
    then math_type should be A instead of X, even if in the PO object corresponding to the variable,
    math_type = X.
    math_type.name_scheme is a list of potential names for future variables fo type math_type

    :param math_type: a mathematical type (e.g. Type, X, A, set X, Function(X,Y), ...)
    :param list_of_names: the list of all names of objects in the current context
    :return: a name for the new variable that does not belong to list_of_names
    """
    if list_of_names is None:
        list_of_names = [prop_obj.lean_data["name"] for prop_obj in PO.ProofStatePO.context_dict.values()]
    good_name = None
    if not hasattr(math_type, name_scheme):
        init_name_scheme(math_type, list_of_names)
    while good_name is None:
        for name in math_type.name_scheme:
            if name not in list_of_names:
                good_name = name
            math_type.name_scheme.remove(name)
        init_name_scheme(math_type, list_of_names)
    return good_name


def init_name_scheme(math_type: PO.PropObj, list_of_names: list, name_prescheme=None):
    """
    determine a list of variable names and attribute it to math_type.name_scheme
    the main sheme is the following:
    first determine the base letter, and second add a decoration (prime or index or nothing)
    - for elements (ie the type of math_type is "Type"), if there is a hint_set which is an upper case letter,
    the base letter is the corresponding lower case letter

    if there is no variable of type math_type, then choose the name according to

    :param math_type: a mathematical type
    :param list_of_names: the list of all current variables
    :param name_prescheme: a hint for naming new variables
    name_prescheme, if not None, is a list of strings of one of the following form:
        - a letter of the latin alphabet, in lower or upper case ;
        - a letter followed by "-", meaning all letters starting from the given one in the alphabetic order
        - an interval of letters, e.g. "[a-e]" or "[A-E]"
        - a letter followed by a prime symbol ('), e.g. "x'" meaning "x", "x'", "x''"
        - a letter followed by an underscore and a number or an interval of numbers, e.g. "x_1" or "x_[0-9]"
        - a Greek letter
    :return: None
    """
    if name_prescheme is not None:
        name_scheme = []  # TODO
        return name_scheme

    base_letter = None
    names = math_type.list_of_terms
    if names:
        name: str = names[-1]  # last attributed name
        l = name[0]
        if l.isalpha():
            base_letter = l


    if math_type.node == "SET":
        letter_hint = math_type.node.lean_data["name"]
        if letter_hint[0].isupper():
            base_letter = letter_hint[0].lower()
        else:
            math_type = math_type.children[0]
    if math_type.math_type == "Type":
        letter_hint = math_type.node.lean_data["name"]
        if letter_hint[0].isupper():
            base_letter = letter_hint[0].lower()
    elif math_type.node == "FUNCTION":
        base_letter = ["f", "g", "h", "\Phi", "\Psi"]
    elif math_type.node == "TYPE_NUMBER[name:ℕ]":
        base_letters = []
    elif math_type.node == "TYPE_NUMBER[name:ℝ]":
        pass
    elif math_type.node == "SEQUENCE":
        base_letter = ["u"]
    elif math_type.node == "SET_FAMILY":
        pass
