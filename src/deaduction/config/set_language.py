"""
# set_language.py : set language and translation

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
import gettext
from pathlib import Path

from .config import user_config

import deaduction.pylib.config.dirs as cdirs
import deaduction.pylib.utils.filesystem as fs

################
# Set language #
################
available_languages = user_config.get('available_languages')
available_languages = available_languages.split(', ')
select_language = user_config.get('select_language')

if available_languages == '':
    available_languages = ['en']
if select_language == '':
    select_language = 'en'

#language_dir_path = Path.cwd() / 'share/locales'
language_dir_path = fs.path_helper(cdirs.share / "locales")

#gettext.bindtextdomain("deaduction", str(language_dir_path))
#gettext.textdomain("deaduction")
language = gettext.translation('deaduction',
                         localedir=str(language_dir_path),
                         languages=[select_language])
language.install()
_ = language.gettext
