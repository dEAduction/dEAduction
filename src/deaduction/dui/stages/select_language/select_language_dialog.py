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
from locale import getdefaultlocale
from PySide2.QtWidgets import   ( QApplication,
                                  QWidget,
                                  QInputDialog )

import deaduction.pylib.config.vars as cvars

PRETTY_NAMES = {"en": "English",
                'fr_FR': "Français"}


def select_language():
    available_languages = cvars.get("i18n.available_languages", ["en"])
    language, font_enc = getdefaultlocale()
    if language in available_languages:
        return language, True
    else:
        for lang in available_languages:
            if lang[:2] == language[:2]:
                return lang, True
    pretty_languages_list = [PRETTY_NAMES[setting] if setting in PRETTY_NAMES
                             else setting for setting in available_languages]
    app = QApplication()
    parent = QWidget()

    language, ok = QInputDialog.getItem(parent,
                                    "Select language",
                                    "Available languages:",
                                    pretty_languages_list,
                                    0,
                                    False)
    for key in PRETTY_NAMES:
        if PRETTY_NAMES[key] == language:
            return key, ok

    return language, ok

