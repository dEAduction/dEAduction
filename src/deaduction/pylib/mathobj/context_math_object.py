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
from deaduction.pylib.math_display.display_data import single_to_every
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
    is_new_: bool  # True if self was not present in previous context
    is_modified_: bool  # True if self is modified from previous context
    is_hidden: bool  # True if self should not be displayed in ui
    has_been_used_in_the_proof: bool
    allow_auto_action_: bool = True

    invisible_name_list = ["RealSubGroup"]

    def __init__(self, node, info, children, math_type):
        super().__init__(node, info, children, math_type)

        ContextMathObject.list_.append(self)

        # Ancestor in logically previous context
        self.parent_context_math_object = None
        self.child_context_math_object = None

        # Tags
        self.has_been_used_in_proof = False
        self.is_hidden = (self.name in self.invisible_name_list
                          or self.name.startswith("_inst_"))

    def __repr__(self):
        return self.debug_repr('CMO')

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

    def display_with_type(self, format_='html'):
        used_in_proof = self.has_been_used_in_proof
        lean_name = self.to_display(format_=format_)
        math_expr = self.math_type_to_display(format_=format_,
                                              used_in_proof=used_in_proof)
        test_expr = self.math_type_to_display(format_='utf8')
        separator = '' if test_expr.startswith(':') else ': '
        caption   = f'{lean_name} {separator}{math_expr}'
        return caption

    @property
    def identifier(self):
        return self.info.get("id")

    def is_potential_type(self):
        """
        True if self may be the type of some MathObject.        
        """
        # FIXME: be more subtle
        if self.is_type(is_math_type=True):
            return True
        
        elif cvars.get('display.use_set_name_as_hint_for_naming_elements') \
                and self.node == 'SET':
            return True

        else:
            return False

    @property
    def allow_auto_action(self):
        """
        False iff allow_auto_action_ is False for self or one of its
        ancestor, else True.
        """
        if self.allow_auto_action_ is False:
            return False
        else:
            parent: ContextMathObject = self.parent_context_math_object
            if parent:
                return parent.allow_auto_action
            else:
                return True

    def turn_off_auto_action(self):
        self.allow_auto_action_ = False

    #####################
    # Help msgs methods #
    #####################
    def action_from_premise_and_operator(self, other: MathObject,
                                         button_names: [str] = None) -> [str]:
        """
        Return possible actions for premise = self and operator = other. This is
        used e.g. to determine which action could be triggered by a drag&drop
        operation.
        """
        operator = self
        premise = other
        actions = []

        implicit = cvars.get("functionality.allow_implicit_use_of_definitions")
        if operator.is_function():
            actions.append("map")

        if premise.math_type.is_prop():
            if operator.can_be_used_for_implication(implicit=implicit):
                actions.append("implies_use")
            yes, subs = operator.can_be_used_for_substitution()
            if yes:
                actions.append("equal")
        if operator.is_for_all(implicit=implicit):
            actions.append("forall_use")

        if button_names:
            actions = [action for action in actions if action in button_names]
        return actions

    def format_msg(self, raw_msg: str,
                   obj: Optional[MathObject] = None,
                   definitions=None,
                   solving_obj=None,
                   on_target=False,
                   format_="html") -> str:
        """
        Format msgs with parameters from self's children, and translate them.
        For now, works only with html format.

        obj is the implicit self, if an implicit definition should be applied.
        definitions is the list of definitions that can be applied.

        The dictionary params is used to display appropriate text versions of
        math objects.
        """

        params: Dict[str, str] = dict()
        params['solving_obj'] = solving_obj
        from deaduction.pylib.math_display import plural_types
        if not obj:
            obj = self.math_type
        children = obj.children

        # Compute text for some pertinent math objects
        if children:
            ch0 = children[0]
            params['type_'] = ch0.to_display(format_=format_)
            params['ch0'] = ch0.to_display(format_=format_)
            # params['ch0_type'] = ch0.math_type.to_display(format_=format_)
            ch0_type = ch0.math_type_to_display(format_=format_,
                                                text=True)
            utf8 = ch0.math_type_to_display(format_='utf8', text=True)
            plural_type = plural_types(ch0_type, utf8)
            params['elements_of_ch0_type'] = (plural_type if plural_type else
                                              _('elements of') + ' ' + ch0_type)
            if len(children) > 1:
                ch1 = children[1]
                params['ch1'] = ch1.to_display(format_=format_)
                # type_ = math_object.math_type_to_display(format_=format_,
                #                                          text_depth=10)
                params['an_element_of_type_'] = \
                    ch1.math_type_to_display(format_=format_, text=True)
                params['every_element_of_type_'] = \
                    single_to_every(params['an_element_of_type_'])

        # Bounded quantification?
        real_type = obj.bounded_quant_real_type(is_math_type=True)
        if real_type:
            params['type_'] = real_type
            params['an_element_of_type_'] = \
                real_type.math_type_to_display(format_=format_, text=True,
                                               is_math_type=True)
            params['every_element_of_type_'] = \
                single_to_every(params['an_element_of_type_'])

        # Definitions names
        if definitions:
            params['def_name'] = f'"{definitions[0].pretty_name}"'
            if len(definitions) > 1:
                def_names = '", "'.join(defi.pretty_name
                                        for defi in definitions)
                params['def_names'] = '"' + def_names + '"'

        # Mention drag and drop (or not)
        format_dic = {**help_msgs.phrase}  # Copy to not alter original dic
        drag_to_context = cvars.get('functionality.drag_and_drop_in_context')
        drag_to_def = cvars.get('functionality.drag_context_to_statements')
        no_drag = dict()
        if not drag_to_context:
            no_drag.update({"or_drag_element_to_property": "",
                            "or_drag_to_function": "",
                            "or_drag_to_equality": "",
                            "or_drag_premise": ""})

        if not drag_to_def:
            no_drag.update({"or_drag_to_def": ""})

        if on_target:  # TODO: make target draggable...
            no_drag.update({"or_drag_to_def": "",
                            "or_drag_element_to_property": "",
                            "or_drag_to_function": "",
                            "or_drag_to_equality": "",
                            "or_drag_premise": ""})
        format_dic.update(no_drag)

        # Name of action buttons according to current prove/use mode
        cbn = help_msgs.current_button_name
        prove_use_dic = {key+suffix: cbn(key+suffix)
                         for key in ('forall', 'exists', 'implies', 'and', 'or')
                         for suffix in ('_prove', '_use')}
        format_dic.update(prove_use_dic)

        # Translate values
        translated_format_dic = {key: help_msgs.conc_n_trans(val) if val
                                 else val for key, val in format_dic.items()}

        # Merge dic
        translated_format_dic.update(**params, **help_msgs.prop_types)

        # Translate msgs, then substitute with translated_format_dic
        # translated_msg = _(raw_msg) if raw_msg else ""
        msg1 = raw_msg.format(**translated_format_dic)
        return msg1

    def help_definition(self, target=False, math_obj=None) -> (str, str, str):
        """
        Try to match all defs on math_obj, and compute a help msg in case of
        success.
        """
        def get_help_msgs(key):
            return help_msgs.get_help_msgs(key, target)
        if not math_obj:
            math_obj = self.math_type
        definitions = math_obj.check_unroll_definitions(is_math_type=True)

        definition_msgs = []
        if definitions:
            msgs = ([] if not definitions
                    else get_help_msgs("definition" if len(definitions) == 1
                                       else "definitions"))
            definition_msgs = [self.format_msg(msg, obj=math_obj,
                                               definitions=definitions,
                                               on_target=target)
                               for msg in msgs]

        elif math_obj.is_not(is_math_type=True):
            prop = math_obj.body_of_negation()
            if prop:
                definition_msgs = self.help_definition(target=target,
                                                       math_obj=prop)

        return definition_msgs

    def after_unfolding_implicit_def_msgs(self, target=False):
        """
        If an implicit definition applies, compute a msg that involving the
        main symbol of self after unfolding the implicit definition.
        """
        def get_help_msgs(key):
            return help_msgs.get_help_msgs(key, target)

        implicit = cvars.get("functionality.allow_implicit_use_of_definitions")
        implicit_objs = (self.math_type.unfold_implicit_definition()
                         if implicit else None)
        if not implicit_objs:
            return

        obj = implicit_objs[0]
        definition = MathObject.last_used_implicit_definition
        main_symbol = obj.main_symbol()
        # msgs_dic = help_msgs.prove if target else help_msgs.use
        msgs = get_help_msgs(main_symbol)
        main_symbol_msgs = []

        # fake = _("Applying definition {def_name} will turn this into")
        # become = _("Applying definition {def_name} will turn this into")
        for msg in msgs:
            msg = help_msgs.make_implicit(msg)
            msg = self.format_msg(msg, obj=obj, definitions=[definition],
                                  on_target=target)
            main_symbol_msgs.append(msg)

        return main_symbol_msgs

    def solving_msgs(self, solving_obj, on_target=False):
        msgs = help_msgs.get_help_msgs('goal!', on_target)
        return list(self.format_msg(msg, solving_obj=solving_obj,
                                    on_target=on_target) for msg in msgs)

    def help_main_symbol(self, on_target=False):

        # msgs_dic = help_msgs.prove if target else help_msgs.use
        def get_help_msgs(key):
            return help_msgs.get_help_msgs(key, on_target)

        main_symbol = self.math_type.main_symbol()

        if main_symbol == "not":
            prop = self.math_type.body_of_negation()
            if prop and not prop.is_simplifiable_body_of_neg(is_math_type=True):
                main_symbol = "not_non_pushable"

        msgs = get_help_msgs(main_symbol)
        main_symbol_msgs = (self.format_msg(msg, on_target=on_target)
                            for msg in msgs)

        return main_symbol_msgs

    def help_msgs(self, on_target=False) -> [Optional[str]]:
        """
        Return help msgs for self as a target if target=True, and as a
        context object otherwise.
        """
        # # msgs_dic = help_msgs.prove if target else help_msgs.use
        # def get_help_msgs(key):
        #     return help_msgs.get_helm_msgs(key, on_target)

        # (1) Main symbol?
        main_symbol_msgs = self.help_main_symbol(on_target)

        # (2) Matching definitions?
        def_msgs = self.help_definition(target=on_target)

        # (3) Apply implicit definitions?
        implicit_msgs = self.after_unfolding_implicit_def_msgs(target=on_target)

        msgs_list = [main_symbol_msgs, def_msgs, implicit_msgs]
        final_msgs_list = []
        for msgs in msgs_list:
            if msgs:
                msgs = list(msgs)
                if msgs:
                    final_msgs_list.append(msgs)

        return final_msgs_list

    def help_target_msg(self, context_solving=None,
                        format_="html") -> (str, str, str):
        """
        Return a list of triples of msgs. Each triple contains three help msgs
        about self:
        - a general msg that describes self,
        - a msgs that explains what to do with self in deaduction,
        - a hint msg.
        Help msgs should depend on the main symbol of self, using implicit
        definition if they are allowed by the current settings.
        """
        msgs = self.help_msgs(on_target=True)
        if context_solving:
            solving_msgs = self.solving_msgs(context_solving[0], on_target=True)
            msgs.insert(0, solving_msgs)
        return msgs

    def help_context_msg(self, context_solving=None,
                         format_="html") -> (str, str, str):
        """
        Return a list of triples of msgs. Each triple contains three help msgs
        about self:
        - a general msg that describes self,
        - a msgs that explains what to do with self in deaduction,
        - a hint msg.
        Help msgs should depend on the main symbol of self, using implicit
        definition if they are allowed by the current settings.
        """
        msgs = self.help_msgs(on_target=False)
        if context_solving and context_solving[0] == self:
            solving_msgs = self.solving_msgs(context_solving[0],
                                             on_target=False)
            msgs.insert(0, solving_msgs)
        return msgs

    def to_lean_with_type(self) -> str:
        """
        Return object in Lean format with type, e.g.
        'x: X'.
        This string should be put between parentheses.
        """
        term = self.to_display(format_='lean')
        type_ = self.math_type.to_display(format_='lean')
        s = f"{term}: {type_}"
        return s

