"""
###################################################
# proofs.py : provide lean code for proof buttons #
###################################################

Author(s)     : Marguerite Bin <bin.marguerite@gmail.com>
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 07 2020 (creation)
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

import logging
from sndhdr import whathdr
from typing import Union
from enum import IntEnum

from deaduction.pylib.text        import tooltips
# from deaduction.pylib.config.i18n import _
import deaduction.pylib.config.vars as cvars

from deaduction.pylib.actions.utils import pre_process_lean_code
from deaduction.pylib.actions.commun_actions import introduce_new_subgoal
from deaduction.pylib.actions import (InputType,
                                      MissingParametersError,
                                      MissingCalculatorOutput,
                                      CalculatorRequest,
                                      WrongUserInput,
                                      MissingJoker,
                                      action,
                                      CodeForLean,
                                      test_selection)
from deaduction.pylib.actions.logic import use_or

from deaduction.pylib.mathobj import MathObject
from deaduction.pylib.give_name import get_new_hyp, get_new_hyps

from deaduction.pylib.math_display.pattern_data import joker_name
from deaduction.pylib.math_display import new_objects, new_properties

log = logging.getLogger(__name__)
global _

# # Turn proof_button_texts into a dictionary
# proof_list = ['action_apply', 'proof_methods', 'new_object']
# lbt = tooltips.get('proof_button_texts').split(', ')
# proof_button_texts = {}
# for key, value in zip(proof_list, lbt):
#     proof_button_texts[key] = value


class ProofMethods:
    """
    An instanceless class for recording user input for the proof_methods action.
    The nb stored in user_input must refer to the complete list, not to the
    local list of available proof methods, so that it is not dependent on
    current settings.

    To add the new proof method blabla:
    add the function method_blabla() at the right place below with the
    @add_to_proof_methods decorator,
    update the pretty_names dict,
    (update the functionality.proof_methods list in config.toml).
    .
    """

    # Items may be added here, but order changes should be avoided
    # (or propagated). Order should not affect UI.
    # Nbs in user_input refer to index in this reference_list.
    # Name of callable must be 'method_' + <name in list>
    reference_list = ["case_based", "contraposition", "contradiction",
                      "sorry", "induction"]
    ordered_list = []
    callables = []

    @staticmethod
    def pretty_names(name):
        proof_methods_dic = {'case_based': _("Case-based reasoning"),
                             'contraposition': _("Proof by contraposition"),
                             'contradiction': _("Proof by contradiction"),
                             'induction': _("Proof by induction"),
                             'sorry': _("Admit current sub-goal!")}
        return proof_methods_dic[name]

    @classmethod
    def local_list(cls):
        """
        List of available proof methods in the current settings context.
        """
        proof_methods = cvars.get('functionality.proof_methods',
                                  default_value=cls.ordered_list)
        local_methods = [m for m in proof_methods
                         if cvars.get('functionality.allow_' + m)]

        return local_methods

    @classmethod
    def choices(cls):
        """
        Return the list of possible choices, as a parameter for the
        MissingParametersError exception.
        e.g.
                choices = [('1', _("Case-based reasoning")),
                   ('2', _("Proof by contraposition")),
                   ('3', _("Proof by contradiction"))]
        """

        l = cls.local_list()
        choices = [(str(idx), cls.pretty_names(l[idx]))
                   for idx in range(len(l))]
        return choices

    @classmethod
    def local_to_absolute_nb(cls, nb):
        """
        Convert the index in the local list to the index of the same item in
        the reference list, that should be stored in user_input.
        """
        name = cls.local_list()[nb]
        idx = cls.reference_list.index(name)
        return idx

    @classmethod
    def callable_method_from_name(cls, name):
        for cal in cls.callables:
            if cal.__name__.endswith(name):
                return cal

    @classmethod
    def callable_from_abs_nb(cls, nb):
        name = cls.reference_list[nb]
        return cls.callable_method_from_name(name)


def add_to_proof_methods() -> callable:
    """
    Decorator that add function to the ProofMethods lists.
    """
    
    def proof_method(func):
        if func not in ProofMethods.callables:
            name = func.__name__[len('method_'):]
            ProofMethods.ordered_list.append(name)
            ProofMethods.callables.append(func)
        return func

    return proof_method


@action()
def action_proof_methods(proof_step) -> CodeForLean:

    selected_objects = proof_step.selection
    # target_selected = proof_step.target_selected
    user_input = proof_step.user_input

    # proof_methods = cvars.get('functionality.proof_methods',
    #                           default_value=UserInput.default)

    # 1st call, choose proof method
    if not user_input:
        # choices = [('1', _("Case-based reasoning")),
        #            ('2', _("Proof by contraposition")),
        #            ('3', _("Proof by contradiction"))]
        # allow_proof_by_sorry = cvars.get('functionality.allow_proof_by_sorry')
        # if allow_proof_by_sorry:
        #     choices.append(('4', _("Admit current sub-goal!")))
        choices = ProofMethods.choices()
        raise MissingParametersError(InputType.Choice,
                                     choices,
                                     title=_("Proof methods"),
                                     output=_("Which proof method?"),
                                     converter=ProofMethods.local_to_absolute_nb
                                     )
    # 2nd call, call the adequate proof method. len(user_input) = 1.
    else:
        method = ProofMethods.callable_from_abs_nb(user_input[0])
        return method(proof_step, selected_objects, user_input)
        # method = int(user_input[0]) + 1
        # if method == 1:
        #     return method_case_based(proof_step, selected_objects, user_input)
        # if method == 2:
        #     return method_contraposition(proof_step, selected_objects)
        # if method == 3:
        #     return method_contradiction(proof_step, selected_objects)
        # if method == 4:
        #     return method_sorry(proof_step, selected_objects)


@add_to_proof_methods()
def method_case_based(proof_step,
                      selected_objects: [MathObject],
                      user_input=[]) -> CodeForLean:
    """
    Engage in a proof by cases.
    - If selection is empty, then ask the user to choose a property
    - If a disjunction is selected, use this disjunction for the proof by cases
    _ If anything else is selected try to discuss on this property
    (useful only in propositional calculus?)
    In any case, ask the user which case she wants to prove first.
    """

    if len(selected_objects) == 0:
        # NB: user_input[1] contains the needed property
        if len(user_input) == 1:
            # raise MissingParametersError(
            #      InputType.Text,
            #      title=_("cases"),
            #      output=_("Enter the property you want to discriminate on:")
            #                             )
            raise MissingCalculatorOutput(CalculatorRequest.ProofByCases,
                                          proof_step=proof_step)

            # raise MissingParametersError(InputType.Calculator,
            #                              title=_("Enter the property you want to discriminate on:"),
            #                              target=MathObject.PROP)

        else:
            # h0 = pre_process_lean_code(user_input[1])
            prop = user_input[1][0]
            h0 = (prop.to_display(format_='lean')
                  if isinstance(prop, MathObject) else prop)

            new_hyp_names = get_new_hyps(proof_step)
            h1 = new_hyp_names[0]
            h2 = new_hyp_names[1]
            code = CodeForLean.from_string(f"cases (classical.em ({h0})) "
                                           f"with {h1} {h2}")
            code.add_success_msg(_("Proof by cases"))
            code.add_disjunction(prop, h1, h2)  # Strings, not MathObject
    else:
        prop = selected_objects[0]
        if not prop.is_or():
            error = _("Selected property is not a disjunction")
            raise WrongUserInput(error)
        else:
            code = use_or(proof_step, selected_objects, user_input)

    return code


@add_to_proof_methods()
def method_contraposition(proof_step,
                          selected_objects: [MathObject],
                          user_input=None) -> CodeForLean:
    """
    If target is an implication, turn it to its contrapose.
    If a property P is selected, and target is Q, then assume (not Q) and
    change target to (not P).
    """

    target: MathObject = proof_step.goal.target

    if len(selected_objects) == 0:
        if target.is_implication():
            code = CodeForLean.from_string("contrapose")
            code.add_success_msg(_("Target replaced by contrapositive"))
            return code
        else:
            error = _('Proof by contraposition only applies when target is '
                      'an implication')
    elif len(selected_objects) == 1:
        prop: MathObject = selected_objects[0]
        if prop.math_type.is_prop():
            name = prop.info["name"]
            h = get_new_hyp(proof_step)
            code = CodeForLean.from_string(f"contrapose {name} with {h}")
            code.add_success_msg(_("Proof by contraposition with hypothesis "
                                   "{}").format(name))
            return code
        else:
            error = _("Selected object should be a property")
            raise WrongUserInput(error)
    else:
        error = _('There should be at most one selected property')
    raise WrongUserInput(error)


@add_to_proof_methods()
def method_contradiction(proof_step,
                         selected_objects: [MathObject],
                         user_input=None) -> CodeForLean:
    """
    If no selection, engage in a proof by contradiction.
    """
    if len(selected_objects) == 0:
        new_hypo = get_new_hyp(proof_step)
        code = CodeForLean.from_string(f'by_contradiction {new_hypo}')
        code.add_success_msg(_("Negation of target added to the context"))
        return code
    else:
        error = _('Proof by contradiction only applies to target')
    raise WrongUserInput(error)


@add_to_proof_methods()
def method_induction(proof_step,
                     selected_objects: [MathObject],
                     user_input=None) -> CodeForLean:
    """
    Try to do a proof by induction.
    """

    implicit = False
    target = proof_step.goal.target
    if not target.is_for_all(implicit=True):
        error = _("Proof by induction only applies to prove "
                  "a universal property '∀n∈ℕ, P(n)'")
        raise WrongUserInput(error)

    if not target.is_for_all(is_math_type=False):
        # Implicit "for all"
        implicit = True
        math_object = MathObject.last_rw_object
    else:
        math_object = target.math_type

    math_type, var, body = math_object.children
    if not var.is_nat():
        if not implicit:
            error = _(f"{var} is not a natural number") + ", " + \
                    _("proof by induction does not apply")
        raise WrongUserInput(error)

    var_name = proof_step.goal.provide_good_name(math_type,
                                                 var.preferred_letter())

    code = CodeForLean.empty_code()
    if len(user_input) < 2:
        choices = [('1', _('Base case')), ('2', _('Induction step'))]
        raise MissingParametersError(
            InputType.Choice,
            choices,
            title=_("Proof by induction"),
            output=_("Which property to prove first?"))
    elif user_input[1] == 0:
        code = CodeForLean.induction(var_name)
    elif user_input[1] == 1:
        code = CodeForLean.induction(var_name).and_then('rotate')

    return code


@add_to_proof_methods()
def method_sorry(proof_step,
                 selected_objects: [MathObject],
                 user_input=None) -> CodeForLean:
    """
    Close the current sub-goal by sending the 'sorry' code.
    """

    goals_nb = len(proof_step.proof_state.goals)
    if goals_nb == 1:
        error = _("This is pertinent only when there are several targets")
        raise WrongUserInput(error)
    else:
        return CodeForLean.from_string('sorry')


def introduce_fun(proof_step, selected_objects: [MathObject]) -> CodeForLean:
    """
    If a hypothesis of form ∀ a ∈ A, ∃ b ∈ B, P(a,b) has been previously
    selected: use the axiom of choice to introduce a new function f : A → B
    and add ∀ a ∈ A, P(a, f(a)) to the properties.
    """

    error = _('Select a property "∀ x, ∃ y, P(x,y)" to get a function')
    success = _("Function {} and property {} added to the context")
    if len(selected_objects) == 1:
        h = selected_objects[0].info["name"]
        # Finding expected math_type for the new function
        universal_property = selected_objects[0]
        if universal_property.is_for_all():
            source_type = universal_property.math_type.children[0]
            exist_property = universal_property.math_type.children[2]
            if exist_property.is_exists(is_math_type=True):
                target_type = exist_property.children[0]
                math_type = MathObject(node="FUNCTION",
                                       info={},
                                       children=[source_type, target_type],
                                       math_type=MathObject.NO_MATH_TYPE)

                hf = get_new_hyp(proof_step)
                name = proof_step.goal.provide_good_name(math_type)

                code = CodeForLean.from_string(f'cases '
                                               f'classical.axiom_of_choice '
                                               f'{h} with {name} {hf}, '
                                               f'dsimp at {hf}, '
                                               f'dsimp at {name}')
                code.add_error_msg(error)
                success = success.format(name, hf)
                code.add_success_msg(success)
                return code
    raise WrongUserInput(error)


@action()
def action_new_object(proof_step) -> CodeForLean:
    """
    Introduce new object / sub-goal / function
    """

    selected_objects = proof_step.selection
    # target_selected = proof_step.target_selected
    user_input = proof_step.user_input

    goal = proof_step.goal

    codes = CodeForLean()
    # Choose between object/sub-goal/function
    if not user_input:
        raise MissingParametersError(InputType.Choice,
                             [(_("Object"), _("Introduce a new object")),
                              (_("Goal"), _("Introduce a new "
                                            "intermediate sub-goal")),
                              (_("Function"), _("Introduce a new "
                                                "function"))],
                             title=_("New object"),
                             output=_("Choose what to introduce:"))
    # (1) Choice = new object
    if user_input[0] == 0:
        if len(user_input) == 1:  # Ask for name
            raise MissingParametersError(InputType.Text,
                                         title=_("New notation"),
                                         output=_("Choose a notation for your "
                                                  "new object:"))
        elif len(user_input) == 2:
            # Check name does not already exist
            name = pre_process_lean_code(user_input[1])
            names = [obj.display_name for obj in goal.context]
            if name in names:
                user_input.pop()
                output = _("This name already exists, please give a new name:")
                raise MissingParametersError(InputType.Text,
                                             title="New object",
                                             output=output)
            else:  # Ask for new object
                # output = new_objects
                new_name = user_input[1]
                raise MissingCalculatorOutput(CalculatorRequest.DefineObject,
                                              new_name=new_name,
                                              proof_step=proof_step)
        else:  # Send code
            name = pre_process_lean_code(user_input[1])
            new_hypo_name = get_new_hyp(proof_step, prefix='Def')

            # Process object from auto_step or from Calculator:
            math_object = user_input[2][0]

            new_object = math_object.to_display(format_='lean')
            codes = CodeForLean.from_string(f"let {name} := {new_object}")
            codes = codes.and_then(f"have {new_hypo_name} : {name} = "
                                                     f"{new_object}")
            codes = codes.and_then("refl")
            codes.add_success_msg(_("New object {} added to the context").
                                  format(name))
            if goal.target.is_for_all():
                # User might want to prove a universal property "∀x..."
                # and mistake "new object" for introduction of the relevant x.
                codes.add_error_msg(_("You might try the ∀ button..."))

    # (2) Choice = new sub-goal
    elif user_input[0] == 1:
        codes = introduce_new_subgoal(proof_step)

    # (3) Choice = new function
    elif user_input[0] == 2:
        return introduce_fun(proof_step, selected_objects)

    return codes


#########
# UTILS #
#########

def which_number_set(string: str):
    """
    Return 'ℕ', 'ℤ', 'ℚ', 'ℝ' if string represents a number, else None
    """
    ind = -1
    if '.' in string or '/' in string:
        ind = 2  # at least Q
    string = string.replace('.', '')
    string = string.replace('/', '')
    if not string.isdigit():
        return None
    else:
        return MathObject.NUMBER_SETS_LIST[ind]


def add_type_indication(item: Union[str, MathObject],
                        math_type: MathObject=None) -> Union[str, MathObject]:
    """
    Add type indication for Lean. e.g.
    '0' -> (0:ℝ)
    'x' -> (x:ℝ)
    :param item:        either a string (provided by user in TextDialog) or
    MathObject
    :param math_type:   math_type indication to add. If None, largest number
    set used in current context will be indicated
    :return: either     string or MathObject, with type indication in name
    """
    if math_type:
        number_type = math_type.which_number_set(is_math_type=True)
    if isinstance(item, str):
        number_set = which_number_set(item)
        if number_set and ':' not in item:
            if not math_type:
                MathObject.add_numbers_set(number_set)
                # Add type indication = largest set of numbers among used
                number_type = MathObject.number_sets[-1]
            item = f"({item}:{number_type})"  # e.g. (0:ℝ)
        return item
    else:
        if not math_type:
            number_type = MathObject.number_sets[-1]
        if hasattr(item, 'info'):
            name = item.display_name
            # Do not put 2 type indications!!
            if (':' not in name
                    and hasattr(item, 'info')):
                item.info['name'] = f"({name}:{number_type})"
        return item


@action()
def action_complete(proof_step,
                    complete_statement=False,
                    user_proves_statement=False,
                    statements_for_prover=None) -> CodeForLean:
    """
    This is called when user wants to fill in a context objects or the target
    which contains a joker. There are two exclusive cases:

    - Usr fills in a joker that she has introduced before. Then the proof
    should just go on.
    - Usr fills in a definition, or a statement, or formalizes a statement
    that should be checked by automatic solving the first time all jokers have
    been complete. Each joker should be equivalent to an equality asserted by
    an axiom called AXIOM<nb><name_of_joker>
    There should be three kind of response:
    - the statement has no meaning,
    - the statement has a meaning, but I am unable to check that it is correct,
    - OK.
    - Afterward usr will maybe have to prove the statement.

    To get the right error msg, we have to try successively
    - all joker declaration ("haves") + checking,
    - all but the last one + checking,
    and so on.
    If none of the above works, then some declaration is meaningless. Again,
    to know which one, we try successively
    - all declarations (with no checking)
    - all but one
    and so on.
    """

    # ---- (1) Handle selection ---- #
    selected_objects = proof_step.selection
    target_selected = proof_step.target_selected
    goal = proof_step.proof_state.goals[0]
    target = goal.target
    extended_selected_objects = (selected_objects + [target]
                                 if target_selected else selected_objects)
    # If no selection, select everything:
    if not extended_selected_objects:
        extended_selected_objects = goal.context + [target]

    user_input = proof_step.user_input

    # ---- (2) Check for jokers in selection ---- #
    # hypos_jokers_n_vars is a list with entries (hypo, [(joker, vars)] ) where
    # joker appears in hypo with variables vars
    # e.g. even n <=> lam n, JOKER n      --> variable = n
    hypos_jokers_n_vars = []
    hypos_with_jokers = []
    hypo_from_joker = dict()
    for cmo in extended_selected_objects:
        # FIXME: no math_type for context objects?
        jokers_n_vars = cmo.math_type.jokers_n_vars()
        if jokers_n_vars:
            hypos_jokers_n_vars.append((cmo, jokers_n_vars))
            hypos_with_jokers.append(cmo)
            # If cmo is "H1: delta = JOKER", hypo_from_joker[JOKER]=H1
            children = cmo.math_type.children
            if cmo.is_equality() and children[1].is_joker():
                hypo_from_joker[children[1].name] = cmo

    if not hypos_with_jokers:
        raise WrongUserInput(error=_("There is nothing to complete"))

    if not user_input:
        raise MissingJoker(proof_step=proof_step,
                           hypos_with_jokers=hypos_with_jokers)

    # ---- (3) Find jokers that have been assigned ---- #
    # print('Find completed jokers')
    completed_jokers = []
    usr_jokers = False  # True if assigned jokers are usr jokers
    for mpmo in user_input[0]:
        more_jokers = mpmo.search_in_name("JOKER")
        for joker in more_jokers:
            assigned_mo = joker.assigned_math_object
            if assigned_mo:
                completed_jokers.append(joker)
                if joker.is_usr_joker():
                    usr_jokers = True

    if not completed_jokers:
        raise WrongUserInput(error=_("No joker completed"))

    # print('Completed jokers:')
    # print([joker.to_display(format_='utf8') for joker in completed_jokers])

    # Check for illegal variables
    for joker in completed_jokers:
        cmo = hypo_from_joker.get(joker.metavar_name)
        # print(f"Looking for {joker.metavar_name} in {hypo_from_joker}")
        if not cmo:
            continue
        # context_math_object
        mo = joker.assigned_math_object
        cmo_var = cmo.math_type.children[0]
        joker_context = goal.context_at_birth(cmo_var)
        used_context = mo.local_constants_in()
        illegal_vars = [cmo for cmo in used_context if cmo not in joker_context]
        # DEBUG:
        # print("context at birth:")
        # print([v.to_display(format_='utf8') for v in joker_context])
        # print(f"Used context:")
        # print([v.to_display(format_='utf8') for v in used_context])
        # print(f"Used Illegal vars:")
        # print([v.to_display(format_='utf8') for v in illegal_vars])
        jname = cmo_var.to_display(format_='utf8')
        if jname in [var.to_display(format_='utf8') for var in used_context]:
            error = _("You cannot use {} to define {}!")
            error = error.format(jname, jname)
            raise WrongUserInput(error)
        elif illegal_vars:
            iv = " ".join(var.to_display(format_='utf8')
                          for var in illegal_vars)
            if len(illegal_vars) == 1:
                error = _("You cannot use variable {} to define {}, "
                          "since it did not exist when {} was created")
            else:
                error = _("You cannot use variables {} to define {}, "
                          "since they did not exist when {} was created")
            error = error.format(iv, jname, jname)
            raise WrongUserInput(error)

    # Find hypos containing this joker, and their variables
    variables = [[]]*len(completed_jokers)
    pertinent_hypos = [[]]*len(completed_jokers)
    idx = 0
    for completed_joker in completed_jokers:
        for hypo, jokers_n_vars in hypos_jokers_n_vars:
            for joker, vars_ in jokers_n_vars:
                if joker_name(joker) == completed_joker.metavar_name:
                    variables[idx] = vars_
                    pertinent_hypos[idx] = hypo
                    break
        idx += 1

    # ---- (4) Check variables ---- #
    # for joker, vars_ in zip(completed_jokers, variables):
    #     for var in vars_:
    #         # FIXME: this does not work because MMVAR.equal_to is used
    #         if not joker.contains(var):
    #             msg = _("Joker {} should use variable {}")
    #             raise WrongUserInput(error=msg.format(joker.name,
    #                                                   var.name))

    # ---- (5) Write Lean code ---- #
    # e.g. have HIDDEN0: HIDDENJOKER_0 = λ n, ∃ a, n = 2*a
    # Here vars = [n], joker.assigned_math_object = "∃ a, n = 2*a"
    hyp_names = get_new_hyps(proof_step,
                             prefix="HIDDEN",
                             nb=len(completed_jokers))

    # List of CodeForLeans respectively for
    # - declaration of jokers (as entered by usr via Calculator),
    # - checking completion is correct,
    # - rewriting hypos/goal using completion

    ##################################
    # ----- Case of usr_jokers ----- #
    ##################################
    # For usr joker we just assign the joker, there is nothing to check
    codes = []
    used_props = []
    msgs = []
    nb = 0
    if usr_jokers:
        for joker, __, hypo in zip(completed_jokers, variables,
                                   pertinent_hypos):
            # cmo is H_1: delta = USR_JOKER
            #  -> cmo_name = 'H_1', display_jkr_name = 'delta',
            #  joker_name = 'USR_JOKER', content = usr joker completion
            j_name = joker.metavar_name
            cmo = hypo_from_joker.get(j_name)
            cmo_name = cmo.display_name
            display_jkr_name = cmo.math_type.children[0]
            content = joker.assigned_math_object.to_display(format_="lean")

            more_codes = [f"clear {cmo_name} {j_name}",
                          f"have {cmo_name}: {display_jkr_name} = {content}",
                          "sorry",
                          f"rw {cmo_name} at *"]
            more_codes = CodeForLean.and_then_from_list(more_codes)

            # We could even clear these, but maybe this is more usr friendly
            used_props.append(cmo)
            codes.append(more_codes)
            msg = f"{cmo_var.to_display(format_='utf8')} = {content}"
            msgs.append(msg)
            nb += 1

        code = CodeForLean.and_then_from_list(codes)
        msg = _("Let us try ") + ", ".join(msgs)
        code.add_success_msg(msg)
        code.add_used_properties(used_props)
        return code

    ######################################
    # ----- Case of non usr jokers ----- #
    ######################################
    # For non usr jokers we assign and check
    # List of CodeForLeans respectively for
    # - declaration of usr joker completions,
    # - checking completion is correct,
    # - rewriting hypos/goal using completion

    # --- (5a) Compute elementary codes --- #
    have_codes = []
    at_hypos = []
    check_codes = []
    check_list = ["try{ext}",  # eliminate lambdas
                  "try{tautology}",
                  "try{simp only [not_and, not_or, not_not, not_forall, "
                  "not_exists, eq_iff_iff,not_imp_not]}"]
    rw_codes = []
    nb = 0
    have_codes_debug = []
    check_codes_debug = []
    for joker, vars_, hypo in zip(completed_jokers, variables, pertinent_hypos):
        name = joker.metavar_name
        vars_.reverse()
        var_names = [var.name for var in vars_]
        at_hypo = "" if hypo == target else f" at {hypo.name}"
        at_hypos.append(at_hypo)

        # Have code:
        content = joker.assigned_math_object.to_display(format_="lean")
        if vars_:
            content = "λ " + " ".join(var_names) + ", " + content
        hypo = hyp_names[nb]
        code_str = f"have {hypo}: {name} = {content}"
        have_code = CodeForLean.from_string(code_str)
        have_codes.append(have_code)
        have_codes_debug.append(code_str)

        # Check code: supposed to solve axiom_name = hypo as current goal
        # axiom_name = "AXIOM" + name, or "AXIOM0" + name, and so on
        try_rw_axioms = ["rw AXIOM" + name] + \
                        ["rw AXIOM" + str(idx) + name for idx in range(10)]

        # Successively try to solve with AXIOM n°<idx>:
        check_code = [CodeForLean.and_then_from_list([rw_axioms] +
                                                     check_list).solve1() 
                      for rw_axioms in try_rw_axioms]
        check_codes.append(CodeForLean.or_else_from_list(check_code))
        check_codes_debug.append(try_rw_axioms)
        # Rw code:
        rw_code = CodeForLean.and_then_from_list([f"rw {hypo}" + at_hypo,
                                                  "try{dsimp only"
                                                  f" {at_hypo}" + "}"])
                                                  # f"clear {hypo}"])
        rw_codes.append(rw_code)
        nb += 1

    # --- (5b) Combine elementary codes to check every possibilities --- #
    # e.g. [ [hc0, rotate, hc1, rotate, hc2, rotate, rotate],
    #        [hc0, rotate, hc1, rotate, rotate],
    #        [hc0] ]
    first_have_codes = []
    while have_codes:
        idx = 0
        more_codes = []
        for code in have_codes:
            more_codes.append(code)
            if idx < len(have_codes)-1:
                more_codes.append(CodeForLean.rotate())
            idx += 1
        if nb > 1:  # More than one completed joker
            more_codes.append(CodeForLean.rotate())
            more_codes.append(CodeForLean.rotate())
        first_have_codes.append(more_codes)
        have_codes.pop()

    first_check_codes = []  # e.g. [ [cc2, cc1, cc0], [cc1, cc0], [cc0] ]
    # print("Check codes:")
    # print(list(code.to_code() for code in check_codes))
    # check_codes.reverse()
    # print("Reversed check codes:")
    # print(code.to_code() for code in check_codes)
    while check_codes:
        # BEWARE, check_codes is a list of or_else codes:
        # We have to COPY them so that the or_else_code_nb works well.
        first_check_codes.append(list(code.copy() for code in check_codes))
        check_codes.pop(0)

    first_rw_codes = []  # e.g. [ [rwc0, rwc1, rwc2, sorry], [rwc0, rwc1],[rwc0] ]
    while rw_codes:
        first_rw_codes.append(rw_codes[:])
        rw_codes.pop()

    codes = []
    nb_jokers = len(completed_jokers)

    what_you_entered = (_("Your proposal") if nb_jokers == 0
                        else _("Everything you entered"))

    # ----- (5.c) Try successive declarations + correctness ----- #
    # (all, then all but the last one, and so on)
    # idx = nb_jokers-1
    idx = 0
    next_success_msg = what_you_entered + " " + _("is correct!")
    for have_codes, check_codes, rw_codes in zip(first_have_codes,
                                                 first_check_codes,
                                                 first_rw_codes):
        code = have_codes + check_codes + rw_codes
        more_code = CodeForLean.and_then_from_list(code)
        more_code.add_success_msg(next_success_msg)
        codes.append(more_code)
        # DEBUG:
        # print(f"Check codes n° {idx}")
        # for c in code:
        #     print("    " + c.to_code())
        # print("-->" + next_success_msg)
        # Write "success" msg (= failure of the next or_else!)
        if nb_jokers == 1:
            not_correct = _("it is not correct")
        else:
            at_hypo = at_hypos[idx]
            hypo = (f"hypothesis {at_hypo[3:]}" if at_hypo  # Remove 'at'
                    else "the goal")
            not_correct = hypo + _(" is not correct")
        next_success_msg = (what_you_entered + " " + _("is meaningful") + " "
                            + _(f"but I suspect") + " " + not_correct)
        idx += 1

    # ----- (5.d) Just try successive declarations ----- #
    idx = nb_jokers-1
    for have_codes, rw_codes in zip(first_have_codes, first_rw_codes):
        code_str = have_codes + ['todo']*(idx+1) + rw_codes
        more_code = CodeForLean.and_then_from_list(code_str)
        more_code.add_success_msg(next_success_msg)
        codes.append(more_code)

        # Write "success" msg (= failure of the next or_else!)
        if nb_jokers == 1:
            your_proposal = _("Your proposal")
        else:
            at_hypo = at_hypos[idx]
            hypo = (f"hypothesis {at_hypo[3:]}" if at_hypo  # Remove 'at'
                    else "the goal")
            your_proposal = _("Your proposal for") + " " + hypo
        next_success_msg = (your_proposal + " " + _("is not meaningful") + ", "
                            + _("maybe a syntax error?"))
        idx -= 1

    final_code = CodeForLean.or_else_from_list(codes)
    final_code.add_error_msg(next_success_msg)
    return final_code
