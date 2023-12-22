"""
# definition_math_object.py : subclass MathObject for definitions with
patterns #

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 08 2022 (creation)
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


from typing import Optional
import logging

from deaduction.pylib.mathobj.math_object import MathObject
from deaduction.pylib.pattern_math_obj.pattern_math_objects import (PatternMathObject,
                                                                    MetaVar)
from deaduction.pylib.coursedata import Definition
from deaduction.pylib.math_display import PatternMathDisplay


log = logging.getLogger(__name__)
global _


class DefinitionMathObject(MathObject, Definition):
    """
    This class stores a definition and its initial proof state in the form of a
    math_object. It initiates from a Definition's instance.
    self.target should be an iff or an equality
    (this is checked in self.check_proof_state() ).
    Then self.pattern has shape
    ... <=> ...
    or
    ... = ...
    """

    definition: Definition
    pattern: PatternMathObject = None
    _last_matched_math_object: Optional[MathObject] = None

    # FIXME: clear at exo change
    instances = []  # List of all instances

    def __init__(self, definition: Definition):
        """
        Init self from a definition.
        """
        self.definition = definition
        self.instances.append(self)
        self.__dict__.update(self.definition.__dict__)

        # definition_args = definition.__dict__
        # Definition.__init__(self, **definition_args)
        self.check_proof_state()

    @classmethod
    def clear_instances(cls):
        cls.instances = []

    @property
    def target(self):
        """
        Target of the initial_proof_state, if exists.
        What interests us is target.math_type, e.g. if self is initiated with
        the Definition instance corresponding to inclusion,
        then self.target.math_type is
            A subset B iff ( for all x in X, x in A implies x in B ).
        """
        if self.definition.initial_proof_state:
            return self.definition.initial_proof_state.goals[0].target

    @classmethod
    def clear_instances(cls):
        cls.instances = []

    @classmethod
    def get_constants(cls):
        """
        Add all CONSTANTS in self to the all_constants list.
        """

        # FIXME: croiser avec PatternMathDisplay.all_constants_names
        all_constants = dict()
        for defi in cls.instances:
            # hierarchy_of_sections = (_(title).capitalize() for title in
            #                          defi.definition.ugly_hierarchy())
            outline = defi.definition.course.outline
            hierarchy_of_sections = defi.definition.pretty_hierarchy(outline)
            section = ' / '.join(hierarchy_of_sections)
            if section not in all_constants:
                all_constants[section] = []
            csts = all_constants[section]
            if defi.lhs_pattern:
                for cst in defi.lhs_pattern.constants_in_self():
                    if (cst.name in PatternMathDisplay.all_constants_names()
                            and cst not in csts):
                        csts.append(cst)

        return all_constants

    def check_proof_state(self) -> bool:
        """
        Init the MathObject parameters with initial_proof_state if not None.
        Return True if successful.
        This is useful because exercise may start before ips is set.
        """
        # match_pattern = self.info.get("MatchPattern")
        # if match_pattern:
        #     print(match_pattern)

        if not self.definition.initial_proof_state:
            return False
        elif self.pattern:
            return True

        if not (self.target.is_iff() or self.target.is_equality()):
            # Ensure def is an iff or an equality, otherwise ignore it
            log.warning(f"Definition {self.definition.pretty_name} is an iff "
                        f"nor an equality")
            return False
        self.__dict__.update(self.target.math_type.__dict__)
        self.pattern = PatternMathObject.from_math_object(self.target.math_type)
        return True

    @property
    def lhs_pattern(self) -> Optional[PatternMathObject]:
        if self.check_proof_state():
            return self.pattern.children[0]

    @property
    def rhs_pattern(self) -> Optional[PatternMathObject]:
        if self.check_proof_state():
            return self.pattern.children[1]

    @property
    def metavars(self) -> [MetaVar]:
        return self.pattern.metavars if self.check_proof_state() else []

    def clear_matching(self):
        for mvar in self.metavars:
            mvar.clear_assignment()

    def match(self, math_object) -> bool:
        """
        True iff math_object match self.
        """
        # TODO: improve
        # self.clear_matching()
        if not self.check_proof_state():
            return False

        if self.lhs_pattern.match(math_object):
            self._last_matched_math_object = math_object
            return True
        else:
            self._last_matched_math_object = None
            return False

    def do_matching(self, math_object) -> Optional[MathObject]:
        """
        Return MathObject obtained from applying self's definition to
        math_object (if it applies).
        """
        if self._last_matched_math_object is not math_object:
            self.match(math_object)
        if self._last_matched_math_object:
            rhs_math_object = self.rhs_pattern.math_object_from_matching()
            return rhs_math_object

    @classmethod
    def set_definitions(cls, definitions: [Definition]):
        """
        Turn definitions into DefinitionMathObjects, in MathObject's
        definitions class attribute.
        """
        MathObject.definitions = [cls(definition) for definition in definitions]
