"""
# test_actions.py : test action files #

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 11 2020 (creation)
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

from deaduction.pylib.actions import CodeForLean


def test_CodeForLean():
    code = CodeForLean.from_string('assumption')
    code = code.or_else(CodeForLean.from_string('norm_num'))
    code = code.or_else(CodeForLean.from_string('good bye'))
    code = code.and_finally(CodeForLean.from_string('no_meta_vars'))
    assert code.to_string() == "{assumption, no_meta_vars} <|> " \
                               "{norm_num, no_meta_vars} <|> " \
                               "{good bye, no_meta_vars}"
    effective_code = code.add_trace_effective_code(42).to_string()
    assert effective_code == """{assumption, no_meta_vars, trace "EFFECTIVE CODE 42: assumption, no_meta_vars"} <|> {norm_num, no_meta_vars, trace "EFFECTIVE CODE 42: norm_num, no_meta_vars"} <|> {good bye, no_meta_vars, trace "EFFECTIVE CODE 42: good bye, no_meta_vars"}"""
