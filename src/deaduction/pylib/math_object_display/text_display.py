"""
# text_display.py : <#ShortDescription> #
    
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

global _

# "QUANT_∀": (r"\forall", 1, r" \in_quant ", 0, ", ", 2),
# "QUANT_∃": (r"\exists", 1, r" \in_quant ", 0, r'\such_that', 2),
# "QUANT_∃!": (r"\exists !", 1, r" \in_quant ", 0, r'\such_that', 2)

# "SET": (r'\set_of_subsets', 0),  # (r'{\mathcal P}', "(", 0, ")"),
# "PROP": (r'\proposition',),
# "TYPE": (r'\set',),
# "FUNCTION": (r'\function_from', 0, r'\to', 1),  # (0, r" \to ", 1),
# "SEQUENCE": (r'\sequence_from', 0, r'\to', 1)  # (0, r" \to ", 1),

couples_of_nodes_to_text = {
    ("QUANT_∀", "SET"): (_("For every subset {} of {}"),
                         (1, (0, 0))),
    ("QUANT_∀", "PROP"): (_("For every proposition {}"),
                          (1,)),
    ("QUANT_∀", "TYPE"): (_("For every set {}"),
                          (1,)),
    ("QUANT_∀", "FUNCTION"): (_("For every function {} from {} to {}"),
                          (1, (0, 0), (0, 1))),
    ("QUANT_∀", "SEQUENCE"): (_("For every sequence {} in {}"),
                              (1, (0, 1))),
    ("QUANT_∃", "SET"): (_("There exists a subset {} of {}"),
                         (1, (0, 0))),
    ("QUANT_∃", "PROP"): (_("There exists a proposition {}"),
                          (1,)),
    ("QUANT_∃", "TYPE"): (_("There exists a set {}"),
                          (1,)),
    ("QUANT_∃", "FUNCTION"): (_("There exists a function {} from {} to {}"),
                              (1, (0, 0), (0, 1))),
    ("QUANT_∃", "SEQUENCE"): (_("There exists a sequence {} in {}"),
                              (1, (0, 1))),
    ("QUANT_∃!", "SET"): (_("There exists a unique subset {} of {}"),
                         (1, (0, 0))),
    ("QUANT_∃!", "PROP"): (_("There exists a unique proposition {}"),
                          (1,)),
    ("QUANT_∃!", "TYPE"): (_("There exists a unique set {}"),
                          (1,)),
    ("QUANT_∃!", "FUNCTION"): (_("There exists a unique function {} from {} "
                                 "to {}"),
                              (1, (0, 0), (0, 1))),
    ("QUANT_∃!", "SEQUENCE"): (_("There exists a unique sequence {} in {}"),
                              (1, (0, 1)))
}

couples_of_nodes_to_utf8 = {
    ("QUANT_∀", "SET"): (r"\forall", 1, r" \subset ", (0, 0), ", ", 2),
    ("QUANT_∀", "PROP"): (r"\forall", 1, r'\proposition'),
    ("QUANT_∀", "TYPE"): (r"\forall", 1, r" \set"),
    ("QUANT_∀", "FUNCTION"): (r"\forall", 1, r" \function_from", (0, 0),
                              r'\to', (0, 1)),
    ("QUANT_∀", "SEQUENCE"): (r"\forall", 1, r'\in', (0, 1)),
    # Other quantifiers are similar
    # ("QUANT_∃", "SET"): (r"\exists", 1, r" \subset ", (0, 0), ", ", 2),
    # ("QUANT_∃", "PROP"): (r"\exists", 1, r'\proposition'),
    # ("QUANT_∃", "TYPE"): (r"\exists", 1, r" \set"),
    # ("QUANT_∃", "FUNCTION"): (r"\exists", 1, r" \function_from", (0, 0),
    #                           r'\to', (0, 1)),
    # ("QUANT_∃", "SEQUENCE"): (r"\exists", 1, r'\in', (0, 1)),
}




def quant_text_display(strings: list, text_depth=0):
    """
    Compute a smart version of a quantified expression.
    :param strings: tree of strings with Latex macros, e.g.
    [r'\forall', 'f', [r'\function_from', 'X', r'\to', 'Y']]

    This allow in particular
        - rightful translation, where we need to know the
        grammatical gender of "function" to spell correctly "for every".
        - rightful word placing.

    Process, in particular:
    - For every element
    - For every function
    - For every subset
    ...
    - Turn "for every element A of P(X)" into
        "For every subset A of X"

    :return: modified tree of strings, with macro replaced by (tra,slated)
    text.
    """



