"""
############################################################
# exceptions.py : functions to call in order to            #
# translate actions into lean code                         #
############################################################
    
Every function action_* takes 2 arguments,
- goal (of class Goal)
- a list of ProofStatePO precedently selected by the user
and returns lean code as a string

Author(s)     : - Marguerite Bin <bin.marguerite@gmail.com>
Maintainer(s) : - Marguerite Bin <bin.marguerite@gmail.com>
Created       : July 2020 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

This file is part of dEAduction.

    dEAduction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    dEAduction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

from enum                         import IntEnum
import deaduction.pylib.config.vars as cvars

global _


class InputType(IntEnum):
    """
    Class clarifying the type of missing parameter.
    """
    Text = 0
    Choice = 1
    YesNo = 2
    Calculator = 3


class MissingParametersError(Exception):
    def __init__(self, input_type: InputType, choices=None, title="", output="",
                 converter=lambda n: n, target=None):
        """

        @param input_type: Text, Choice (in a list), YesNo, Calculator (
        obsolete)
        @param choices: list of (text) choices
        @param title: title of the window QDialog
        @param output: text of the question
        @param converter: 
        @param target: (for calculator)
        """
        self.input_type         = input_type
        self.choices            = choices
        self.title              = title
        self.output             = output
        self.local_to_complete_nb = converter
        self.input_target = target


class CalculatorRequest(IntEnum):
    """
    Class clarifying th type of request to the Calculator.
    """
    ApplyProperty = 0
    ApplyStatement = 1
    ProveExists = 2
    StateSubGoal = 3
    DefineObject = 4
    EnterObject = 5


class MissingCalculatorOutput(MissingParametersError):
    """
    Any instance should provide enough info so that, together with the goal,
    Calculator is able to construct the CalculatorTargets.

    Individual target titles are provided when there is a detailed context,
    i.e. request_type is one of
    ApplyProperty, ApplyStatement, ProveExists.
    These are provided by the targets_types_n_titles() method.
    """
    MathObject = None  # filled in by Coordinator

    def __init__(self, request_type: CalculatorRequest,
                 proof_step,
                 prop=None,
                 statement=None,
                 new_name=None,
                 object_of_requested_math_type=None):
        """

        @param request_type:
        @param proof_step:
        @param prop: a ContextMathObject (use prop.math_type).
        @param statement:
        @param new_name: name for a new object
        @param requested_type: type of object to enter
        """
        super().__init__(input_type=InputType.Calculator)
        self.request_type = request_type
        self.proof_step = proof_step
        self.initial_place_holders = []
        self.prop = prop
        self.statement = statement
        self.name = new_name
        self.object_of_requested_math_type = object_of_requested_math_type

        if self.request_type is CalculatorRequest.ApplyProperty:
            # self.prop = prop
            self.title = _("Apply a universal context property")
        elif self.request_type is CalculatorRequest.ApplyStatement:
            # self.statement = statement
            self.title = _("Apply a universal statement")
        elif self.request_type is CalculatorRequest.ProveExists:
            self.prop = prop if prop else proof_step.goal.target.math_type
            self.title = _("Provide a witness for an existential property")
        elif self.request_type is CalculatorRequest.DefineObject:
            # self.name = new_name  # Object name
            self.title = _("Introduce the new object {}").format(new_name)
        elif self.request_type is CalculatorRequest.StateSubGoal:
            self.title = _("Introduce a new sub-goal")
        elif self.request_type is CalculatorRequest.EnterObject:
            self.title = _("Define an object")

    def task_title(self):
        if self.request_type is CalculatorRequest.ApplyProperty:
            title = _("Apply the universal context property:")
        elif self.request_type is CalculatorRequest.ApplyStatement:
            title = _("Apply the universal statement:")
        elif self.request_type is CalculatorRequest.ProveExists:
            title = _("Provide a witness for the existential property:")
        elif self.request_type is CalculatorRequest.StateSubGoal:
            title = _("State a new sub-goal:")
        elif self.request_type is CalculatorRequest.DefineObject:
            title = _("Introduce a new object: {} = ?").format(self.name)
        elif self.request_type is CalculatorRequest.EnterObject:
            if self.request_type and self.object_of_requested_math_type:
                mo = self.object_of_requested_math_type
                object_type = (mo.math_type_to_display(format_='html',
                                                       text=True))
                title = _("Enter {}:").format(object_type)
            else:
                title = _("Enter an object:")
        else:
            title = None
        return title

    def target_type(self):
        """
        Determine type of target when there is only one target,
        with no detailed context to show (e.g. enter an object).
        """
        if self.object_of_requested_math_type:
            # e.g. CalculatorRequest.EnterObject
            return self.object_of_requested_math_type.math_type
        elif self.request_type is CalculatorRequest.StateSubGoal:
            return self.MathObject.PROP

    def explicit_math_type_of_prop(self):
        """
        Return prop.math_type, or its explicit version if it ias an implicit
        universal prop.
        """
        if self.prop and self.prop.math_type:
            return self.prop.math_type.explicit_quant()

    def extract_types_n_vars(self):

        # (1) Get all initial universal dummy vars
        if self.request_type is CalculatorRequest.ApplyProperty:
            math_object = self.prop.math_type
        elif self.request_type is CalculatorRequest.ApplyStatement:
            math_object = self.statement.to_math_object()
        else:
            return []
        types_n_vars = math_object.types_n_vars_of_univ_prop()
        if not types_n_vars:
            return None
        # if not types_n_vars:  # Include implicit vars if no explicit var
        #     types_n_vars = math_object.types_n_vars_of_univ_prop(
        #         include_initial_implicit_vars=True)

        # (2) replace initial vars by place_holders if they can be inferred
        #  from the following ones
        # TODO: option from settings to keep implicit vars
        #  (in this case, skip the following)
        idx = 0
        self.initial_place_holders = []
        for math_type, var in types_n_vars:
            go_on = False
            for other_type, v in types_n_vars[idx:]:
                # Search for var
                if (other_type.contains_including_types(var) or
                        var.is_instance()):
                    # Replace var by a place_holder
                    types_n_vars[idx] = math_type, math_object.place_holder()
                    self.initial_place_holders.append(
                        self.MathObject.place_holder())
                    go_on = True
                    break
            if not go_on:
                break
            idx += 1

        return types_n_vars

    def targets_types_n_titles(self):
        types = []
        titles = []
        if self.request_type in (CalculatorRequest.EnterObject,
                                 CalculatorRequest.StateSubGoal,
                                 CalculatorRequest.DefineObject):
            types = [self.target_type()]
            titles = []  # No individual title

        if self.request_type in (CalculatorRequest.ApplyProperty,
                                 CalculatorRequest.ApplyStatement):
            types_n_vars = self.extract_types_n_vars()
            for math_type, var in types_n_vars:
                if var and var.is_place_holder():  # Remove place_holders
                    # title = 'PLACE_HOLDER'
                    continue
                elif var:
                    name = var.to_display(format_='html')
                    title = _("Which object plays the role of {}?").format(name)
                else:
                    title = _("To which object shall we apply this property?")
                types.append(math_type)
                titles.append(title)
        if self.request_type is CalculatorRequest.ProveExists:
            target = self.prop.math_type
            explicit_type = target.explicit_quant()
            if explicit_type:
                math_type, var, body = explicit_type.children
                types = [math_type]
                name = var.to_display(format_='html')
                title = _("Which object plays the role of {}?").format(name)
                titles = [title]

        return types, titles

    # def task_description(self):
    #     """
    #     Provide a display of self.prop or self.statement after
    #     unfolding definition to reveal quantifiers if necessary.
    #     """
    #
    #     # FIXME: not really used?
    #     task = None
    #     if self.request_type in (CalculatorRequest.ApplyProperty,
    #                              CalculatorRequest.ProveExists):
    #         math_obj = self.prop.math_type.explicit_quant()
    #         task = math_obj.to_display(format_='html')
    #     elif self.request_type is CalculatorRequest.ApplyStatement:
    #         math_obj = self.statement.to_math_object().explicit_quant()
    #         task = math_obj.to_display(format_='html')
    #     return task


class WrongUserInput(Exception):
    def __init__(self, error=""):
        super().__init__(f"Wrong user input with error: {error}")
        self.message = error


class WrongProveModeInput(WrongUserInput):
    def __init__(self, error="", prop=None):
        super().__init__(f"Wrong 'prove' user input with error: {error}")
        if not prop:
            prop = _("a property")
        if not error:
            if cvars.get("logic.button_use_or_prove_mode") == "display_switch":
                error = _("Go into 'use mode' to make use of {} of "
                          "the context").format(prop)
            else:
                error = _("Press the 'use' button to make use of {} of "
                          "the context").format(prop)
        self.message = error


class WrongUseModeInput(WrongUserInput):
    def __init__(self, error="", prop=None):
        super().__init__(f"Wrong 'use' user input with error: {error}")
        if not prop:
            prop = _("the goal")
        if not error:
            if cvars.get("logic.button_use_or_prove_mode") == "display_switch":
                error = _("Go into 'prove mode' to prove {}").format(prop)
            else:
                error = _("Press the 'prove' button to prove {}").format(prop)
        self.message = error


class SelectDefaultTarget(Exception):
    def __init__(self):
        super().__init__("Selecting target")


def test_selection(items_selected: [],
                   selected_target: bool,
                   exclusive=False,
                   select_default_target=True,
                   force_default_target=False):
    """
    Test that at least one of items_selected or selected_target is not empty.
    If exclusive is True, then also test that both are not simultaneously
    nonempty. In case nothing is selected and both the "target selected by
    default" setting and the arg select_default_target are True, then
    raise the SelectDefaultTarget exception.
    """
    # implicit_target = cvars.get("functionality.target_selected_by_default")

    if not (items_selected or selected_target):
        settings = cvars.get('functionality.target_selected_by_default')
        if force_default_target or (select_default_target and settings):
            raise SelectDefaultTarget
        else:
            error = _("Select at least one object, one property or the target")
            raise WrongUserInput(error)

    if exclusive and items_selected and selected_target:
        error = _("I do not know what to do with this selection")
        raise WrongUserInput(error)


def test_prove_use(selected_objects, demo, use, prop):
    """
    Raise an exception if nb of selected_objects does not fit use/demo mode.
    @param selected_objects:
    @param demo: True iff demo mode is on
    @param use: True iff use mode is on
    @param prop: the type of property
    """
    if not selected_objects and not demo:
        raise WrongUseModeInput(prop=prop)
    elif selected_objects and not use:
        raise WrongProveModeInput(prop=prop)


