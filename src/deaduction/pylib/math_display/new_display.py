
from typing import Union
import logging

from deaduction.pylib.mathobj import MathObject, ContextMathObject
from deaduction.pylib.pattern_math_obj import PatternMathObject
from deaduction.pylib.math_display.display_data import (latex_from_node,
                                                        latex_from_quant_node,
                                                        needs_paren)
from deaduction.pylib.math_display.pattern_init import (pattern_latex,
                                                        pattern_text,
                                                        pattern_latex_for_type)
from deaduction.pylib.math_display.display import abstract_string_to_string
from deaduction.pylib.math_display.display_math import (shallow_latex_to_text,
                                                        latex_to_text_func)

log = logging.getLogger(__name__)

latex_from_node.update(latex_from_quant_node)


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

    # index = shape_item.find('.')
    # if index == -1:
    #     return shape_item
    #
    # root, attribute = shape_item[:index], shape_item[index+1:]

    attributes = shape_item.split('.')
    # if len(attributes) == 1:
    #     return shape_item

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


def substitute_metavars(shape, metavars, self):
    """
    Recursively substitute int by the corresponding metavars in shape.
    """
    if isinstance(shape, int):
        item = shape
        return metavars[item].matched_math_object
    elif isinstance(shape, list):
        return list(substitute_metavars(item, metavars, self) for item in shape)
    else:  # e.g. str, MathObject
        return shape


def latex_shape(self: MathObject, is_type=False, text=False) -> []:
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

    if self.node == "QUANT_∀":
        # print("app")
        pass

    # (0) Dictionaries to be used (order matters!):
    dicts = []
    if not isinstance(self, PatternMathObject):
        if is_type:
            dicts.append(pattern_latex_for_type)
        if text:
            dicts.append(pattern_text)
        dicts.append(pattern_latex)

    # (1) Search for patterns
    for dic in dicts:
        for pattern, pre_shape, metavars in dic:
            # if self.node == "QUANT_∀" and pre_shape[0] == r'\forall':
            #     print("(debug))")
            if pattern.match(self):
                # Now metavars are matched
                # log.debug(f"Matching pattern --> {pre_shape}")
                shape = tuple(substitute_metavars(item, metavars, self)
                              for item in pre_shape)
                break
        if shape:
            break

    # (2) Generic cases: use only node
    if not shape:
        if self.node in latex_from_node:
            shape = list(latex_from_node[self.node])
        else:
            shape = ["***"]  # Default

    # (3) Process macros
    if shape[0] == "global":
        shape = global_pre_shape_to_pre_shape(shape[1:], text=text)

    shape = [process_shape_macro(self, item) if isinstance(item, str)
             else item for item in shape]

    return shape


def expanded_latex_shape(math_object=None, shape=None, text=False):
    """
    Recursively replace each MathObject by its shape.
    tuples corresponds to children (or descendants) and are also replaced.
    """
    # TODO: compare recursive_display
    # if self.is_variable(is_math_type=True) or self.is_bound_var:
    #     return self

    if hasattr(math_object, 'matched_math_object'):
        if math_object.matched_math_object:
            return expanded_latex_shape(math_object.matched_math_object,
                                        shape, text)

    if not shape:
        shape = latex_shape(math_object, text=text)
    if shape[0] == r'\no_text':
        text = False
        shape.pop(0)

    #####################
    # Expand first item #
    #####################
    new_item = "***"
    item = shape[0]
    if isinstance(item, str):
        new_item = item
    elif isinstance(item, MathObject):
        new_item = expanded_latex_shape(math_object=item, text=text)
        # TODO: add parentheses
        # # Between parentheses?
        # if needs_paren(math_object, child, item):
        #     display_item = [r'\parentheses', display_item]

    elif isinstance(item, tuple) or isinstance(item, int):
        child = math_object.descendant(item)
        new_item = expanded_latex_shape(math_object=child, text=text)
        if needs_paren(math_object, child, item):
            new_item = [r'\parentheses', new_item]
    elif callable(item):
        new_item = item(math_object)
    elif isinstance(item, list):
        # We have to pass the math_object, in case the list contains
        # references to math_object's children or descendant
        new_item = expanded_latex_shape(math_object=math_object,
                                        shape=item,
                                        text=text)

    #################################
    # Expand the remaining of shape #
    #################################
    more_shape = (expanded_latex_shape(math_object=math_object,
                                       shape=shape[1:],
                                       text=text)
                  if len(shape) > 1 else [])
    expanded_shape = [new_item] + more_shape

    return expanded_shape


def to_display(self: MathObject, format_="html", text=False,
               use_color=True, bf=False, is_type=False,
               used_in_proof=False) -> str:
    """
    Method to display MathObject on screen.
    Note that it cannot be put in MathObject module, due to import problem
    (namely: we need PatternMathObject to get the right shape to display).
    """

    # (1) Compute expanded shape
    shape = latex_shape(self, is_type=is_type, text=text)
    if used_in_proof:
        shape = [r'\used_property'] + shape
    abstract_string = expanded_latex_shape(math_object=self, shape=shape,
                                           text=text)

    # log.debug(f"Abstract string: {abstract_string}")
    # (3) Replace some symbols by plain text, or shorten some text:
    text_depth = 100 if text else 0
    abstract_string = shallow_latex_to_text(abstract_string, text_depth)

    # (4) Format into a displayable string
    display = abstract_string_to_string(abstract_string, format_,
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

MathObject.math_type_to_display = math_type_to_display

