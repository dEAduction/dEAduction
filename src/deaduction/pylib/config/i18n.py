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

# _ = None

log = logging.getLogger(__name__)


def init_i18n():
    # global _
    log.info("Init i18n")
    available_languages = cvars.get("i18n.available_languages", "en")
    select_language     = cvars.get('i18n.select_language', "en")

    log.info(f"available_languages = {available_languages}")
    log.info(f"select_language     = {select_language}")

    language_dir_path   = fs.path_helper(cdirs.share / "locales")
    gettext.install('deaduction',
                    localedir=str(language_dir_path))
    language = gettext.translation('deaduction',
                                   localedir=str(language_dir_path),
                                   languages=[select_language],
                                   fallback=True)
    language.install()


# def update_language():
#     select_language     = cvars.get('i18n.select_language', "en")
#     language_dir_path   = fs.path_helper(cdirs.share / "locales")
#     available_languages = cvars.get("i18n.available_languages")
#
#     # log.info(f"available_languages = {available_languages}")
#     # log.info("Language updated: ")
#     # log.info(f"select_language     = {select_language}")
#
#     if select_language == 'no_language':
#         # This should not happen except first time deaduction is launched...
#         select_language = 'en'
#         cvars.set('i18n.select_language', 'en')
#
#     if select_language == 'en':
#         log.info("(no translation)")
#         # No translation needed
#         def _(message):
#             return
#         _ = gettext.gettext
#     #     new_translator = lambda x: x
#     else:
#         new_language = gettext.translation('deaduction',
#                                            localedir=str(language_dir_path),
#                                            languages=[select_language])
#         new_language.install()
#         _ = new_language.gettext
#     return _


# FIXME: better init management
# _ = update()
init_i18n()
