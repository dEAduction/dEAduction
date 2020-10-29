"""
# __init__.py : load config files

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 10 2020 (creation)
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

from .config import config, user_config, EXERCISE, COURSE, SESSION
from .set_language import _
import deaduction.config.tooltips as tooltips

config['DEFAULT'].update(tooltips.__tooltips)
config['DEFAULT'].update(tooltips.__tooltips_apply)
config['DEFAULT'].update(tooltips.__buttons)



#########
# tests #
#########
if __name__ == "__main__":
    # boolean = user_config.getboolean('fold_statements')
    # text_boolean = user_config.get('fold_statements')
    # print(boolean, text_boolean)

    #####################
    # Print config file #
    #####################
    for sect in config.sections():
        print('Section:', sect)
        for k, v in config.items(sect):
            print(f' {k} = {v}')