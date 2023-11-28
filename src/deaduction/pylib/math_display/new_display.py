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

import logging

from deaduction.pylib.text import replace_dubious_characters
from deaduction.pylib.math_display.display_data import MathDisplay
from deaduction.pylib.math_display.pattern_init import PatternInit
from deaduction.pylib.math_display.display import (html_display, 
                                                   # lean_display,
                                                   utf8_display)
from deaduction.pylib.math_display.display_utils import (shallow_latex_to_text,
                                                         latex_to_text_func)
from deaduction.pylib.math_display.more_display_utils import (cut_spaces,
                                                              cut_successive_spaces)

log = logging.getLogger(__name__)


#####################
#####################
# Latex shape utils #
#####################
#####################

def process_shape_macro(self, shape_item: str):  # -> Union[str, MathObject]:
    """
    Process macros in shape:
        - if item has the form "root.attribute", with
            - root either "self", or a tuple
            - attribute an attribute of the corresponding MathObject, e.g.
            math_type, name, value, local_constant_shape
        then item is substituted with the corresponding object.

    Note that the attribute part may be empty, e.g. 'self' just display self;
    this is useful for math_type_to_display, 'self' will be displayed with
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


def substitute_metavars(shape, metavars,  # : [MetaVar]
                        pattern):
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


def process_shape_item(item, root_math_object=None, line_of_descent=tuple(),
                       text=False, lean_format=False):
    """
    Replace item by its expanded shape.
    tuples corresponds to children (or descendants) and are also replaced.

    Beware that math_object is the root_math_object, an ancestor of item,
    but not the math_object corresponding to item, which equals
    math_object.descendant(line_of_descent).

    In this function, it is crucial that all root_math_objects and
    line_of_descent are correctly computed.
    """

    # Default values
    descendant = root_math_object.descendant(line_of_descent)
    new_descendant = None
    new_item = None
    new_line = line_of_descent

    ###################################
    # Process cases of string or list #
    ###################################
    if isinstance(item, str):
        if isinstance(item, MathString):
            # MathString
            return item
        else:
            # MathString
            return MathString(item, root_math_object=root_math_object,
                              line_of_descent=line_of_descent)
    elif isinstance(item, list):
        new_item = MathList(item, root_math_object, line_of_descent)
        new_item.recursive_expand_latex_shape(text=text,
                                              lean_format=lean_format)
        return new_item

    #################################
    # Process case of a math_object #
    #################################
    elif str(type(item)) == 'MathObject':
        # print(1/0)
        # FIXME: improve info?
        #  Root Math Object will NOT be the good one.
        log.warning(f"Found MathObject {item} in shape, proceed and cross "
                    f"fingers...")
        shape = item.latex_shape(text=text, lean_format=lean_format)
        new_item = shape.recursive_expand_latex_shape(text=text,
                                                      lean_format=lean_format)
        return new_item

    ####################################
    # Process case of a new descendant #
    ####################################
    elif isinstance(item, tuple):
        maybe_callable = item[-1]
        if callable(maybe_callable):
            # e.g. (display_name, (0,))
            new_line = line_of_descent + item[:-1]
            new_descendant = root_math_object.descendant(new_line)
            item = maybe_callable
            # Will be further processed below in case item is callable
        else:
            new_line = line_of_descent + item
            new_descendant = root_math_object.descendant(new_line)

    if callable(item):
        if not new_descendant:
            new_descendant = descendant
        new_item = item(new_descendant)
        if isinstance(new_item, str):
            # MathString
            return MathString(new_item, root_math_object, new_line)
        elif isinstance(new_item, list):
            # Fixme?
            ml = MathList(new_item, root_math_object, new_line)
            ml.recursive_expand_latex_shape(text=text, lean_format=lean_format)
            ml.check_completeness()
            return ml

    elif isinstance(item, int):
        new_line = line_of_descent + (item,)
        new_descendant = root_math_object.descendant(new_line)

    ###########################
    # Recursively expand item #
    ###########################
    if not new_item and not new_descendant:
        return MathString.error_string

    if not new_item:
        new_item = new_descendant.latex_shape(text=text,
                                              lean_format=lean_format)

        new_item.set_root_math_object(root_math_object)
        new_item.add_line_of_descent(new_line)

    new_item.recursive_expand_latex_shape(text=text,
                                          lean_format=lean_format)

    # PARENTHESES?
    if new_line != line_of_descent:
        parent = root_math_object.descendant(line_of_descent)
        child = root_math_object.descendant(new_line)
        if MathDisplay.needs_paren(parent, child, item):
            # MathList
            new_item = MathList([MathList.parentheses, new_item],
                                new_item.root_math_object,
                                new_item.line_of_descent)

    return new_item


###################################
###################################
# MathString and MathList classes #
###################################
###################################

class MathDescendant:
    """
    A class to store a root MathObject and a line of descent.
    """

    NO_MATH_TYPE = None  # Set in MathObject

    def __init__(self, root_math_object, line_of_descent=tuple()):
        self._root_math_object = (root_math_object if root_math_object
                                  else self.NO_MATH_TYPE)
        self.line_of_descent = line_of_descent

    @property
    def root_math_object(self):
        if self._root_math_object:
            return self._root_math_object
        else:
            return self.NO_MATH_TYPE

    @root_math_object.setter
    def root_math_object(self, math_object):
        self._root_math_object = math_object

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

    error_string = "***"
    cursor = r'\DeadCursor'
    marked = r'\marked'
    dummy_var = r'\dummy_variable'
    var = r'\variable'
    begin_sub = '<sub>'
    end_sub = '</sub>'

    _format_strings = {error_string, cursor, marked, dummy_var, var,
                       begin_sub, end_sub}

    is_tagged = False

    def __new__(cls, string, root_math_object=None,
                line_of_descent: tuple = None):
        instance = str.__new__(cls, string)
        instance._root_math_object = root_math_object
        instance.line_of_descent = line_of_descent
        return instance

    def __init__(self, string, root_math_object=None, line_of_descent=tuple()):
        str.__init__(string)
        MathDescendant.__init__(self, root_math_object=root_math_object,
                                line_of_descent=line_of_descent)

    def set_root_math_object(self, math_object):
        self.root_math_object = math_object

    def add_line_of_descent(self, line_of_descent):
        self.line_of_descent = line_of_descent + self.line_of_descent

    @classmethod
    def format_strings(cls):
        """
        We remove the empty string since it should not be considered
        as a formatter.
        """
        return cls._format_strings.difference("")

    ######################################################
    # Some methods for compatibility with MathList items #
    ######################################################
    def to_string(self):
        """
        For compatibility with MathList.
        """
        return self

    def is_marker(self):
        """
        The empty string may be used to mark beginning/end of some MathList,
        so it is not considered as a formatter.  Fixme
        """
        return self == '' and self.root_math_object is not None

    def is_formatter(self):
        """
        True iff self is in self.format_strings list, which is extended
        dynamically when the formatter() method is used.
        """
        return self in self.format_strings()  # and not self.is_marker()

    def is_format_parenthesis(self):
        """
        True if self is a priority parenthesis (NOT added by user).
        """

        test1 = (self in ('(', ')'))

        # Added by usr?
        test2 = (self.descendant.node.endswith('PARENTHESES') or
                 self.descendant.node.endswith('PARENTHESIS'))

        return test1 and not test2

    def significant_items(self):
        return [] if self.is_formatter() else [self]

    def remove_formatters(self):
        return None if self.is_formatter() else self

    def first_descendant(self):
        """
        For compatibility with MathList.
        """
        return self

    def last_descendant(self):
        """
        For compatibility with MathList.
        """
        return self

    def item_for_address(self, position: tuple):
        """
        Return the item at the given position, considered as an address in
        the tree of strings.
        """

        if not position:
            # Empty tuple
            return self
        else:
            raise ValueError(f"MathString has no item at non trivial "
                             f"position{position}.")

    @classmethod
    def formatter(cls, format_name: str):
        """
        This class method is supposed to be used for inserting a formatter
        expression, e.g. '\\used_property'.

        IMPORTANT: this method must be restricted to strings which do not
        display anything on screen by themselves (e.g. a parenthesis is NOT
        a formatter).
        """
        if format_name == '':
            print('')
        cls._format_strings.add(format_name)
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

    def map(self, func):
        new_string = func(self)
        if new_string is not None:
            return self.replace_string(self, func(self))

    def last_address_of(self, math_object):
        """
        For compatibility with MathList.
        """
        if self.descendant == math_object:
            return tuple()
        else:
            return None

    # def cut_spaces(self):
    #     new_string = self.cut_spaces()
    #     if new_string:
    #         return self.replace_string(self, new_string)

    # @property
    # def address_of_first_leaf_descendant(self):
    #     """
    #     This is just for compatibility with MathList.
    #     """
    #     return tuple()

    # @classmethod
    # def cursor(cls):
    #     return cls(string = cls.marked_cursor, root_math_object=None)


MathString.error_string = MathString.formatter("***")
MathString.cursor = MathString.formatter(r'\DeadCursor')
MathString.marked_object = MathString.formatter(r'\marked')
MathString.left_paren = MathString('(', root_math_object=None)
MathString.right_paren = MathString(')', root_math_object=None)


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

    string = MathString  # For reference from instances of this class
    formatter = MathString.formatter
    variable = formatter(r"\variable")  # FIXME: used?
    parentheses = formatter(r'\parentheses')

    is_tagged = False

    def __init__(self, iterable,
                 root_math_object,
                 line_of_descent=tuple(),
                 pattern=None,
                 pattern_dic=None,
                 format_="utf8",
                 text=False
                 ):
        super().__init__(iterable)
        MathDescendant.__init__(self, root_math_object, line_of_descent)

        if format_ not in ('lean', 'utf8', 'html'):
            raise ValueError("Wrong format_ type, must be one of 'lean', "
                             "'utf8', 'html'")
        self.format_ = format_
        self.text = text

        # For debugging:
        self.pattern = pattern
        self.pattern_dic = pattern_dic

    # def __str__(self):
    #     flat_list = [str(item) for item in self]
    #     return ''.join(flat_list)

    def set_root_math_object(self, math_object):
        self.root_math_object = math_object
        for item in self:
            if isinstance(item, MathString) or isinstance(item, MathList):
                item.set_root_math_object(math_object)

    def add_line_of_descent(self, line_of_descent):
        """
        Recursively add the line of descent to items of self.
        """

        self.line_of_descent = line_of_descent + self.line_of_descent
        for item in self:
            if isinstance(item, MathString) or isinstance(item, MathList):
                item.add_line_of_descent(line_of_descent)

    @property
    def lean_format(self):
        return self.format_ == "lean"

    def is_formatter(self):
        """
        True is self is a single term list with a formatter MathString,
        e.g. [[[r'\dummy_variable']]].
        """
        return len(self) == 1 and self[0].is_formatter()

    def is_marker(self):
        """
        True is self is a single term list with a marker MathString,
        e.g. [[['']]].
        """
        return len(self) == 1 and self[0].is_marker()

    def significant_items(self):
        """
        Return a list of all MathString in self or a sub-list which are not
        formatters.
        """

        items = []
        for item in self:
            items.extend(item.significant_items())

        return items

    def is_format_parenthesis(self):
        return len(self) == 1 and self[0].is_format_parenthesis()

    def remove_formatters(self):
        """
        Remove all formatters from self.
        """

        idx = 0
        while idx < len(self):
            new_item = self[idx].remove_formatters()
            if new_item is None:
                self.pop(idx)
            else:
                self[idx] = new_item
                idx += 1

        if len(self) > 0:  # Do not return empty list!
            return self

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
            new_math_str = MathString.replace_string(math_string, new_string)
            self[idx] = new_math_str
            return True

    def map(self, func):
        idx = 0
        for item in self:
            new_item = func(item)
            self[idx] = new_item

    def recursive_map(self, func: callable):
        """
        Here map is assumed to be a simple function str -> str,
        which is applied recursively on self. If func returns None for a
        given item then no replacement is done.
        """
        idx = 0
        for item in self:
            if isinstance(item, MathString):
                new_item = item.map(func)
                if new_item is not None:
                    self[idx] = new_item
            elif isinstance(item, MathList):
                item.recursive_map(func)
            else:
                log.warning(f"In MathList.recursive_map, item {idx} in {self}"
                            f"is neither MathString nor MathList")
            idx += 1

    def wrap(self, pre: MathString, post: MathString):
        """
        Add preamble and postamble.
        """
        self.insert(0, pre)
        self.append(post)

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
            assert len(self) > child_idx
            try:
                item = self[child_idx].item_for_address(further_descendant)
                return item
            except:  # FIXME
                log.warning(f"In MathList.item_for_address, item {child_idx}"
                            f"of {self} has no {further_descendant}")

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

    def first_descendant(self):
        if len(self) == 0:
            return
        elif isinstance(self[0], MathList):
            return self[0].first_descendant()
        else:
            return self[0]

    def parent_of_first_descendant(self):
        if len(self) == 0:
            return
        elif not isinstance(self[0], MathList):
            return self
        else:
            return self[0].parent_of_first_descendant()

    def last_descendant(self):
        if len(self) == 0:
            return
        elif isinstance(self[-1], MathList):
            return self[-1].last_descendant()
        else:
            return self[-1]

    def wrap_lean_shape_with_type(self, math_object):
        """
        Add type indication for Lean shape, if this is pertinent.
        Return a new tuple shape.
        """

        # lean_shape = list(lean_shape)

        if (math_object.node == 'NUMBER' and
                (math_object.math_type.is_number() or 
                 math_object.math_type.node == '*NUMBER_TYPES')):
            # wrap_shape = ['(', '('] + lean_shape + [') : ', lean_type, ')']
            lean_type = math_object.math_type.to_display(format_='lean')
            self.insert(0, MathString.left_paren)
            self.insert(0, MathString.left_paren)
            self.append(MathString.right_paren)
            self.append(MathString(": ", root_math_object=None))
            self.append(MathString(lean_type))
            self.append(MathString.right_paren)
            
    @classmethod
    def lean_shape(cls, math_object):
        """
        Shape for lean format. See the latex_shape() method doc.
        """
        shape = None
        for pattern, pre_shape, metavars in PatternInit.pattern_lean:
            # if pattern.node == 'LOCAL_CONSTANT' and len(pattern.children) == 3:
            #     print("debug")
            if pattern.match(math_object):
                # Now metavars are matched
                # log.debug(f"Matching pattern --> {pre_shape}")
                shape = tuple(substitute_metavars(item, metavars, pattern)
                              for item in pre_shape)
                break
        if not shape:
            if math_object.node in MathDisplay.lean_from_node:
                shape = list(MathDisplay.lean_from_node[math_object.node])

                shape = [
                    process_shape_macro(math_object, item) if isinstance(item, str)
                    else item for item in shape]
        if shape:
            # (3) Process macros
            if shape[0] == "global":
                shape = global_pre_shape_to_pre_shape(shape[1:])

            shape = MathList([process_shape_macro(math_object, item)
                             if isinstance(item, str)
                             else item for item in shape],
                             root_math_object=math_object)

            shape.wrap_lean_shape_with_type(math_object)

        return shape

    @classmethod
    def latex_shape(cls, math_object, is_type=False, text=False,
                    lean_format=False):
        """
        Return the unexpanded shape of self, e.g.
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

        if lean_format:
            shape = cls.lean_shape(math_object)
            if shape:  # Really, no more processing??
                return shape

        shape_math = MathList((), root_math_object=math_object,
                              format_="lean" if lean_format else "utf8",
                              text=text)

        # descendant = math_object.descendant(line_of_descent)

        # (0) Dictionaries to be used (order matters!):
        dicts = []
        if is_type:
            dicts.append(PatternInit.pattern_latex_for_type)
        if text:
            dicts.append(PatternInit.pattern_text)
        dicts.append(PatternInit.pattern_latex)

        # (1) Search for patterns
        for dic in dicts:
            for pattern, pre_shape, metavars in dic:
                if pattern.match(math_object):
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
            node = math_object.node
            if node in MathDisplay.latex_from_node:
                shape = list(MathDisplay.latex_from_node[node])
            else:
                shape = ["***"]  # Default

        # (3) Process macros
        if shape[0] == "global":
            shape = global_pre_shape_to_pre_shape(shape[1:], text=text)

        for item in shape:
            if isinstance(item, str):
                new_item = process_shape_macro(math_object, item)
                if isinstance(new_item, str):
                    if new_item in MathString.format_strings():
                        new_item = MathString.formatter(new_item)
                    else:
                        new_item = MathString(new_item,
                                              root_math_object=math_object)
                shape_math.append(new_item)
            else:
                shape_math.append(item)
        return shape_math

    def check_completeness(self) -> bool:
        """
        Recursively checks that self's items are MathString or MathLists.
        Change pure strings to MathStrings.
        Change [[]] to [].
        Add an empty MathString at vbeginning and end if and only if self has no
        non formatter MathString whose descendant is self.root_math_object.
        """

        # Remove useless nested lists [[]]
        if len(self) == 1 and isinstance(self[0], MathList):
            item = self.pop(0)
            item.check_completeness()
            self.extend(item)
            return True

        idx = 0
        root_appears_in_self = False
        for item in self:
            if isinstance(item, MathString):
                if item.descendant == self.root_math_object:
                    root_appears_in_self = True
            elif isinstance(item, str):
                self[idx] = MathString(item, root_math_object=None)
            elif isinstance(item, MathList):
                item.check_completeness()
            else:
                raise TypeError(f"Item {item} of a complete MathList"
                                f"should be either MathList or MathString,"
                                f"but is {type(item)}")
            idx += 1

        # FIXME
        # if not root_appears_in_self:
        #     log.warning(f"Root does not appear in {self}")
        #     marker = MathString('', root_math_object=self.root_math_object)
        #     self.insert(0, marker)
        #     self.append(marker)

    def expand_latex_shape(self):
        """
        Expand latex shape. The resulting self is a MathList whose items are
        either MathString or MathList with the same property.
        """
        self.recursive_expand_latex_shape()
        self.check_completeness()

    def recursive_expand_latex_shape(self,
                                     # root_math_object=None,
                                     # line_of_descent=None,
                                     text=None, lean_format=None):
        """
        Recursively replace each MathObject by its shape.
        tuples corresponds to children (or descendants) and are also replaced.
        Return a tree of string, structured by lists.
        """

        # Adjust self.line_of_descent and root_math_orbject!
        # if line_of_descent is not None:
        #     self.line_of_descent = line_of_descent
        # else:
        #     line_of_descent = self.line_of_descent
        #
        # if root_math_object is not None:
        #     self.root_math_object = root_math_object
        # else:
        #     root_math_object = self.root_math_object

        if text is None:
            text = self.text
        if lean_format is None:
            lean_format = self.lean_format

        idx = 0
        for item in self:
            new_item = process_shape_item(item, 
                                          root_math_object=self.root_math_object,
                                          line_of_descent=self.line_of_descent,
                                          text=text, lean_format=lean_format)
            self[idx] = new_item
            idx += 1

    def process_text(self):
        """
        Replace some symbols by plain text, or shorten some text:
        """

        text_depth = 100 if self.text else 0
        if not self.lean_format:
            shallow_latex_to_text(self, text_depth)

        self.check_completeness()

    def cut_spaces(self, previous_item=None):
        """
        Remove double spaces, within items or between successive items:
        if previous_item is not None then a leading space of first descendant of
        sel may be erased.
        """

        if len(self) == 0:
            return

        if not previous_item:
            self.recursive_map(cut_spaces)
            # previous_item = self.formatter("")
            previous_item = ""

        idx = 0
        for item in self:
            if isinstance(item, MathString):  # Immediately cut space
                new_string = cut_successive_spaces(previous_item, item)
                if new_string:
                    self.replace_string(idx, new_string)
            elif isinstance(item, MathList):  # Recursively cut spaces
                item.cut_spaces(previous_item)
            previous_item = item.last_descendant()
            idx += 1

    def linear_list(self, until=None, from_=None):
        """
        Return the linear MathList of self.
        If until is not None, then stop
        at first item equal to until (including until).
        If from_ is not None, then start at last item equal to from_ (
        excluding from_).
        """

        linear_list = MathList([], self.root_math_object,
                               format_=self.format_,
                               text=self.text)
        for item in self:
            if isinstance(item, MathList):
                linear_list.extend(item.linear_list())
            else:
                linear_list.append(item)
            if until and linear_list[-1] == until:
                break
            if from_ and linear_list[-1] == from_:
                linear_list = []

        return linear_list

    def descendants_with_nodes(self, until=None, from_=None):
        """
        Return the linear MathList of descendants of self.
        If until is not None, then stop
        at first item equal to until (including until, but NOT including ).
        If from_ is not None, then start at last item equal to from_ (
        excluding from_).

        Contrarily to the preceding method, this one includes nodes, if and
        only if they do not appear in their own sub-list.
        """

        linear_list = MathList([], self.root_math_object,
                               format_=self.format_,
                               text=self.text)
        include_self = True
        for item in self:
            if item.descendant == self.descendant:
                include_self = False
            if isinstance(item, MathList):
                linear_list.extend(item.linear_list())
            else:
                linear_list.append(item)
            if until and linear_list[-1] == until:
                include_self = False
                break
            if from_ and linear_list[-1] == from_:
                linear_list = []
                include_self = False

        if include_self:
            linear_list.append(self)

        return linear_list

    def to_string(self) -> str:
        """
        Concatenate self into an actual string.
        """
        for item in self:
            if not isinstance(item, MathList) and not isinstance(item,
                                                                 MathString):
                print("Bug")  # Fixme

        # flat_list = [item.to_string() for item in self]

        linear_list = self.linear_list()
        string = ''.join(linear_list)
        return string

    def mark(self):
        self.insert(0, MathString.marked_object)

    def adapt_to_format_(self, format_, use_color=True, bf=False,
                         no_text=False):
        """
        Adapt self to the format specified by self.format_.
        """

        display = None
        # (1) Replace latex macro by utf8/lean versions
        if format_ == 'lean':  # FIXME:
            self.recursive_map(MathDisplay.latex_to_lean)

        if format_ in ('lean', 'utf8', 'html'):  # Replace latex macro by utf8:
            self.recursive_map(MathDisplay.latex_to_utf8)
        else:
            raise ValueError(
                "Wrong format_ type, must be one of 'lean', 'utf8', "
                "'html'")
        # (2) Format
        if format_ == 'html':
            html_display(self, use_color=use_color, bf=bf, no_text=no_text)

        elif format_ == 'utf8' or format_ == 'lean':
            utf8_display(self)
        # elif format_ == 'lean':  # FIXME:
        #     display = lean_display(self)

        # Put here general hygiene, and remove to_string
        if format_ in ('utf8', 'html'):
            self.recursive_map(replace_dubious_characters)

        self.check_completeness()
        self.cut_spaces()

    @classmethod
    def complete_latex_shape(cls, math_object, format_="html", text=False,
                             use_color=True, bf=False, is_type=False,
                             used_in_proof=False):

        lean_format = (format_ == "lean")

        # !! Beware that the latex_shape() method is subclassed, e.g. in
        # MarkedPatternMathObject
        shape = math_object.latex_shape(is_type=is_type, text=text,
                                        lean_format=lean_format)

        if used_in_proof and not lean_format:
            # shape = [r'\used_property'] + shape
            shape.insert(0, MathString.formatter(r'\used_property'))

        # (2) Expand shape into a complete MathList
        shape.expand_latex_shape()

        # (3) Replace some symbols by plain text, or shorten some text:
        shape.process_text()

        # shape.adapt_to_format_(use_color=use_color, bf=bf)
        # (4) Format into a displayable string
        shape.adapt_to_format_(format_, use_color=use_color, bf=bf,
                               no_text=not text)

        return shape

    @classmethod
    def display(cls, math_object, format_="html", text=False,
                use_color=True, bf=False, is_type=False,
                used_in_proof=False) -> str:
        """
        Method to display MathObject on screen.
        Note that it cannot be put in MathObject module, due to import problem
        (namely: we need PatternMathObject to get the right shape to display).
        """

        # lean_format = (format_ == "lean")
        #
        # # (1) Find basic shape
        # shape = cls.latex_shape(math_object, is_type=is_type, text=text,
        #                         lean_format=lean_format)
        #
        # if used_in_proof and not lean_format:
        #     # shape = [r'\used_property'] + shape
        #     shape.insert(0, MathString.formatter(r'\used_property'))
        #
        # # (2) Expand shape into a complete MathList
        # shape.expand_latex_shape()
        #
        # # (3) Replace some symbols by plain text, or shorten some text:
        # shape.process_text()
        #
        # # (4) Format into a displayable string
        # shape.adapt_to_format_(format_, use_color=use_color, bf=bf,
        #                        no_text=not text)
        shape = cls.complete_latex_shape(math_object, format_, text, use_color,
                                         bf, is_type, used_in_proof)

        # (5) And joint everything!
        display = shape.to_string()

        return display


