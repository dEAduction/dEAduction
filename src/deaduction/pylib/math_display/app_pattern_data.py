"""
##########################################################
# app_pattern_data.py : patterns to display APPLICATIONs #
##########################################################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 11 2022 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2022 the d∃∀duction team

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

from .display_parser import display_grammar, DisplayPatternVisitor
from deaduction.pylib.math_display.display_data import (display_name,
                                                        local_constant_shape)

log = logging.getLogger(__name__)

global _

# Here int stands for metavars ('?1' in pattern --> 1 in display),
# to display children use tuples, e.g. '(1, )' means second child.
latex_from_app_pattern = {
    # TODO: test Id, Id(x)
    "APP(CONSTANT/name=Identite, ?1, ?2: ?1)": ("Id", r"\parentheses", 2),

    # u_n:
    "APP(LOCAL_CONSTANT: !SEQUENCE(?2, ?3)(...), ?1: ?2)":
    # ('', (0, local_constant_shape), ['_', (1, )], ''),
        ((0, local_constant_shape), ['_', (1,)]),
    # "APP(LOCAL_CONSTANT: !SEQUENCE(...)(...), ?1)":
    #     ('(0, ).name', ['_', (1,)]),
    "APP(LOCAL_CONSTANT: !SEQUENCE(...)(...), ?1)":
        # ('', (0, local_constant_shape), ['_', (1,)], ''),
        ((0, local_constant_shape), ['_', (1,)]),
    # APP(E, i) --> E_i
    #   Here E is the name of the local constant, which is self.children[0]
    "APP(LOCAL_CONSTANT: !SET_FAMILY(?2, ?3)(...), ?1: ?2)":
        # ('', (0, local_constant_shape), ['_', (1, )], ''),
        ((0, local_constant_shape), ['_', (1,)]),
    "APP(CONSTANT/name=limit_function, LAMBDA(?2, ?3, ?4), ?0, ?1)":
        (r'\no_text', "lim", ['_', (-3, 1), r'\to', (-2,)], ' ', (-3, 2),
         " = ", (-1,)),
    # "APP(CONSTANT/name=metric_space, ?0)":
    #     (-1, r'\text_is', _('a metric space'))
}

# The following is used to update latex_from_app_pattern
# Negative value = from end of children list
latex_from_constant_name = {
    "Identite": ("Id",),
    "identite": ("Id",),
    "interval": (r"\[", -2, ",", -1, r"\]"),
    "inv": ([r'\parentheses', (-1, )], [r'^', '-1']),
    "image": (-1, " = ", -3, "(", -2, ")"),
    "classe_equivalence": (r"\[", (-1, ), r"\]", ['_', (1, )]),
    "disjoint": (-2, " " + _("and") + " ", -1, " " + _("are disjoint")),
    "powerset": (r'\set_of_subsets', [r"\parentheses", (-1, )]),
    "RealSubGroup": (r"\real", ),
    "IntegerSubGroup": (r"\integer", ),
    "connexe": (-2, r'\text_is', " " + _("connected")),
    "connexePartie": (-1, r'\text_is', " " + _("connected")),
}

generic_app_dict = {
    # The following works only for some constant, do not use:
    # "NOT(APP(CST?,...))": ((0, -1), r'\text_is_not', (0, 0)),
    # Generic app for constants
    # CST? = CONSTANT with any name
    # FIXME: type PROP() below is OK? If not, move AFTER APP(?0: FUNCTION...
    "APP: PROP()(CST?, ...)": ('', (-1,), [r'\text_is', (0,)], ''),
    # f(x):
    "APP(?0: !FUNCTION(?1, ?2), ?3: ?1)": ((0,), r"\parentheses", (1,)),
    # Replace x ↦ f(x) by f:
    "LAMBDA(?0, ?1, APP(?3, ?1))": ((2, 0),)
}


# def additional_data_from_pattern(patterns: [str]) -> dict:
#     dic = dict()
#     for pattern in patterns:
#         try:
#             tree = display_grammar.parse(pattern)
#             more_entry = DisplayPatternVisitor().visit(tree)
#             dic.update(more_entry)
#         except ParseError:
#             pass
#     # TODO


def app_pattern_from_constants(additional_data=None):
    """
    Construct APPLICATION patterns from constant dictionary, and also their
    negations when appropriate.
    additional_data may come from the metadata in the Lean file, with field
    name = "display". Note that lists are already turned into tuples by
    parser_course.
    """
    latex_from_app_constant_patterns = {}
    if additional_data:
        # Obsolete:
        # tree = display_grammar.parse(additional_data)
        # additional_dic = DisplayPatternVisitor().visit(tree)
        # Done in parser_course:
        # Change lists to tuples
        # additional_dic = {key: tuple(value) for key, value in
        #                   additional_data.items()}
        latex_from_constant_name.update(additional_data)
        log.info("Adding display data from metadata of the lean file:")
        log.info(additional_data)
    for key, value in latex_from_constant_name.items():
        # Modify key:
        # if key in ('divise', 'pair'):
        #     pass
        new_key = f'APP(CONSTANT/name={key}, ...)'
        # Change int into tuples in value:
        new_value = tuple((item, ) if isinstance(item, int) else item
                          for item in value)
        if r'\text_is' in new_value:
            new_not_key = f"NOT(APP(CONSTANT/name={key},...))"
            new_not_value = tuple(r'\text_is_not' if item == r'\text_is' else
                                  (0, item) if isinstance(item, int) else
                                  (0, ) + item if isinstance(item, tuple)
                                  else item for item in new_value)
            latex_from_app_constant_patterns[new_not_key] = new_not_value
        latex_from_app_constant_patterns[new_key] = new_value
    latex_from_app_pattern.update(latex_from_app_constant_patterns)

    # latex_from_app_pattern.update(generic_app_dict)


class PatternMathDisplay:
    """
    A class with no instance, to store data and methods for displaying
    MathObjects with pattern string. Most attributes are dict.
    cf the MathDisplay class.

    - generic patterns:
        - unary number functions, e.g. sin
        - binary number functions, e.g. max
        - infix binary operator, e.g. divides
        - unary predicate, e.g. bounded
        - sup/inf/lim/...
    TODO: some negations are treated in pattern_data, e.g. divides,
     but should be treated here.
    """

    # constants = {
    #     'sin': ('sin', app_functional_shape, 1),
    #     'max': ('Max', app_functional_shape, 2),
    #     'divise': (_('divise')), infix_operator_shape, '|')
    # }

    # Constant Lists:
    fcts_one_var = ['sin', 'sqrt']

    fcts_two_var = ['max', 'min']

    infix = {'divides': '|',
             'ne': '\\neq',
             'prod': '\\times',
             'product': ".",
             "symmetric_difference": r'\Delta',
             }

    unary_predicate = ['bounded', 'converging_seq', 'increasing_seq',
                       'decreasing_seq', 'bounded_above', 'bounded_below',
                       'bounded_sequence', 'cauchy',
                       'continuous', 'uniformly_continuous',
                       'injective', 'surjective', 'bijective',
                       'relation_equivalence', 'partition',
                       'application', 'application_bijective', 'even', 'odd',
                       'prime']

    # Dicts
    constants_pretty_names = {'converging_seq': _("converging"),
                              'increasing_seq': _(" non decreasing"),
                              'decreasing_seq': _(" non increasing"),
                              'continuous': _("continuous"),
                              'uniformly_continuous': _("uniformly continuous"),
                              'bounded_above': _("bounded from above"),
                              'bounded_below': _("bounded from below"),
                              'bounded_sequence': _("bounded"),
                              'cauchy': _("a Cauchy sequence"),
                              'bounded': _("bounded"),  # FIXME: bounded_func
                              'limit': "lim",
                              'limit_function': "lim",
                              'limit_plus_infinity': "lim ∞",
                              'continuous_at': _('continuous at'),

                              'relation_equivalence': _('an equivalence '
                                                        'relation'),
                              'partition': _('a partition'),
                              'application': _('an application'),
                              'application_bijective': _('a bijective '
                                                         'application'),
                              'even': _('even'),
                              'odd': _('odd'),
                              'divides': _('divides'),
                              'sqrt': _('sqrt'),
                              'segment': _("segment"),
                              'prime': _('prime'),
                              'rel_prime': _('relatively prime'),
                              }

    # NB: int will be turned to tuples
    special_latex_shapes = {"abs": ('|', -1, '|'),  # FIXME: does not work ???
                            "limit": ("\lim ", -2, " = ", -1),
                            "majorant": (-1, r'\text_is', " majorant de ", -2),
                            "minorant": (-1, r'\text_is', " minorant de ", -2),
                            "continuous_at": (
                            -2, r'\text_is', _("continuous at") + " ", -1),

                            "est_majore": (-1, r'\text_is', " majoré"),
                            "est_minore": (-1, r'\text_is', " minoré"),
                            "est_borne": (-1, r'\text_is', " borné"),

                            # "limit": ("lim ", -2, " = ", -1),
                            "borne_sup": ("Sup ", -2, " = ", -1),
                            "borne_inf": ("Inf ", -2, " = ", -1),
                            "limit_plus_infinity": ("\lim", " ", -1, " = ",
                                                    "+", "\infty"),
                            "limit_function": ("\lim", ['_', (-2,)], (-3,),
                                               " = ", (-1,)),
                            # "sqrt":  ("√", -1),
                            "segment": ("[", -2, ", ", -1, "]"),
                            "bit0": (-1, " + ", -1),
                            "rel_prime": (-2, " " + _("and") + " ", -1, " " + _(
                                "relatively prime")),
                            }

    # TODO: add a "special_patterns" if both pattern and shape are special??

    latex_from_app_constant_patterns = {}
    lean_from_app_constant_patterns = {}

    # Used by Calculator to display definitions:
    fake_app_constant_patterns = {}

    # To be updated with the display metadata:
    latex_from_name_in_lean_metadata = {}

    # To be updated:
    more_calculator_definitions = None
    restricted_calculator_definitions = None

    @classmethod
    def usr_n_special_latex_shapes(cls):
        """
        Merge usr (from the lean file metadata 'display') and latex dict.
        """
        dict_ = {}
        dict_.update(cls.special_latex_shapes)
        dict_.update(cls.latex_from_name_in_lean_metadata)
        return dict_

    @staticmethod
    def pattern_from_cst_name(name):
        pattern = f'CONSTANT/name={name}'
        return pattern

    @classmethod
    def app_pattern_from_cst_name(cls, name):
        cst_pattern = cls.pattern_from_cst_name(name)
        pattern = f'APP({cst_pattern}, ...)'
        return pattern

    @classmethod
    def app_negation_pattern_from_cst_name(cls, name):
        cst_pattern = cls.pattern_from_cst_name(name)
        pattern = f'NOT(APP({cst_pattern}, ...))'
        return pattern

    @classmethod
    def fake_app_pattern_from_cst_name(cls, name):
        """
        FIXME: more than 3 args !!!
        This is used only in Calculator to determine where to put the
        metavar.
        In general it does NOT corresponds to the actual pattern as used in
        Lean, since it omits all non displayed arguments.
        """
        cst_pattern = cls.pattern_from_cst_name(name)
        nb_args = cls.nb_args(name)
        if nb_args == 1:
            pattern = f'APP({cst_pattern}, ?0)'
        elif nb_args == 2:
            pattern = f'APP({cst_pattern}, ?0, ?1)'
        else:
            pattern = f'APP({cst_pattern}, ?0, ?1, ?2)'
        return pattern

    @staticmethod
    def not_pattern_from_cst_name(name):
        pattern = f"NOT(APP(CONSTANT/name={name},...))"
        return pattern

    @classmethod
    def all_constants_names(cls) -> []:
        """
        Return the list of all Lean names of constants by concatenating the
        various lists.
        """

        names = (cls.fcts_one_var + cls.fcts_two_var + cls.unary_predicate
                 + list(cls.infix.keys()) + list(cls.usr_n_special_latex_shapes().keys()))

        return names

    @staticmethod
    def exhaustive_nb_list(l):
        nbs = []
        for item in l:
            if isinstance(item, int):
                nbs.append(item)
            elif isinstance(item, tuple) and len(item) == 1:
                nbs.append(item[0])
            elif isinstance(item, list):
                nbs.extend(PatternMathDisplay.exhaustive_nb_list(item))
        return nbs

    @classmethod
    def nb_args(cls, name):
        """
        Return the nb of args for constant name.
        This is crucial for Lean display.
        """

        if name in (cls.fcts_one_var + cls.unary_predicate):
            return 1

        elif name in (cls.fcts_two_var + list(cls.infix.keys())):
            return 2

        elif name in cls.usr_n_special_latex_shapes().keys():
            shape = cls.usr_n_special_latex_shapes()[name]
            # nbs = list(item for item in shape if isinstance(item, int))
            nbs = PatternMathDisplay.exhaustive_nb_list(shape)
            if nbs:
                max_nb = max(nbs)
                min_nb = min(nbs)
                return max(max_nb, -min_nb)
            else:
                return 0

    @classmethod
    def latex_shape_for_fcts(cls, name):
        """
        e.g.     "max": ("max", r'\parentheses', -2, ",", -1).
        """
        nb_args = cls.nb_args(name)
        args = []
        for idx in range(nb_args):
            args.extend([(idx - nb_args,), ","])
        args = tuple(args[:-1])
        pretty_name = cls.constants_pretty_names.get(name, name)
        shape = (pretty_name, r'\parentheses') + args
        return shape

    @classmethod
    def latex_shape_for_infix(cls, name):
        """
        e.g.     "sum": ((-2,), '+', (-1,))
        """
        nb_args = cls.nb_args(name)
        args = []
        for idx in range(1, nb_args):
            args.extend([(idx - nb_args,), ","])
        args = tuple(args[:-1])
        pretty_name = cls.infix.get(name, name)
        shape = ((-nb_args, ), pretty_name) + args
        return shape

    @classmethod
    def latex_shape_for_predicate(cls, name):
        """
        e.g.         "converging_seq": ((-1, ), r'\text_is', _(" converging")).
        """

        pretty_name = cls.constants_pretty_names.get(name, name)
        shape = ((-1, ), r'\text_is', pretty_name)
        return shape

    @classmethod
    def latex_negation_shape_for_predicate(cls, name):
        """
        e.g.   "converging_seq": ((-1, ), r'\text_is_not', _(" converging")).
        """

        display = cls.usr_n_special_latex_shapes().get(name)
        if display:
            if r'\text_is' in display:
                display_not = [r'\text_is_not' if item == r'\text_is'
                               else item for item in display]
                return display_not
            if r'\text_are' in display:
                display_not = [r'\text_are_not' if item == r'\text_are'
                               else item for item in display]
                return display_not
            else:
                return

        if name not in cls.unary_predicate:
            return

        pretty_name = cls.constants_pretty_names.get(name, name)
        shape = ((0, -1), r'\text_is_not', pretty_name)
        return shape

    @classmethod
    def latex_shape_for_app_of_cst(cls, name):
        if name in cls.fcts_one_var + cls.fcts_two_var:
            # NB: one var could ba handled in latex_from_node
            return cls.latex_shape_for_fcts(name)
        elif name in cls.infix:
            return cls.latex_shape_for_infix(name)
        elif name in cls.unary_predicate:
            return cls.latex_shape_for_predicate(name)
        else:
            return cls.usr_n_special_latex_shapes().get(name)

    @classmethod
    def lean_shape_for_app_of_cst(cls, name):
        """
        e.g.     "max": ("max", ' ', -2, ' ', -1).
        """
        nb_args = cls.nb_args(name)
        if nb_args is None:
            # nb_args = 1
            return
        args = [(0,), ' ']
        for idx in range(nb_args):
            args.extend([(idx - nb_args,), ' '])
        shape = tuple(args[:-1])
        return shape

    @classmethod
    def update_calculator_definitions(cls, defs: []):
        """
        Check if the definitions whose names are in defs are in
        cls.latex_from_name_in_lean_metadata, and if not,
        add a standard latex shape.
        """
        if not defs:
            defs = []
        cls.more_calculator_definitions = defs
        for name in defs:
            if name not in cls.latex_from_name_in_lean_metadata.keys():
                shape = cls.latex_shape_for_predicate(name)
                cls.latex_from_name_in_lean_metadata[name] = shape

    @classmethod
    def populate_app_pattern_dict(cls):
        """
        Populate the latex_from_app_constant_patterns and
        lean_from_app_constant_patterns dicts.
        The fake_app_constant_patterns is used by the
        Calculator to decide which definitions should be displayed.

        Shapes are computed by looking for the name entry in the unary,
        binary, infix, ... dict.
        """

        # TODO: special negation patterns/shapes
        for name in cls.all_constants_names():
            key = cls.app_pattern_from_cst_name(name)
            key_not = cls.not_pattern_from_cst_name(name)
            value = cls.latex_shape_for_app_of_cst(name)
            value_not = cls.latex_negation_shape_for_predicate(name)
            # print(value)
            lean_value = cls.lean_shape_for_app_of_cst(name)
            if value:
                cls.latex_from_app_constant_patterns[key] = value
            if value_not:
                cls.latex_from_app_constant_patterns[key_not] = value_not
            if lean_value:
                cls.lean_from_app_constant_patterns[key] = lean_value

            cst_key = cls.pattern_from_cst_name(name)
            cls.lean_from_app_constant_patterns[cst_key] = (display_name, )

            fake_pattern = cls.fake_app_pattern_from_cst_name(name)
            cls.fake_app_constant_patterns[name] = fake_pattern
            # log.debug(f"Added {name} in "
            #           f"PatternMathDisplay.fake_app_constant_patterns")

    @classmethod
    def adjust_special_shape_dict(cls):
        """
        Replace single int by tuple (e.g. '3' --> '(3, )'.
        """
        for dic in (cls.special_latex_shapes,
                    cls.latex_from_name_in_lean_metadata):
            for key, value in dic.items():
                new_value = tuple((item, ) if isinstance(item, int)
                                  else item for item in value)
                dic[key] = new_value

    @classmethod
    def update_dicts(cls):
        cls.adjust_special_shape_dict()
        cls.populate_app_pattern_dict()


PatternMathDisplay.update_dicts()

