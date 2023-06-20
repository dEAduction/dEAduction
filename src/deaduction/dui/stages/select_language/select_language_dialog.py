"""
select_language_dialog.py : a function for selecting language
the first time deaduction is launched
    

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 07 2021 (creation)
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
import logging

from locale import getdefaultlocale
from PySide2.QtWidgets import   ( QApplication,
                                  QWidget,
                                  QInputDialog )

import deaduction.pylib.config.vars as cvars

PRETTY_NAMES = {"en": "English",
                'fr_FR': "Français"}

log = logging.getLogger(__name__)


def select_language():
    log.debug("Selecting language")
    available_languages = cvars.get("i18n.available_languages", ["en"])
    log.debug("Get default local:")
    language, font_enc = getdefaultlocale()
    log.debug(f"Language: {language}")
    # language = None
    if language in available_languages:
        log.debug(f"Found default language {language}")
        return language, True
    else:
        language, ok = 'en', True
    # elif language and len(language) >= 2:
    #     log.debug("Choosing language")
    #     for lang in available_languages:
    #         log.debug(f"Trying {lang}")
    #         if lang[:2] == language[:2]:
    #             return lang, True
    # pretty_languages_list = [PRETTY_NAMES[setting] if setting in PRETTY_NAMES
    #                          else setting for setting in available_languages]
    # # app = QApplication()  # Fixed: there is already one
    # parent = QWidget()
    # log.debug("Start Dialog:")
    # language, ok = QInputDialog.getItem(parent,
    #                                     "Select language",
    #                                     "Available languages:",
    #                                     pretty_languages_list,
    #                                     0,
    #                                     False)
    # for key in PRETTY_NAMES:
    #     if PRETTY_NAMES[key] == language:
    #         return key, ok

    return language, ok

