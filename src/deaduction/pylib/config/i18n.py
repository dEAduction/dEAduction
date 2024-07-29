"""
#########################################
# i18n.py : Internationalization helper #
#########################################

Author(s)      : - Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>

Maintainer(s)) : - Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>

Date           : October 2020

Copyright (c) 2020 the dEAduction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    d∃∀duction is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with d∃∀duction. If not, see <https://www.gnu.org/licenses/>.
"""

import gettext
import logging

import deaduction.pylib.config.vars      as cvars
import deaduction.pylib.config.dirs      as cdirs
import deaduction.pylib.utils.filesystem as fs

log = logging.getLogger(__name__)


def init_i18n():
    log.info("Init i18n")
    select_language     = cvars.get('i18n.select_language', "en")
    log.info(f"selected language     = {select_language}")

    # language_dir_path = fs.path_helper(cdirs.share / "locales")
    gettext.install('deaduction',
                    localedir=str(cdirs.language_dir_path))
    if select_language != "no_language":
        # 'no_language' is gotten first time deaduction is launched
        language = gettext.translation('deaduction',
                                       localedir=str(cdirs.language_dir_path),
                                       languages=[select_language],
                                       fallback=True)
        language.install()

    return select_language


# FIXME: better init management
init_i18n()

