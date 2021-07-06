"""
# generic.py : # Contain actions the graphic interface has to call #
# when the user selects a definition or a theorem                  #
    
    (#optionalLongDescription)

Author(s)     : Marguerite Bin bin.marguerite@gmail.com
Maintainer(s) : Marguerite Bin bin.marguerite@gmail.com
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

# from deaduction.pylib.config.i18n import _
from deaduction.pylib.actions import (  WrongUserInput,
                                        CodeForLean,
                                        test_selection)
from deaduction.pylib.mathobj import (  Goal,
                                        MathObject,
                                        get_new_hyp)


def rw_using_statement(goal: Goal, selected_objects: [MathObject],
                       statement) -> CodeForLean:
    """
    Return codes trying to use statement for rewriting. This should be
    reserved to iff or equalities. This function is called by
    action_definition, and by action_theorem in case the theorem is an iff
    statement.
    """
    codes = CodeForLean.empty_code()

    defi = statement.lean_name

    if len(selected_objects) == 0:
        target_msg = _('definition applied to target') \
            if statement.is_definition() else _('theorem applied to target') \
            if statement.is_theorem() else _('exercise applied to target')
        codes = codes.or_else(f'rw {defi}')
        codes = codes.or_else(f'simp_rw {defi}')
        codes = codes.or_else(f'rw <- {defi}')
        codes = codes.or_else(f'simp_rw <- {defi}')
        codes.add_success_msg(target_msg)
    else:
        names = [item.info['name'] for item in selected_objects]
        arguments = ' '.join(names)
        context_msg = _('definition applied to') \
            if statement.is_definition() else _('theorem applied to') \
            if statement.is_theorem() else _('exercise applied to')
        context_msg += ' ' + arguments
        codes = codes.or_else(f'rw {defi} at {arguments}')
        codes = codes.or_else(f'simp_rw {defi} at {arguments}')
        codes = codes.or_else(f'rw <- {defi} at {arguments}')
        codes = codes.or_else(f'simp_rw <- {defi} at {arguments}')
        codes.add_success_msg(context_msg)

    return codes


def action_definition(proof_step,
                      selected_objects: [MathObject],
                      definition,
                      target_selected: bool = True
                      ):
    """
    Apply definition to rewrite selected object or target.
    """

    test_selection(selected_objects, target_selected)

    codes = rw_using_statement(proof_step.goal, selected_objects, definition)
    codes.add_error_msg(_("unable to apply definition"))
    return codes


def action_theorem(proof_step,
                   selected_objects: [MathObject],
                   theorem,
                   target_selected: bool = True
                   ):
    """
    Apply theorem on selected objects or target.
    """

    # test_selection(selected_objects, target_selected)

    # TODO: For an iff statement, use rewriting
    #  test for iff or equality is removed since it works only with
    #  pkl files

    goal = proof_step.goal

    codes = rw_using_statement(goal, selected_objects, theorem)

    h = get_new_hyp(proof_step)
    th = theorem.lean_name
    if len(selected_objects) == 0:
        codes = codes.or_else(f'apply {th}',
                              success_msg=_('theorem applied to target'))
        codes = codes.or_else(f'have {h} := @{th}',
                              success_msg=_('theorem added to the context'))
    else:
        command = f'have {h} := {th}'
        command_implicit = f'have {h} := @{th}'
        names = [item.info['name'] for item in selected_objects]
        arguments = ' '.join(names)
        # up to 4 implicit arguments
        more_codes = [f'apply {th} {arguments}',
                      f'apply @{th} {arguments}']
        more_codes += [command + arguments,
                       command_implicit + arguments,
                       command + ' _ ' + arguments,
                       command_implicit + ' _ ' + arguments,
                       command + ' _ _ ' + arguments,
                       command_implicit + ' _ _ ' + arguments,
                       command + ' _ _ _ ' + arguments,
                       command_implicit + ' _ _ _ ' + arguments,
                       command + ' _ _ _ _ ' + arguments,
                       command_implicit + ' _ _ _ _ ' + arguments
                       ]
        more_codes = CodeForLean.or_else_from_list(more_codes)
        context_msg = _('theorem') + ' ' + _('applied to') + ' ' + arguments
        more_codes.add_success_msg(context_msg)
        codes = codes.or_else(more_codes)

        codes.add_error_msg(_("unable to apply theorem"))

    return codes
