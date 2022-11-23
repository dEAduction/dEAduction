
import logging

from deaduction.pylib.mathobj import MathObject, ContextMathObject
from deaduction.pylib.pattern_math_obj import PatternMathObject
from deaduction.pylib.math_display.display_data import (latex_from_node,
                                                        latex_from_quant_node,
                                                        needs_paren)
from deaduction.pylib.math_display.pattern_data import (pattern_latex,
                                                        pattern_text,
                                                        pattern_latex_for_type)
from deaduction.pylib.math_display.display import abstract_string_to_string
from deaduction.pylib.math_display.display_math import (shallow_latex_to_text,
                                                        latex_to_text_func)

log = logging.getLogger(__name__)

latex_from_node.update(latex_from_quant_node)


def global_pre_shape_to_pre_shape(pre_shape, text=False):
    """
    Turn a global pre_shape, e.g.
        ("global", r"\forall {} \subset {}, ", 0, (0, 0), 1),
    into a "normal" pre_shape, e.g.
        (r"\forall", 0, r" \subset ", (0, 0), ", ", 1),
    (or, in text mode,
        ("for every subsets ", 0, " of ", (0,0), ", ", 1).
    )
    """
    gps = list(pre_shape)
    words = gps.pop(0)
    if text:  # Try to convert into text
        words, success = latex_to_text_func(words)
    words = words.split("{}")
    vars_ = gps
    pre_shape = []

    # Intercaler les mots et les variables:
    while words:
        pre_shape.append(words.pop(0))
        if vars_:
            pre_shape.append(vars_.pop(0))

    return pre_shape


def latex_shape(self: MathObject, is_type=False, text=False) -> []:
    """
    Return the shape of self, e.g.
            [r'\forall', 1, r'\subset', 0, 2]
    where 0, 1, 2 are replaced by pertinent MathObjects.

    If is_type is True, then pattern is first looked for in the
    pattern_latex_for_type list. This should be used for math_types of
    context objects.

    If text is True, then the pattern_text list is used first.

    Here we make as few substitution as possible, namely we only substitute
    metavars and not children or descendant, since descendant nb are useful
    to add appropriate parentheses.
    """

    #  REMOVE the sequence/set_families methods

    # Dictionaries to be used (order matters!):
    dicts = []
    if not isinstance(self, PatternMathObject):
        if is_type:
            dicts.append(pattern_latex_for_type)
        if text:
            dicts.append(pattern_text)
        dicts.append(pattern_latex)

    # (1) Difficult cases: patterns
    for dic in dicts:
        for pattern, pre_shape, metavars in dic:
            if pattern.match(self):
                # DEBUG
                if r'\circ' in pre_shape:
                    print('compo')
                log.debug(f"Matched pattern--> shape {pre_shape}")
                log.debug(f"Node: {self.node}")
                # Now metavars are matched
                if pre_shape[0] == "global":
                    pre_shape = global_pre_shape_to_pre_shape(pre_shape[1:],
                                                              text=text)
                shape = [metavars[item].matched_math_object  # int for metavars
                         if isinstance(item, int)
                         # NO substitution here: DO NOT uncomment the following
                         # else self.descendant(item)
                         # if isinstance(item, tuple)
                         else item  # str for str
                         for item in pre_shape]
                return shape

    # (2) Generic case: node
    if self.node in latex_from_node:
        shape = list(latex_from_node[self.node])
        # NO substitution here: DO NOT uncomment the following
        # shape = [self.descendant(item) if isinstance(item, int)
        #          else item for item in pre_shape]
        return shape

    return ["***"]


def expanded_latex_shape(math_object=None, shape=None, text=False):
    """
    Recursively replace each MathObject by its shape.
    """
    # TODO: compare recursive_display
    # if self.is_variable(is_math_type=True) or self.is_bound_var:
    #     return self

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
               use_color=True, bf=False, is_type=False) -> str:
    """
    """

    # (1) Compute expanded shape
    shape = latex_shape(self, is_type=is_type, text=text)
    abstract_string = expanded_latex_shape(math_object=self, shape=shape,
                                           text=text)

    log.debug(f"Abstract string: {abstract_string}")
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

    return math_type.to_display(format_, text=text, is_type=True)


MathObject.to_display = to_display

MathObject.math_type_to_display = math_type_to_display

