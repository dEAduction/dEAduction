"""
# new_display.py : compute display for MathObject #

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 12 2021 (creation)
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
from typing import Union, Optional
import logging

from deaduction.pylib.mathobj import MathObject
from deaduction.pylib.pattern_math_obj import MetaVar
from deaduction.pylib.math_display.display_data import MathDisplay
from deaduction.pylib.math_display.pattern_init import (pattern_latex,
                                                        pattern_lean,
                                                        pattern_text,
                                                        pattern_latex_for_type)
from deaduction.pylib.math_display.display import abstract_string_to_string
from deaduction.pylib.math_display.display_math import (shallow_latex_to_text,
                                                        latex_to_text_func)

log = logging.getLogger(__name__)

# latex_from_node.update(latex_from_quant_node)

# latex_from_node = MathDisplay.latex_from_node
# lean_from_node = MathDisplay.lean_from_node
# needs_paren = MathDisplay.needs_paren


class MathDescendant:
    """
    A class to store a root MathObject and a line of descent.
    """
    def __init__(self, root_math_object: MathObject,
                 line_of_descent=tuple()):
        self._root_math_object = root_math_object
        self.line_of_descent = line_of_descent
        assert self.root_math_object.descendant(line_of_descent) is not None

    @property
    def root_math_object(self):
        if self._root_math_object:
            return self._root_math_object
        else:
            return MathObject.NO_MATH_TYPE

    @property
    def descendant(self):
        if self.line_of_descent:
            return self.root_math_object.descendant(self.line_of_descent)
        else:
            return self.root_math_object


class MathString(str, MathDescendant):
    """
    A string with annotations:
    - the root_math_object is the MathObject from which the request of display
        originates.
    - the line_of_descent is the place in root_math_object corresponding to
    the string.
    """

    marked_cursor = r'\DeadCursor'

    def __new__(cls, string, root_math_object: MathObject,
                line_of_descent: tuple = None):
        instance = str.__new__(cls, string)
        instance._root_math_object = root_math_object
        instance.line_of_descent = line_of_descent
        return instance

    def __init__(self, string, root_math_object, line_of_descent=tuple()):
        str.__init__(string)
        MathDescendant.__init__(self, root_math_object=root_math_object,
                                line_of_descent=line_of_descent)

    @classmethod
    def formatter(cls, format_name: str):
        """
        This class method is supposed to be used for inserting a formatter
        expression, e.g. '\\used_property'.
        """

        return cls(string=format_name, root_math_object=None)

    @classmethod
    def replace_string(cls, math_string, new_string):
        """
        Return a copy of math_string with string replaced by new_string.
        """
        new_math_str = cls(new_string,
                           math_string.root_math_object,
                           math_string.line_of_descent)
        return new_math_str

    def last_address_of(self, math_object):
        """
        For compatibility with MathList.
        """
        if self.descendant == math_object:
            return tuple()
        else:
            return None

    # @property
    # def address_of_first_leaf_descendant(self):
    #     """
    #     This is just for compatibility with MathList.
    #     """
    #     return tuple()

    # @classmethod
    # def cursor(cls):
    #     return cls(string = cls.marked_cursor, root_math_object=None)


MathString.error_string = MathString("***", MathObject.NO_MATH_TYPE)


class MathList(list, MathDescendant):
    """
    This class is used to store structured strings in order to display
    MathObject. Its core data is a list whose items must be of one the
    following types (as processed by the process_shape_item() method):
    - MathList,
    - MathString,
    - int (coding for a child nb)
    - tuple of int (coding for a descendant address)
    - MathObject, e.g. coming from metavars in a pattern shape (they will be
    replaced by its own shape). FIXME: this should not happen?
    """

    variable = MathString(r"\variable", root_math_object=None)

    def __init__(self, iterable,
                 root_math_object: MathObject,
                 line_of_descent=tuple(),
                 pattern=None,
                 pattern_dic=None,
                 format_="utf8",
                 text=False
                 ):
        super().__init__(iterable)
        MathDescendant.__init__(self, root_math_object, line_of_descent)

        self.format_ = format_
        self.text = text

        # For debugging:
        self.pattern = pattern
        self.pattern_dic = pattern_dic

    def __str__(self):
        flat_list = [str(item) for item in self]
        return ''.join(flat_list)

    def replace_string(self, idx, new_string: str) -> bool:
        """
        Replace the string of item self[idx] ny new_string, converted to a
        MathString with the same root and line ode descent.
        """
        math_string = self[idx]
        if not isinstance(math_string, MathString):
            return False
        elif isinstance(new_string, MathString):
            # Just replace
            self[idx] = new_string
        else:
            # Convert and replace
            new_math_str = MathString.replace_str(math_string, new_string)
            self[idx] = new_math_str
            return True

    @property
    def lean_format(self):
        return self.format_ == "lean"

    def item_for_address(self, position: tuple):
        """
        Return the item at the given position, considered as an address in
        the tree of strings.
        """

        if not position:
            # Empty tuple
            return self
        else:
            child_idx, *further_descendant = position
            assert isinstance(self, MathList) and len(self) > child_idx
            return self[child_idx].item_for_position(further_descendant)

    def last_address_of(self, math_object) -> tuple:
        """
        Recursively find the last address whose item corresponds to given
        math_object. Return None if not found.
        """

        for idx in range(len(self)).__reversed__():
            item = self[idx]
            if item.descendant == math_object:
                return (idx,)
            else:
                partial_address = item.last_address_of(math_object)
                if partial_address is not None:  # Maybe the empty tuple!
                    return (idx,) + partial_address

    @property
    def address_of_first_leaf_descendant(self):
        """
        Return a pertinent tuple of zeros.
        """
        descendant = self[0]
        if not isinstance(descendant, MathList):
            return (0,)
        else:
            return (0,) + descendant.address_of_first_leaf_descendant

    # TODO: expanded_latex_shape should be a here?

    def check_completeness(self) -> bool:
        """
        Recursively checks that self's items are MathString or MathLists.
        Change pure strings to MathStrings.
        """

        idx = 0
        for item in self:
            if isinstance(item, MathString):
                return True
            elif isinstance(item, str):
                self[idx] = MathString(item, root_math_object=None)
            elif isinstance(item, MathList):
                return item.check_completeness()
            else:
                raise TypeError(f"Item {item} of a complete MathList"
                                f"should be either MathList or MathString")
            idx += 1

    def expand_latex_shape(self):
        """
        Expand latex shape. The resulting self is a MathList whose items are
        either MathString or MathList with the same property.
        """
        new_expanded_latex_shape(self)
        self.check_completeness()

    def process_text(self):
        """
        Replace some symbols by plain text, or shorten some text:
        """

        text_depth = 100 if self.text else 0
        if not self.lean_format:
            shallow_latex_to_text(self, text_depth)

    def format(self):
        """
        Modify self to a specific format (Lean, html, utf8).
        """
        # TODO


def process_shape_macro(self, shape_item: str) -> Union[str, MathObject]:
    """
    Process macros in shape:
        - if item has the form "root.attribute", with
            - root either "self", or a tuple
            - attribute an attribute of the corresponding MathObject, e.g.
            math_type, name, value, local_constant_shape
        then item is substituted with the corresponding object.

    Note that the attribute part may be empty, e.g. 'self' just display self;
    this is useful for math_type_to_display, 'self' with be displayed with
    the to_display() method. (Beware of infinite recursion).
    """

    attributes = shape_item.split('.')

    root = attributes.pop(0)

    # A - Determine math_object:
    # (1) 'self'
    if root == 'self':
        math_object = self

    # (2) '(1, 0)'
    elif root.startswith('(') and root.endswith(')'):
        chain = [item.strip() for item in root[1:-1].split(',')]
        descent = tuple(int(item) for item in chain if item.isdigit())
        math_object = self.descendant(line_of_descent=descent)

    else:
        #############################
        return shape_item

    # B - Apply attributes iteratively:
    object_ = math_object
    while attributes and object_:
        attribute = attributes.pop(0)
        if hasattr(object_, attribute):
            object_ = getattr(math_object, attribute, None)

    return object_


def global_pre_shape_to_pre_shape(pre_shape, text=False):
    """
    Turn a global pre_shape, e.g.
        ("global", r"\forall {} \subset {}, {}", 0, (0, 0), 1),
    into a "normal" pre_shape, e.g.
        (r"\forall", 0, r" \subset ", (0, 0), ", ", 1),
    (or, in text mode,
        ("for every subsets ", 0, " of ", (0,0), ", ", 1).
    )
    """
    gps = list(pre_shape)
    words = gps.pop(0)
    if text:  # Try to convert into text  FIXME: this is odd??
        words, success = latex_to_text_func(words)
    words = words.split("{}")
    vars_ = gps
    pre_shape = []

    # Intertwine words and variables:
    while words:
        pre_shape.append(words.pop(0))
        if vars_:
            pre_shape.append(vars_.pop(0))

    return pre_shape


def substitute_metavars(shape, metavars: [MetaVar], pattern):
    """
    Recursively substitute integers by the corresponding matched math object in
    shape.
    The given integer is the index of the metavar in the metavars list,
    then the matched math object is obtained from the pattern.
    Mind that metavars is NOT equal to pattern.metavars: the lists are
    probably equal up to a permutation, but the indices in metavars
    correspond to the number in the pattern, e.g. ?0 is the first item in
    metavars (but not necessarily in pattern.metavars).
    """
    if isinstance(shape, int):
        item = shape
        mvar = metavars[item]
        return mvar.matched_math_object(pattern.metavars,
                                        pattern.metavar_objects)
    elif isinstance(shape, list):
        return list(substitute_metavars(item, metavars, pattern)
                    for item in shape)
    else:  # e.g. str, MathObject
        return shape


def lean_shape(self: MathObject) -> []:
    """
    Shape for lean format. See the latex_shape() method doc.
    """
    shape = None
    for pattern, pre_shape, metavars in pattern_lean:
        # if pattern.node == 'LOCAL_CONSTANT' and len(pattern.children) == 3:
        #     print("debug")
        if pattern.match(self):
            # Now metavars are matched
            # log.debug(f"Matching pattern --> {pre_shape}")
            shape = tuple(substitute_metavars(item, metavars, pattern)
                          for item in pre_shape)
            break
    if not shape:
        if self.node in MathDisplay.lean_from_node:
            shape = list(MathDisplay.lean_from_node[self.node])

            shape = [process_shape_macro(self, item) if isinstance(item, str)
                     else item for item in shape]
    if shape:
        # (3) Process macros
        if shape[0] == "global":
            shape = global_pre_shape_to_pre_shape(shape[1:])

        shape = [process_shape_macro(self, item) if isinstance(item, str)
                 else item for item in shape]

        shape = MathDisplay.wrap_lean_shape_with_type(self, shape)

    return shape


def latex_shape(self: MathObject, is_type=False, text=False,
                lean_format=False) -> MathList:
    """
    Return the shape of self, e.g.
            [r'\forall', 1, r'\subset', 0, (2, )]
    where 0, 1 are replaced by pertinent MathObjects (but not (2, ) that
    stands for children[2], not for metavars).

    If is_type is True, then pattern is first looked for in the
    pattern_latex_for_type list. This should be used for math_types of
    context objects.

    If text is True, then the pattern_text list is used first.

    Here we make as few substitution as possible, namely we only substitute
    metavars and not children or descendant, since descendant nb are useful
    to add appropriate parentheses.
    """

    shape = None
    shape_math = MathList((), self,
                          format_="lean" if lean_format else "utf8",
                          text=text)

    # FIXME?
    if lean_format:
        shape = self.lean_shape()
        if shape:  # Really, no more processing??
            return shape

    # (0) Dictionaries to be used (order matters!):
    dicts = []
    if is_type:
        dicts.append(pattern_latex_for_type)
    if text:
        dicts.append(pattern_text)
    dicts.append(pattern_latex)

    # (1) Search for patterns
    for dic in dicts:
        for pattern, pre_shape, metavars in dic:
            if pattern.match(self):
                # Now metavars are matched
                # log.debug(f"Matching pattern --> {pre_shape}")
                shape = tuple(substitute_metavars(item, metavars, pattern)
                              for item in pre_shape)
                break
        if shape:
            shape_math.pattern = pattern
            shape_math.pattern_dic = dic
            break

    # (2) Generic cases: use only node
    if not shape:
        if self.node in MathDisplay.latex_from_node:
            shape = list(MathDisplay.latex_from_node[self.node])
        else:
            shape = ["***"]  # Default

    # (3) Process macros
    if shape[0] == "global":
        shape = global_pre_shape_to_pre_shape(shape[1:], text=text)

    # shape = [process_shape_macro(self, item) if isinstance(item, str)
    #          else item for item in shape]

    for item in shape:
        if isinstance(item, str):
            new_item = process_shape_macro(self, item)
            if isinstance(new_item, str):
                new_item = MathString(new_item, root_math_object=self)
                # print(f"Stringmath of {new_item.math_object()}: {new_item}")
            shape_math.append(new_item)
            # print(isinstance(s, str))
        else:
            shape_math.append(item)
    # print(f"MathList of {shape_math.math_object()}: {shape_math}")
    # print(isinstance(shape_math, list))
    return shape_math


def process_shape_item(item, math_object=None, text=False,
                       lean_format=False):
    """
    Replace item by its shape.
    tuples corresponds to children (or descendants) and are also replaced.
    """

    if isinstance(item, str):
        # Nothing to do!
        return item

    # Default values
    new_shape = None
    new_math_object = math_object

    if isinstance(item, tuple):
        maybe_callable = item[-1]
        if callable(maybe_callable):
            # e.g. (display_name, (0,))
            line_of_descent = item[:-1]
            new_math_object = math_object.descendant(line_of_descent)
            item = maybe_callable
            # Will be further processed below in case item is callable
        else:
            new_math_object = math_object.descendant(item)

    if callable(item):
        new_shape = item(new_math_object)
        if isinstance(new_shape, str):
            return new_shape

    elif isinstance(item, MathObject):
        new_math_object = item

    elif isinstance(item, int):
        new_math_object = math_object.children[item]

    elif isinstance(item, list):
        new_shape = item

    if new_math_object is None:
        new_item = '***'
    elif new_shape or new_math_object != math_object:
        new_item = expanded_latex_shape(math_object=new_math_object,
                                        shape=new_shape,
                                        text=text, lean_format=lean_format)
    else:
        new_item = '***'

    # PARENTHESES?
    if (new_math_object != math_object and
            MathDisplay.needs_paren(math_object, new_math_object, item)):
        # Fixme
        new_item = [r'\parentheses', new_item]

    return new_item


# Gestion des parenthèses :
# --> Enlever les parenthèses redondantes
# puis c'est utilisable pour gérer le curseur du calculator

# Remplacer les int/tuple restant par leur math_object,
# --> ou bien to_display(),
# --> ou bien callable
# puis afficher


def full_latex_shape_with_descendants(math_object, shape=None, text=False,
                                      lean_format=False) -> []:
    """
    Recursively replace each child or descendant item by its shape,
    until we get to childless object or CONSTANT/LOCAL_CONSTANT.
    The result is a tree of lists, with basic items which are either
    - strings,
    - or int/tuples coding for descendants, e.g.
        1 --> self.children[1]
        (1,0) --> self.children[1].children[0]
    - or callable, e.g.
        display_name --> self.display_name()
    - or mixed, e.g.
        (1,0, display_name) --> self.children[1].children[0].display_name().

    Strings are coding either for symbols, e.g. +, -, etc.;
    they maybe latex macro, e.g. \circ, \in, etc.;
    they maybe other macros, e.g.
    \variable  (used for colouring)
    \notext
    \parentheses
    ...
    """
    # Fixme: obsolete?
    # FIXME: text is useless?

    if not shape:
        shape = math_object.latex_shape(text=text, lean_format=lean_format)

    full_shape = MathList([], root_math_object=math_object)
    for item in shape:
        if isinstance(item, int) or isinstance(item, tuple):
            child = math_object.descendant(item)
            if (child.children and not child.is_constant() or
                    child.is_local_constant()):
                if isinstance(item, tuple) and callable(item[-1]):
                    #  e.g. (0, 1, display_name)
                    #  --> [display_name, (0,1)]
                    expanded_item = [item[-1], item[:-1]]
                else:
                    expanded_item = full_latex_shape_with_descendants(
                        math_object=math_object, shape=None, text=text,
                        lean_format=lean_format)
            else:
                expanded_item = [item]

            if MathDisplay.needs_paren(math_object, child, item):
                expanded_item = [r'\parentheses', expanded_item]

            full_shape.append(expanded_item)

        else:
            full_shape.append(item)


def expanded_latex_shape(math_object=None, shape=None, text=False,
                         lean_format=False) -> []:
    """
    Recursively replace each MathObject by its shape.
    tuples corresponds to children (or descendants) and are also replaced.
    Return a tree of string, structured by lists.
    """

    if not shape:
        shape = math_object.latex_shape(text=text, lean_format=lean_format)

    item = shape[0]
    new_item = process_shape_item(item, math_object=math_object, text=text,
                                  lean_format=lean_format)

    more_shape = (expanded_latex_shape(math_object=math_object,
                                       shape=shape[1:],
                                       text=text,
                                       lean_format=lean_format)
                  if len(shape) > 1 else [])

    # if not isinstance(new_item, list):
    #     new_item = [new_item]
    expanded_shape = [new_item] + more_shape

    return expanded_shape


def new_process_shape_item(item, math_object=None, line_of_descent=tuple(),
                           text=False, lean_format=False) -> Union[MathString,
                                                                   MathList]:
    """
    Replace item by its expanded shape.
    tuples corresponds to children (or descendants) and are also replaced.
    """

    # FIXME: should return only MathString or MathList instances?

    if isinstance(item, str):
        if isinstance(item, MathString):
            # MathString
            return item
        else:
            # MathString
            return MathString(item, root_math_object=math_object,
                              line_of_descent=line_of_descent)

    # Default values
    new_item = MathString.error_string
    new_shape = None
    new_line = line_of_descent

    if isinstance(item, tuple):
        maybe_callable = item[-1]
        if callable(maybe_callable):
            # e.g. (display_name, (0,))
            new_line = line_of_descent + item[:-1]
            item = maybe_callable
            # Will be further processed below in case item is callable
        else:
            new_line = line_of_descent + item

    if callable(item):
        descendant = math_object.descendant(new_line)
        new_shape = item(descendant)
        if isinstance(new_shape, str):
            # MathString
            return MathString(new_shape, math_object, line_of_descent)

    elif isinstance(item, int):
        new_line = line_of_descent + (item,)

    elif isinstance(item, list):
        new_shape = MathList(item, math_object, line_of_descent)

    elif isinstance(item, MathObject):
        print(1/0)
        # FIXME: improve info?
        #  Root Math Object will NOT be the good one.
        new_item = full_latex_shape_with_descendants(item, text=text,
                                                     lean_format=lean_format)

    # Recursively expand item
    if new_shape or new_line != line_of_descent:
        # Fixme: MathList?
        new_item = new_expanded_latex_shape(math_object=math_object,
                                            line_of_descent=new_line,
                                            shape=new_shape,
                                            text=text, lean_format=lean_format)

    # PARENTHESES?
    if new_line != line_of_descent:
        parent = math_object.descendant(line_of_descent)
        child = math_object.descendant(new_line)
        if MathDisplay.needs_paren(parent, child, item):
            # MathList
            new_item = MathList([r'\parentheses', new_item],
                                new_item.root_math_object,
                                new_item.line_of_descent)

    return new_item


def new_expanded_latex_shape(shape: Optional[MathList] = None,
                             math_object=None, line_of_descent=None,
                             text=None,
                             lean_format=None) -> MathList:
    """
    Recursively replace each MathObject by its shape.
    tuples corresponds to children (or descendants) and are also replaced.
    Return a tree of string, structured by lists.
    """

    if not shape:
        if not math_object:
            raise ValueError("At least one of shape and math_object must be "
                             "provided")
        else:
            descendant = math_object.descendant(line_of_descent)
            shape = descendant.latex_shape(text=text, lean_format=lean_format)
    else:
        if math_object is None:
            math_object = shape.root_math_object
        if line_of_descent is None:
            line_of_descent = shape.line_of_descent
        if text is None:
            text = shape.text
        if lean_format is None:
            lean_format = shape.lean_format

    # expanded_shape = MathList([],
    #                           root_math_object=math_object,
    #                           line_of_descent=line_of_descent)

    idx = 0
    for item in shape:
        new_item = new_process_shape_item(item,
                                          math_object=math_object,
                                          line_of_descent=line_of_descent,
                                          text=text,
                                          lean_format=lean_format)
        shape[idx] = new_item
        idx += 1
        # expanded_shape.append(new_item)

    # return expanded_shape
    return shape


def to_display(self: MathObject, format_="html", text=False,
               use_color=True, bf=False, is_type=False,
               used_in_proof=False) -> str:
    """
    Method to display MathObject on screen.
    Note that it cannot be put in MathObject module, due to import problem
    (namely: we need PatternMathObject to get the right shape to display).
    """

    lean_format = (format_ == "lean")

    # (1) Compute expanded shape
    shape: MathList = self.latex_shape(is_type=is_type, text=text,
                                       lean_format=lean_format)

    if used_in_proof and not lean_format:
        # shape = [r'\used_property'] + shape
        shape.insert(0, MathString.formatter(r'\used_property'))

    # abstract_string = new_expanded_latex_shape(math_object=self, shape=shape,
    #                                        text=text, lean_format=lean_format)

    # new_expanded_latex_shape(shape=shape)
    shape.expand_latex_shape()

    # (3) Replace some symbols by plain text, or shorten some text:
    # text_depth = 100 if text else 0
    # if not lean_format:
    #     # abstract_string = shallow_latex_to_text(abstract_string, text_depth)
    # shallow_latex_to_text(shape, text_depth)
    shape.process_text()

    # (4) Format into a displayable string
    display = abstract_string_to_string(shape, format_,
                                        use_color=use_color, bf=bf,
                                        no_text=not text)

    return display


def math_type_to_display(self, format_="html",
                         text=False,
                         is_math_type=False,
                         used_in_proof=False) -> str:

    math_type = self if is_math_type else self.math_type
    return math_type.to_display(format_, text=text, is_type=True,
                                used_in_proof=used_in_proof)


#############################
# Add methods to MathObject #
#############################
MathObject.to_display = to_display
MathObject.latex_shape = latex_shape
MathObject.lean_shape = lean_shape
MathObject.math_type_to_display = math_type_to_display

