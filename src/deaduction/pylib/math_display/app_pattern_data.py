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
from deaduction.pylib.math_display.display_data import display_name

log = logging.getLogger(__name__)

global _

# Here int stands for metavars ('?1' in pattern --> 1 in display),
# to display children use tuples, e.g. '(1, )' means second child.
latex_from_app_pattern = {
    # For functions, two patterns: (f circ g)(x) and (f circ g).
    "APP(CONSTANT/name=composition, ?1, ?2, ?3, ?4: FUNCTION(?2, ?3), "
    "?5: FUNCTION(?1, ?2), ?6)": ((-3,), r'\circ', (-2,), r"\parentheses",
                                  (-1,)),
    "APP(CONSTANT/name=composition, ?1, ?2, ?3, ?4: FUNCTION(?2, ?3), "
    "?5: FUNCTION(?1, ?2))": ((-2,), r'\circ', (-1,)),
    "APP(CONSTANT/name=composition, ?4: FUNCTION(?2, ?3), "
    "?5: FUNCTION(?1, ?2))": ((1, ), r'\circ', (2,)),
    # TODO: test Id, Id(x)
    "APP(CONSTANT/name=Identite, ?1, ?2: ?1)": ("Id", r"\parentheses", 2),

    # u_n:
    "APP(LOCAL_CONSTANT: !SEQUENCE(?2, ?3)(...), ?1: ?2)":
        ('(0, ).name', ['_', (1, )]),
    # APP(E, i) --> E_i
    #   Here E is the name of the local constant, which is self.children[0]
    "APP(LOCAL_CONSTANT: !SET_FAMILY(?2, ?3)(...), ?1: ?2)":
        ('(0,).name', ['_', (1, )]),
    "APP(CONSTANT/name=limit_function, LAMBDA(?2, ?3, ?4), ?0, ?1)":
        (r'\no_text', "lim", ['_', (-3, 1), r'\to', (-2,)], ' ', (-3, 2),
         " = ", (-1,)),
    # "APP(CONSTANT/name=metric_space, ?0)":
    #     (-1, r'\text_is', _('a metric space'))
}

# TODO: english translation
# Negative value = from end of children list
latex_from_constant_name = {
    "symmetric_difference": (-2, r'\Delta', -1),
    # "composition": (4, r'\circ', 5),  # APP(compo, X, Y, Z, g, f)
    # "prod": (1, r'\times', 2),
    "Identite": ("Id",),# FIXME: use Id for name...
    "identite": ("Id",),
    # "ne": (2, r" \neq ", 3),  # Lean name for ≠
    "interval": (r"\[", -2, ",", -1, r"\]"),

    # FIXME: translate to english in Lean files
    "majorant": (-1, r'\text_is', " majorant de ", -2),
    "minorant": (-1, r'\text_is', " minorant de ", -2),
    "continuous_at": (-2, r'\text_is', _("continuous at") + " ", -1),

    "est_majore": (-1, r'\text_is', " majoré"),
    "est_minore": (-1, r'\text_is', " minoré"),
    "est_borne": (-1, r'\text_is', " borné"),

    "limit": ("lim ", -2, " = ", -1),
    "borne_sup": ("Sup ", -2, " = ", -1),
    "borne_inf": ("Inf ", -2, " = ", -1),
    "limit_plus_infinity": ("lim ", -1, " = +∞"),
    "limit_function": ("lim", ['_', (-2,)], (-3,), " = ", (-1,)),
    # "converging_seq": (-1, r'\text_is', _(" converging")),
    # "increasing_seq": (-1, r'\text_is', _(" non decreasing")),
    # "bounded_above": (-1, r'\text_is', " " + _("bounded from above")),
    # "bounded_below": (-1, r'\text_is', " " + _("bounded from below")),
    # "bounded_sequence": (-1, r'\text_is', " " + _("bounded")),
    # "continuous": (-1, r'\text_is', _("continuous")),
    # "uniformly_continuous": (-1, r'\text_is', _("uniformly continuous")),
    # "cauchy": (-1, r'\text_is', _("a Cauchy sequence")),
    "abs": ('|', -1, '|'),
    # "max": ("Max", r'\parentheses', -2, ",", -1),
    # "min": ("Min", r'\parentheses', -2, ",", -1),
    "inv": ([r'\parentheses', (-1, )], [r'^', '-1']),
    # "product": (-2, ".", -1),
    "image": (-1, " = ", -3, "(", -2, ")"),
    # "relation_equivalence": (-1, r'\text_is', _("an equivalence relation")),
    "classe_equivalence": (r"\[", (-1, ), r"\]", ['_', (1, )]),
    "disjoint": (-2, " " + _("and") + " ", -1, " " + _("are disjoint")),
    "powerset": (r'\set_of_subsets', [r"\parentheses", (-1, )]),
    # "partition": (-1, r'\text_is', _("a partition of") + " ", -2),
    # "application": (-1, r'\text_is', _("an application") + " "),
    # "application_bijective":  (-1, r'\text_is', _("a bijective application") + " "),
    "RealSubGroup": (r"\real", ),
    # "even":  (-1,  r'\text_is', " " + _("even")),
    # "divise": (-2, ' | ', -1),
}

generic_app_dict = {
    # The following works only for some constant, do not use:
    # "NOT(APP(CST?,...))": ((0, -1), r'\text_is_not', (0, 0)),
    # Generic app for constants
    # CST? = CONSTANT with any name
    # FIXME: type PROP() below is OK? If not, move AFTER APP(?0: FUNCTION...
    "APP: PROP()(CST?, ...)": ((-1,), [r'\text_is', (0,)]),
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
    """
    latex_from_app_constant_patterns = {}
    if additional_data:
        tree = display_grammar.parse(additional_data)
        additional_dic = DisplayPatternVisitor().visit(tree)
        latex_from_constant_name.update(additional_dic)
        log.info("Adding display data from metadata of the lean file:")
        log.info(additional_dic)
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
        # Debug
        # if key in ('divise', 'delta'):
        #     log.debug(f"{key} added in dic")
        #     print(latex_from_app_constant_patterns)
    latex_from_app_pattern.update(latex_from_app_constant_patterns)

    # latex_from_app_pattern.update(generic_app_dict)


# def app_functional_shape(math_object, lean_format=False):
#
#     lean_name = math_object.name()
#     pretty_name, toto,  nb_args = PatternMathDisplay.constants[lean_name]
#     if lean_format:
#         shape = [lean_name]
#         for i in range(len(math_object.children[-nb_args:])):
#             shape.extend([i - nb_args, " "])
#         return shape
#
#     else:
#         shape = [pretty_name, '(']
#         for i in range(len(math_object.children[-nb_args:])):
#             shape.extend([i - nb_args, ", "])
#         # Replace last comma
#         shape[-1] = ')'
#         return shape


class PatternMathDisplay:
    """
    A class with no instance, to store data and methods for displaying
    MathObjects with pattern string. Most attributes are dict.
    cf the MathDisplay class.

    - generic patterns:
        - unary number functions, e.g. sin
        - binary number functions, e.g. max
        - infix binary operator, e.g. divise
        - unary predicate, e.g. bounded
        - sup/inf/lim/...
    """

    # constants = {
    #     'sin': ('sin', app_functional_shape, 1),
    #     'max': ('Max', app_functional_shape, 2),
    #     'divise': (_('divise')), infix_operator_shape, '|')
    # }

    # Constant Lists:
    fcts_one_var = ['sin', 'sqrt', 'abs']
    fcts_two_var = ['max', 'min']
    infix = {'divise': '|',
             'ne': '\\neq',
             'prod': '\\times',
             'product': ".",

             }
    unary_predicate = ['bounded', 'converging_seq', 'increasing_seq',
                       'decreasing_seq', 'bounded_above', 'bounded_below',
                       'bounded_sequence', 'cauchy',
                       'continuous', 'uniformly continuous',
                       'injective', 'surjective',
                       'relation_equivalence', 'partition',
                       'application', 'application_bijective', 'even', 'odd']
    
    # Dicts
    constants_pretty_names = {'converging_seq': _("converging"),
                              'increasing_seq': _(" non decreasing"),
                              'decreasing_seq': _(" non increasing"),
                              'continuous': _("continuous"),
                              'uniformly continuous': _("uniformly continuous"),
                              'bounded_above': _("bounded from above"),
                              'bounded_below': _("bounded from below"),
                              'bounded_sequence': _("bounded"),
                              'cauchy': _("a Cauchy sequence"),
                              'bounded': _("borné(e)"),
                              'relation_equivalence': _('an equivalence '
                                                        'relation'),
                              'partition': _('a partition'),
                              'application': _('an application'),
                              'application_bijective': _('a bijective '
                                                         'application'),
                              'even': _('even'),
                              'odd': _('odd')
                              }

    special_shapes = {"abs": ('|', -1, '|')
                      }

    latex_from_app_constant_patterns = {}
    lean_from_app_constant_patterns = {}
    fake_app_constant_patterns = {}

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
    def fake_app_pattern_from_cst_name(cls, name):
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
                 + list(cls.infix.keys()) + list(cls.special_shapes.keys()))
        return names
    
    @classmethod
    def nb_args(cls, name):
        """
        Return the nb of args for constant name.
        This is crucial for Lean display.        
        """
        
        if name in (cls.fcts_one_var + cls.unary_predicate):
            return 1
        
        if name in (cls.fcts_two_var + list(cls.infix.keys())):
            return 2

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
    def latex_shape_for_app_of_cst(cls, name):
        if name in cls.fcts_one_var + cls.fcts_two_var:
            # NB: one var could ba handled in latex_from_node
            return cls.latex_shape_for_fcts(name)
        elif name in cls.infix:
            return cls.latex_shape_for_infix(name)
        elif name in cls.unary_predicate:
            return cls.latex_shape_for_predicate(name)

    @classmethod
    def lean_shape_for_app_of_cst(cls, name):
        """
        e.g.     "max": ("max", ' ', -2, ' ', -1).
        """
        nb_args = cls.nb_args(name)
        args = [(0,), ' ']
        for idx in range(nb_args):
            args.extend([(idx - nb_args,), ' '])
        shape = tuple(args[:-1])
        return shape

    @classmethod
    def populate_app_pattern_dict(cls):
        """
        Populate the latex_from_app_constant_patterns and
        lean_from_app_constant_patterns dicts.
        """

        # TODO: negation patterns/shapes
        for name in cls.all_constants_names():
            key = cls.app_pattern_from_cst_name(name)
            value = cls.latex_shape_for_app_of_cst(name)
            # print(value)
            lean_value = cls.lean_shape_for_app_of_cst(name)
            cls.latex_from_app_constant_patterns[key] = value
            cls.lean_from_app_constant_patterns[key] = lean_value
            # TODO: move elsewhere?
            cst_key = cls.pattern_from_cst_name(name)
            cls.lean_from_app_constant_patterns[cst_key] = (display_name, )

            fake_pattern = cls.fake_app_pattern_from_cst_name(name)
            cls.fake_app_constant_patterns[name] = fake_pattern

    @classmethod
    def update_dicts(cls):
        cls.populate_app_pattern_dict()


PatternMathDisplay.update_dicts()

