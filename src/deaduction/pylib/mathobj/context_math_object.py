"""
# context_math_object.py : subclass MathObject for objects in the context #

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


from typing import Any, Tuple, Dict, Optional
import logging

import deaduction.pylib.config.vars as cvars

# from deaduction.pylib.text                  import use, prove
import deaduction.pylib.text.help_msgs as help_msgs
from deaduction.pylib.mathobj.math_object   import MathObject

log = logging.getLogger(__name__)
global _


class ContextMathObject(MathObject):
    """
    This class subclasses MathObject for objects of the context.
    At a given moment of a proof, the list of instances, as recorded in
    self.list_, is exactly the list of MathObjects in the current context.
    This list is useful for naming dummy vars.

    Attributes allow to keep track of some additional information.
    """
    list_: [Any] = []  # List of all ContextMathObject in the current context
    is_new_: bool  # True if self was not present in previous context FIXME
    is_modified_: bool  # True if self is modified from previous context FIXME
    is_hidden: bool  # True if self should not be dispplayed in ui
    has_been_used_in_the_proof: bool

    def __init__(self, node, info, children, bound_vars, math_type):
        super().__init__(node, info, children, bound_vars, math_type)

        ContextMathObject.list_.append(self)

        # Ancestor in logically previous context
        self.parent_context_math_object = None
        self.child_context_math_object = None

        # Tags
        self.is_new_ = False  # FIXME: obsolete
        self.is_modified_ = False  # FIXME: obsolete
        self.has_been_used_in_proof = False  # TODO: implement
        self.is_hidden = False # TODO
        # log.debug(f"Creating ContextMathPObject {self.to_display()},")
                  # f"dummy vars = "
                  # f"{[var.to_display() for var in self.bound_vars]}")

    @property
    def is_new(self):
        return self.parent_context_math_object is None

    @property
    def is_modified(self):
        return (self.parent_context_math_object
                and self.parent_context_math_object.math_type != self.math_type)

    def is_descendant_of(self, other):
        """
        True is self is a (strict) descendant of other.
        """
        parent = self.parent_context_math_object
        if parent:
            return parent == other or parent.is_descendant_of(other)

    @classmethod
    def whose_math_type_is(cls, math_type: MathObject):
        """
        Return the list of current ContextMathObjects with given math_type.
        """
        math_objects = [mo for mo in cls.list_ if mo.math_type == math_type]
        return math_objects

    def copy_tags(self, other):
        self.has_been_used_in_proof = other.has_been_used_in_proof
        self.is_hidden = other.is_hidden

    def remove_future_info(self):
        self.child_context_math_object = None

    def raw_latex_shape(self, negate=False, text_depth=0):
        """
        Replace the raw_latex_shape method for MathObject.
        """
        shape = super().raw_latex_shape(negate, text_depth)
        if (hasattr(self, 'has_been_used_in_proof')
                and self.has_been_used_in_proof):
            shape = [r'\used_property'] + shape
        return shape

    def raw_latex_shape_of_math_type(self, text_depth=0):
        """
        Replace the raw_latex_shape_of_math_type method for MathObject.
        """
        shape = super().raw_latex_shape_of_math_type(text_depth)
        if (hasattr(self, 'has_been_used_in_proof')
                and self.has_been_used_in_proof):
            shape = [r'\used_property'] + shape
        if self.is_function():
            # Should be "a function from" in text mode,
            # and nothing in symbol mode.
            shape[0] = r"\context_function_from"
        return shape

    @property
    def identifier(self):
        return self.info.get("id")

    def action_from_premise_and_operator(self, other: MathObject):
        """
        Return possible actions for premise = self and operator = other. This is
        used e.g. to determine which action could be triggered by a drag&drop
        operation.
        """
        operator = self
        premise = other
        action = None

        implicit = cvars.get("functionality.allow_implicit_use_of_definitions")
        if operator.is_function():
            action = "map"

        if premise.math_type.is_prop():
            if operator.can_be_used_for_implication(implicit=implicit):
                action = "implies"
            else:
                yes, subs = operator.can_be_used_for_substitution()
                if yes:
                    action = "equal"
        else:
            if operator.is_for_all(implicit=implicit):
                action = "forall"

        return action

    def check_unroll_definitions(self) -> []:
        """
        Return the definitions that match self.
        """
        definitions = MathObject.definitions
        math_type = self.math_type
        matching_defs = [defi for defi in definitions if defi.match(math_type)]
        return matching_defs

    def format_msg(self, raw_msg: str,
                   obj: Optional[MathObject] = None,
                   definitions=None,
                   format_="html") -> str:
        """
        Format msgs with parameters from self's children, and translate them.
        For now, works only with html format.
        obj is the implicit self, if an implicit definition should be applied.
        """

        params: Dict[str, str] = dict()

        if not obj:
            obj = self.math_type
        children = obj.children

        if children:
            ch0 = children[0]
            params['type_'] = ch0.to_display(format_=format_)
            params['ch0'] = ch0.to_display(format_=format_)
            params['ch0_type'] = ch0.math_type.to_display(format_=format_)
            if len(children) > 1:
                ch1 = children[1]
                params['ch1'] = ch1.to_display(format_=format_)
                # type_ = math_object.math_type_to_display(format_=format_,
                #                                          text_depth=10)
                params['an_element_of_type_'] = \
                    ch1.math_type_to_display(format_=format_, text_depth=10)
                params['every_element_of_type_'] = \
                    help_msgs.single_to_every(params['an_element_of_type_'])

        # Bounded quantification
        prop = obj.bounded_quantification(is_math_type = True)
        if prop and prop.node == "PROP_BELONGS":
            params['type_'] = prop.children[1]

        # Definitions names
        if definitions:
            params['def_name'] = f'"{definitions[0].pretty_name}"'
            if len(definitions) > 1:
                def_names = '", "'.join(defi.pretty_name
                                        for defi in definitions)
                params['def_names'] = '"' + def_names + '"'

        # Merge and translate dict
        format_dic = {**help_msgs.phrase, **help_msgs.prop_types}
        # Translate values
        translated_format_dic = {key: _(val)
                                 for key, val in format_dic.items()}
        # # Replace def_name in dict values...
        # formatted_format_dic = {key: val.format(**params)
        #                         for key, val in translated_format_dic.items()}

        translated_format_dic.update(params)

        translated_msg = _(raw_msg) if raw_msg else ""
        msg1 = translated_msg.format(**translated_format_dic)
        return msg1

    def help_definition(self, target=False) -> ((str, str, str), Any):

        msgs_dic = help_msgs.prove if target else help_msgs.use
        # msgs = ("", "", "")
        definitions = self.check_unroll_definitions()
        msgs = ([] if not definitions
                else msgs_dic["definition"] if len(definitions) == 1
                else msgs_dic["definitions"])
        definition_msgs = (self.format_msg(msg, definitions=definitions)
                           for msg in msgs)

        return definition_msgs

    # def help_implicit_def(self, obj, target=False) -> (Optional[Tuple[str, str,
    #                                                                   str]],
    #                                                    Optional[bool]):
    #     """
    #     Compute help msgs for the implicit definition obj.
    #     The bool output indicates if implicit def should be used or not when
    #     formatting with types, and so on.
    #     """
    #     msgs_dic = help_msgs.prove if target else help_msgs.use
    #     main_symbol = obj.main_symbol()
    #     implicit_def = MathObject.last_used_implicit_definition
    #     # Msg associated to main symbol:
    #     main_symbol_msgs = msgs_dic.get(main_symbol) if main_symbol else None
    #
    #     # # If self also has a msg associated to it (without unfolding implicit
    #     # # def), then we will show this one.
    #     # alt_main_symbol = self.math_type.main_symbol()
    #     # alt_main_symbol_msgs = (msgs_dic.get(alt_main_symbol) if
    #     #                         alt_main_symbol else None)
    #
    #     # Msg associated to unfolding definitions:
    #     def_msgs, definitions = self.help_definition(target=target)
    #
    #     if not (def_msgs and main_symbol_msgs):
    #         return None, None
    #
    #     # Msgs = "After unfolding def, this property is blabla"
    #     def_msg = tuple(def_msgs)[0] + " " + tuple(def_msgs)[1]
    #     # if not alt_main_symbol_msgs:
    #     implicit = True
    #     after_unfolding = _("After unfolding the definition {def_name}")
    #     after_unfolding = self.format_msg(after_unfolding,
    #                                       definitions=[implicit_def])
    #     msg_0 = (def_msg
    #              + "<br> <br>"
    #              + after_unfolding + ", "
    #              + main_symbol_msgs[0].lower())
    #     msg_1 = main_symbol_msgs[1]
    #     # else:
    #     #     implicit = False
    #     #     main_symbol_msgs = alt_main_symbol_msgs
    #     #     # msg_0 = def_msg + "<br> <br>" + main_symbol_msgs[0]
    #     #     msg_0 = main_symbol_msgs[0] + "<br> <br>" + main_symbol_msgs[1]
    #     #     msg_1 = def_msg
    #
    #     msgs = msg_0, msg_1, main_symbol_msgs[2]
    #
    #     return msgs, implicit

    def after_unfolding_implicit_def_msgs(self, target=False):
        """
        If an implicit definition applies, compute a msg that involving the
        main symbol of self after unfolding the implicit definition.
        """
        implicit = cvars.get("functionality.allow_implicit_use_of_definitions")
        obj = self.math_type
        implicit_defs = (self.math_type.unfold_implicit_definition()
                         if implicit else None)
        if not implicit_defs:
            return

        obj = implicit_defs[0]
        definition = MathObject.last_used_implicit_definition
        main_symbol = obj.main_symbol()
        msgs_dic = help_msgs.prove if target else help_msgs.use
        msgs = msgs_dic.get(main_symbol) if main_symbol else []
        main_symbol_msgs = []

        become = _("Applying definition {def_name} will turn this into")
        for msg in msgs:
            msg = msg.replace("{this_is}", become)
            msg = msg.replace("{this_property_is}", become)
            msg = self.format_msg(msg, obj=obj, definitions=[definition])
            main_symbol_msgs.append(msg)

        return main_symbol_msgs

    def help_msgs(self, target=False) -> [Optional[str]]:
        """
        Return help msgs for self as a target if target=True, and as a
        context object otherwise.
        """
        msgs_dic = help_msgs.prove if target else help_msgs.use

        # (1) Main symbol?
        main_symbol = self.math_type.main_symbol()
        msgs = msgs_dic.get(main_symbol) if main_symbol else []
        main_symbol_msgs = (self.format_msg(msg) for msg in msgs)

        # (2) Matching definitions?
        def_msgs = self.help_definition(target=target)

        # (3) Apply implicit definitions?
        implicit_msgs = self.after_unfolding_implicit_def_msgs(target=target)

        msgs_list = [main_symbol_msgs, def_msgs, implicit_msgs]
        final_msgs_list = []
        for msgs in msgs_list:
            if msgs:
                msgs = list(msgs)
                if msgs:
                    final_msgs_list.append(msgs)

        return final_msgs_list

    def help_target_msg(self, format_="html") -> (str, str, str):
        """
        Return three help msgs about self:
        - a general msg that describes self,
        - a msgs that explains how to use self in deaduction,
        - a (maybe empty) hint msg.
        Help msgs should depend on the main symbol of self, using implicit
        definition if they are allowed by the current settings.
        """
        return self.help_msgs(target=True)

    def help_context_msg(self, format_="html") -> (str, str, str):
        """
        Return three help msgs about self:
        - a general msg that describes self,
        - a msgs that explains how to use self in deaduction,
        - a (maybe empty) hint msg.
        Help msgs should depend on the main symbol of self, using implicit
        definition if they are allowed by the current settings.
        """
        return self.help_msgs(target=False)

