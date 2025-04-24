"""
###########################################################
# __init__.py : __init__.py for deaduction.dui.primitives #
###########################################################

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
Date           : March 2021

Copyright (c) 2021 the dEAduction team

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

from .buttons_dialog      import ButtonsDialog
from .disclosure_dict import DisclosureDict
from .text_edit_logger    import TextEditLogger, TextEditLoggerHandler
from .yes_no_dialog       import YesNoDialog, DeaductionTutorialDialog
from .font_config         import deaduction_fonts
from .base_math_widgets_styling import (MathLabel, MathItem, MathTextWidget,
                                        GoalTextWidget, scale_geometry,
                                        ExerciseStatementWindow,)
from .disclosure_triangle import (DisclosureTriangle, DisclosureTitleWidget,
                                  DisclosureGroupBox)
from .rich_tool_button import RichTextToolButton


