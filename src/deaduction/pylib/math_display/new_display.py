
from deaduction.pylib.mathobj import MathObject, ContextMathObject
from deaduction.pylib.math_display.display_data import (latex_from_node,
                                                        latex_from_quant_node)
from deaduction.pylib.math_display.pattern_data import pattern_latex_pairs
from deaduction.pylib.math_display.display import abstract_string_to_string
from deaduction.pylib.math_display.display_math import shallow_latex_to_text


latex_from_node.update(latex_from_quant_node)


def latex_shape(self: MathObject) -> []:
    """
    Return the shape of self, e.g.
            [r'\forall', 1, r'\subset', 0, 2]
    where 0, 1, 2 are replaced by pertinent MathObjects.
    """

    # FIXME: keep item nb, e.g.  (item, metavars[item].matched_math_object)
    #  for parentheses?
    # (1) Difficult cases: patterns
    for pattern, pre_shape, metavars in pattern_latex_pairs:
        if pattern.match(self):
            # Now metavars are matched
            shape = [metavars[item].matched_math_object  # int for metavars
                     if isinstance(item, int)
                     else self.descendant(item)  # tuple for children/descendant
                     if isinstance(item, tuple)
                     else item  # str for str
                     for item in pre_shape]
            return shape

    # (2) Generic case: in latex_from_node
    if self.node in latex_from_node:
        pre_shape = list(latex_from_node[self.node])
        shape = [self.descendant(item) if isinstance(item, int)
                 else item for item in pre_shape]
        return shape

    return ["***"]


def expanded_latex_shape(math_object=None, shape=None):
    """
    Recursively replace each MathObject by its shape.
    """
    # TODO: compare recursive_display
    # if self.is_variable(is_math_type=True) or self.is_bound_var:
    #     return self

    if not shape:
        shape = latex_shape(math_object)

    # Expand first item
    new_item = "***"
    item = shape[0]
    if isinstance(item, str):
        new_item = item
    elif isinstance(item, MathObject):
        new_item = expanded_latex_shape(math_object=item)
        # TODO: add parentheses
        # # Between parentheses?
        # if needs_paren(math_object, child, item):
        #     display_item = [r'\parentheses', display_item]

    elif isinstance(item, tuple) or isinstance(item, int):
        child = math_object.descendant(item)
        new_item = expanded_latex_shape(math_object=child)
    elif callable(item):
        new_item = item(math_object)
    elif isinstance(item, list):
        # We have to pass the math_object, in case the list contains
        # references to math_object's children or descendant
        new_item = expanded_latex_shape(math_object=math_object,
                                        shape=item)

    # Expand the remaining of shape
    more_shape = (expanded_latex_shape(math_object=math_object,
                                       shape=shape[1:])
                  if len(shape) > 1 else [])
    expanded_shape = [new_item] + more_shape
    return expanded_shape


def to_display(self: MathObject, format_="html", text=False,
               use_color=True, bf=False) -> str:
    """
    """

    # (1) Compute shape
    abstract_string = expanded_latex_shape(math_object=self)

    # (3) Replace some symbols by plain text, or shorten some text:
    text_depth = 100 if text else 0
    abstract_string = shallow_latex_to_text(abstract_string, text_depth)

    # (4) Format into a displayable string
    display = abstract_string_to_string(abstract_string, format_,
                                        use_color=use_color, bf=bf,
                                        no_text=(text_depth <= 0))

    return display


def math_type_to_display(self, format_="html",
                         text=False,
                         is_math_type=False,
                         used_in_proof=False) -> str:
    return self.math_type.to_display(format_, text=text)


MathObject.to_display = to_display

MathObject.math_type_to_display = math_type_to_display

