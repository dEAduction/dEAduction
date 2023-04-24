"""
#############################################
# __init__.py : for deaduction.dui.elements #
#############################################

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

from .actions_widgets_classes import (
    ActionButton,
    DemoUseModeSetter,
    ActionButtonsWidget,
    StatementsTreeWidgetNode,
    StatementsTreeWidgetItem,
    StatementsTreeWidget)

from .context_widgets_classes import (
    TargetLabel,
    MathObjectWidget,
    MathObjectWidgetItem,
    TargetWidget)

from .html_list_view import HTMLDelegate

from .lean_editor import (
    LeanEditor)

from .menubar import (
    MenuBar,
    MenuBarAction,
    MenuBarMenu)

from .recent_courses_widgets import (
    RecentCoursesLW,
    RecentCoursesLWI)

from .config_window import ConfigMainWindow

from .proof_outline_widget import ProofOutlineWindow

from .proof_tree import ProofTreeController

from .help import HelpWindow
