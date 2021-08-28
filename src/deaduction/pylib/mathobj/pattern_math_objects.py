"""
# implicit_definitions.py : <#ShortDescription> #
    
    <#optionalLongDescription>

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 08 2021 (creation)
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

import logging
from typing import Optional
if __name__ == "__main__":
    import deaduction.pylib.config.i18n

from deaduction.pylib.mathobj       import ( MathObject,
                                             NO_MATH_TYPE,
                                             HAVE_BOUND_VARS )
# from .MathObject import mark_bound_vars, unmark_bound_vars

log = logging.getLogger(__name__)

# List of default implicit definitions
# TODO: mark them in the metadata of the Lean file
# TODO: test double-inclusion as a def
IMPLICIT_DEFINITIONS = ['inclusion',
                        'intersection_deux_ensembles',
                        'union_deux_ensembles',
                        'intersection_quelconque_ensembles',
                        'union_quelconque_ensembles',
                        'produit_de_parties',
                        'image_directe',
                        'egalite_fonctions',
                        'Identite',
                        'injectivite'
                        ]


class PatternMathObject(MathObject):
    """
    A class for MathObject that may contains metavariables. Metavraiables
    are represented by PatternMathObject whose node is 'METAVAR".
    e.g. The PatternMathObject representing the definition of injectivity
    looks like:
        metavar_28 is injective ⇔ ( ∀x ∈ metavar_26, ∀x' ∈ metavar_26,
                                  (metavar_28(x) = metavar_28(x') ⇒ x = x') )
    Note that here metavar_28 would have type '(metavar_26) → (metavar_27)'
    and metavar_26 has type 'ensemble'.

    The match() method tests if a given MathObject match a PatternMathObject,
    e.g. if left is the PatternMathObject 'metavar_28 is injective', and
         math_object = 'g∘f is injective'
    then
        left.match(math_object)
    will be True. Note the the math_types should also match.

    After a successful matching test, the matching values of the metavars are
    stored in the metavar_objects class attribute as a list of MathObject
    instances. Then the apply_matching() method will substitute metavars in
    some MathObject. For instance after the previous example, if right is the
    PatternMathObject
        (∀x ∈ metavar_26, ∀x' ∈ metavar_26,
        (metavar_28(x) = metavar_28(x') ⇒ x = x'))
    then right.apply_matching() will produce the MathObject
        ∀x ∈ X, ∀x' ∈ X, (g∘f(x) = g∘f(x') ⇒ x = x')
    """
    metavar_nb = 0
    metavars_csts           = []  # List of all metavars in all patterns
    loc_csts_for_metavars   = []  # and corresponding local constants
    __tmp_metavars_csts         = None
    __tmp_loc_csts_for_metavars = None
    metavars        = None
    metavar_objects = None  # Objects matching metavars (see self.match)

    def __init__(self, node, info, children, bound_vars, math_type):
        super().__init__(node=node,
                         info=info,
                         children=children,
                         bound_vars=bound_vars,
                         math_type=math_type)

    @property
    def nb(self):
        if self.node == 'METAVAR':
            return self.info['nb']
        else:
            return None

    @classmethod
    def new_metavar(cls, math_type):
        cls.metavar_nb += 1
        return cls(node='METAVAR',
                   info={'nb': cls.metavar_nb},
                   children=[],
                   bound_vars=[],
                   math_type=math_type)

    @classmethod
    def from_math_object(cls, math_object: MathObject):
        cls.__tmp_loc_csts_for_metavars = []
        cls.__tmp_metavars_csts         = []
        return cls.__from_math_object(math_object)

    @classmethod
    def __from_math_object(cls, math_object: MathObject):
        """
        Produce a PatterMathObject from math_object by replacing all local
        constants which are not bound variables by fresh metavars.
        Of course all occurrences of a given local constant must be replaced
        by the same metavar.
        This is obviously a recursive method. The lists loc_csts, metavars
        allow to keep track of the correspondence between the local
        constants that have been previously replaced and the metavars.

        :param loc_csts: list of local constants
        :param metavars: corresponding list of metavars
        :return:         new PatternMathObject
        """
        # log.debug(f"Patterning mo {math_object.to_display()}")
        metavars = cls.__tmp_metavars_csts
        loc_csts = cls.__tmp_loc_csts_for_metavars

        if math_object in loc_csts:
            metavar = metavars[loc_csts.index(math_object)]
            # log.debug(f"   Mo is metavar n°{metavar.info['nb']}")
            return metavar

        elif math_object.node == 'LOCAL_CONSTANT' and \
                not math_object.is_bound_var():
            # Turn math_type into a PatternMathObject,
            # then create a new metavar.
            if math_object.math_type is NO_MATH_TYPE:
                math_type = NO_MATH_TYPE_PATTERN
            else:
                math_type   = cls.__from_math_object(math_object.math_type)
            new_metavar = cls.new_metavar(math_type)
            metavars.append(new_metavar)
            cls.metavars_csts.append(new_metavar)
            loc_csts.append(math_object)
            cls.loc_csts_for_metavars.append(math_object)
            # metavar_list[math_object] = new_metavar
            # log.debug(f"   Creating metavar n°{new_metavar.info['nb']}")
            return new_metavar

        else:
            node = math_object.node

            info = math_object.info  # Useless??
            # log.debug("   ->Children:")
            children = []
            for child in math_object.children:
                new_child = cls.__from_math_object(child)
                children.append(new_child)
            if math_object.math_type is NO_MATH_TYPE:
                math_type = NO_MATH_TYPE_PATTERN
            else:
                # log.debug("   ->Math type:")
                math_type   = cls.__from_math_object(math_object.math_type)

            pattern_math_object = cls(node=node,
                                      info=info,
                                      children=children,
                                      bound_vars=math_object.bound_vars,
                                      math_type=math_type)
            # log.debug(f"   ->pmo: {pmo.to_display()}")
            return pattern_math_object

    def __eq__(self, other):
        """
        Redefine __eq__, otherwise all METAVARS are equals!?
        """
        return self is other

    def is_metavar(self):
        return self.node == "METAVAR"

    def match(self, math_object: MathObject) -> bool:
        """
        Test if math_object match self. This is a recursive test.
        The list PatternMathObject.metavars contains the metavars that have
        already been matched against a math_object, which is stored with the
        same index in the list PatternMathObject.metavar_objects.
        e.g. 'g∘f is injective' matches 'metavar_28 is injective'
        (note that math_types of metavars should also match).
        """

        PatternMathObject.metavars = []
        PatternMathObject.metavar_objects = []
        match = self.recursive_match(math_object)
        log.debug(f"Matching...")
        list_ = [(PatternMathObject.metavars[idx].to_display(),
                  PatternMathObject.metavar_objects[idx].to_display())
                 for idx in range(len(PatternMathObject.metavars))]
        log.debug(f"    Metavars, objects: {list_}")
        return match

    def recursive_match(self, math_object: MathObject) -> bool:
        """
        Test if math_object match self. This is a recursive test.
        The list metavars contains the metavars that have already been
        matched against a math_object, and this object is stored with the same
        index in the metavar_objects list.
        """

        metavars = PatternMathObject.metavars
        metavar_objects = PatternMathObject.metavar_objects
        match = True    # Self and math_object are presumed to match
        marked = False  # Will be True if bound variables should be unmarked

        node = self.node
        # Case of NO_MATH_TYPE (avoid infinite recursion!)
        if self is NO_MATH_TYPE_PATTERN:
            return True

        # METAVAR
        elif node == 'METAVAR':
            # If self has already been identified, math_object matches self
            #   iff it is equal to the corresponding item in metavar_objects
            # If not, then self matches with math_object providing their
            #   math_types match. In this case, identify metavar.
            if self in metavars:
                corresponding_object = self.math_object_from_metavar()
                match = (math_object == corresponding_object)
            else:
                mvar_type = self.math_type
                math_type = math_object.math_type
                match = mvar_type.recursive_match(math_type)
                if match:
                    metavars.append(self)
                    metavar_objects.append(math_object)
                match = True
            return match
        # Node
        elif node != math_object.node:
            # log.debug(f"distinct nodes {self.node, math_object.node}")
            return False

        # Mark bound vars in quantified expressions to distinguish them
        elif node in HAVE_BOUND_VARS:
            # Here self and math_object are assumed to be a quantified
            # proposition and children[1] is the bound variable.
            # We mark the bound variables in self and math_object with same
            # number so that we know that, say, 'x' in self and 'y' in
            # math_object are linked and should represent the same variable
            # everywhere
            bound_var_1 = self.children[1]
            bound_var_2 = math_object.children[1]
            self.mark_bound_vars(bound_var_1, bound_var_2)
            marked = True

        # Names
        if 'name' in self.info.keys():
            # For bound variables, do not use names, use numbers
            if self.is_bound_var():
                if not math_object.is_bound_var():
                    match = False
                # Here both are bound variables
                elif 'bound_var_number' not in self.info:
                    if 'bound_var_number' in math_object.info:
                        # Already appeared in math_object but not in self
                        match = False
                    else:
                        # Here both variable are unmarked. This means
                        # we are comparing two subexpressions with respect
                        # to which the variables are not local:
                        # names have a meaning
                        match = (self.info['name'] == math_object.info['name'])
                # From now on self.info['bound_var_number'] exists
                elif 'bound_var_number' not in math_object.info:
                    match = False
                # From now on both variables have a number
                elif (self.info['bound_var_number'] !=
                      math_object.info['bound_var_number']):
                    match = False
            else:  # Self is not bound var
                if math_object.is_bound_var():
                    match = False
                elif self.info['name'] != math_object.info['name']:
                    # None is a bound var
                    match = False
                    # log.debug(f"distinct names "
                    #        f"{self.info['name'], math_object.info['name']}")

        # Recursively test for math_types
        elif not self.math_type.recursive_match(math_object.math_type):
            log.debug(f"distinct types {self.math_type}")
            log.debug(f"math_object type     {math_object.math_type}")
            match = False

        # Recursively test matching for children
        elif len(self.children) != len(math_object.children):
            match = False
        else:
            for child0, child1 in zip(self.children, math_object.children):
                if not child0.recursive_match(child1):
                    match = False

        # Unmark bound_vars, in prevision of future tests
        if marked:
            self.unmark_bound_vars(bound_var_1, bound_var_2)

        return match

    def math_object_from_metavar(self):
        if self not in PatternMathObject.metavars:
            return NO_MATH_TYPE
        else:
            index = PatternMathObject.metavars.index(self)
            math_object = PatternMathObject.metavar_objects[index]
            return math_object

    def apply_matching(self):
        """
        Substitute metavars in self according to PatternMathObject.metavars and
        PatternMathObject.metavar_objects. Returns a MathObject if all
        metavars of self are in PatternMathObject.metavars,
        else a MathObject with some metavars.
        """

        if self.is_metavar():
            return self.math_object_from_metavar()
        elif self is NO_MATH_TYPE_PATTERN:
            return NO_MATH_TYPE

        found_math_type = self.math_type.apply_matching()
        found_children = []
        for pattern_child in self.children:
            child = pattern_child.apply_matching()
            found_children.append(child)

        math_object = MathObject(node=self.node,
                                 info=self.info,
                                 children=found_children,
                                 bound_vars=self.bound_vars,
                                 math_type=found_math_type)
        return math_object

    @classmethod
    def set_definitions_for_implicit_use(cls, definitions):
        """
        Set definitions for implicit use.
        """
        MathObject.implicit_definitions = []
        MathObject.definition_patterns = []
        for definition in definitions:
            log.debug(f"Adding implicit use of "
                      f"{definition.pretty_name}")
            iff = definition.extract_iff()
            if iff:
                pattern = cls.from_math_object(iff)
                log.debug(f"   Pattern: {pattern.to_display()}")
                MathObject.implicit_definitions.append(definition)
                MathObject.definition_patterns.append(pattern)
                definition.implicit_use_activated = True


NO_MATH_TYPE_PATTERN = PatternMathObject(node="not provided",
                                         info={},
                                         children=[],
                                         bound_vars=[],
                                         math_type=None)


#########
# TESTS #
#########

if __name__ == '__main__':
    from deaduction.pylib.mathobj.lean_analysis import (
                                            lean_expr_with_type_grammar,
                                            LeanEntryVisitor)
    import deaduction.pylib.config.i18n
    import logging
    from deaduction.pylib import logger
    logger.configure(domains='__main__', display_level='debug')

    targets_analysis = []
    targets_analysis.append("""¿¿¿property¿[pp_type: x ∈ A ∩ B ↔ x ∈ A ∧ x ∈ B¿]: METAVAR¿[name: _mlocal._fresh.231.31595¿]¿= PROP_IFF¿[type: PROP¿]¿(PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.230.21962¿]¿, SET_INTER¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.230.21950¿]¿)¿]¿(LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.230.21954¿]¿, LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.230.21959¿]¿)¿)¿, PROP_AND¿[type: PROP¿]¿(PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.230.21962¿]¿, LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.230.21954¿]¿)¿, PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.230.21962¿]¿, LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.230.21959¿]¿)¿)¿)""")
    targets_analysis.append("""¿¿¿property¿[pp_type: x ∈ A ∪ B ↔ x ∈ A ∨ x ∈ B¿]: METAVAR¿[name: _mlocal._fresh.326.17524¿]¿= PROP_IFF¿[type: PROP¿]¿(PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.325.14324¿]¿, SET_UNION¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.325.14312¿]¿)¿]¿(LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.325.14316¿]¿, LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.325.14321¿]¿)¿)¿, PROP_OR¿[type: PROP¿]¿(PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.325.14324¿]¿, LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.325.14316¿]¿)¿, PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.325.14324¿]¿, LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.325.14321¿]¿)¿)¿)""")
    targets_analysis.append("""¿¿¿property¿[pp_type: injective f ↔ ∀ (x y : X), f x = f y → x = y¿]: METAVAR¿[name: _mlocal._fresh.307.5511¿]¿= PROP_IFF¿[type: PROP¿]¿(APPLICATION¿[type: PROP¿]¿(APPLICATION¿[type: FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.307.5242¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.307.5244¿]¿)¿, PROP¿)¿]¿(APPLICATION¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.307.5869¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.307.5242¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.307.5869¿]¿)¿, PROP¿)¿)¿]¿(CONSTANT¿[name: injective¿]¿[type: QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.307.5896¿]¿, QUANT_∀¿(TYPE¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.307.5908¿]¿, FUNCTION¿(FUNCTION¿(LOCAL_CONSTANT¿[name: X¿/ identifier: _fresh.307.5896¿]¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: _fresh.307.5908¿]¿)¿, PROP¿)¿)¿)¿]¿, LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.307.5242¿]¿)¿, LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.307.5244¿]¿)¿, LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.307.5247¿]¿)¿, QUANT_∀¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.307.5242¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.307.5927¿]¿, QUANT_∀¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.307.5242¿]¿, LOCAL_CONSTANT¿[name: y¿/ identifier: _fresh.307.5937¿]¿, PROP_IMPLIES¿[type: PROP¿]¿(PROP_EQUAL¿[type: PROP¿]¿(APPLICATION¿[type: LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.307.5244¿]¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.307.5247¿]¿, LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.307.5927¿]¿)¿, APPLICATION¿[type: LOCAL_CONSTANT¿[name: Y¿/ identifier: 0._fresh.307.5244¿]¿]¿(LOCAL_CONSTANT¿[name: f¿/ identifier: 0._fresh.307.5247¿]¿, LOCAL_CONSTANT¿[name: y¿/ identifier: _fresh.307.5937¿]¿)¿)¿, PROP_EQUAL¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: _fresh.307.5927¿]¿, LOCAL_CONSTANT¿[name: y¿/ identifier: _fresh.307.5937¿]¿)¿)¿)¿)¿)""")
    hypo = """¿¿¿property¿[pp_type: x ∈ A ∩ (B ∪ C)¿]: LOCAL_CONSTANT¿[name: H¿/ identifier: 0._fresh.340.35755¿]¿= PROP_BELONGS¿[type: PROP¿]¿(LOCAL_CONSTANT¿[name: x¿/ identifier: 0._fresh.340.35743¿]¿, SET_INTER¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.338.29051¿]¿)¿]¿(LOCAL_CONSTANT¿[name: A¿/ identifier: 0._fresh.338.29052¿]¿, SET_UNION¿[type: SET¿(LOCAL_CONSTANT¿[name: X¿/ identifier: 0._fresh.338.29051¿]¿)¿]¿(LOCAL_CONSTANT¿[name: B¿/ identifier: 0._fresh.338.29054¿]¿, LOCAL_CONSTANT¿[name: C¿/ identifier: 0._fresh.338.29056¿]¿)¿)¿)"""

    # Test is_and
    nb = 0
    tree = lean_expr_with_type_grammar.parse(targets_analysis[nb])
    mo = LeanEntryVisitor().visit(tree)
    mt = mo.math_type

    pattern = PatternMathObject.from_math_object(mt)
    print("Pattern:")
    print("    ", pattern.to_display())
    # print("Pattern matches left?")
    # print(pattern.match(left))


    MathObject.definition_patterns.append(pattern)
    tree = lean_expr_with_type_grammar.parse(hypo)
    mo = LeanEntryVisitor().visit(tree)
    mt = mo.math_type
    print(f"{mt.to_display()} matches {pattern.to_display()} ?")
    print(pattern.children[0].match(mt))
    print(pattern.children[1].apply_matching().to_display())
