"""
base_math_widgets_styling.py : provide the MathLabel, MathItem and
MathTextWidget classes that takes care of html stylesheet.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 12 2023 (creation)
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
from PySide2.QtWidgets import (QCheckBox,
                               QHBoxLayout, QLabel, QVBoxLayout,
                               QWidget, QStackedLayout)

from deaduction.dui.primitives      import (MathTextWidget)
from .context_widgets_classes        import (MathObjectWidget,
                                             TargetLabel)

log = logging.getLogger(__name__)
global _


class GoalTextWidget(MathTextWidget):
    """
    A MathTextWidget to display a goal in text mode. This can be a statement,
    an exercise (to_prove=True), or an open question.
    This used in StartCoEx, and in CalculatorTargets.
    """
    def __init__(self, goal=None, math_object=None,
                 to_prove=False, open_problem=False,
                 apply_statement=False):
        super().__init__()
        self.setReadOnly(True)

        if goal:
            text = goal.goal_to_text(format_="html",
                                     text_mode=True,
                                     to_prove=to_prove,
                                     open_problem=open_problem,
                                     apply_statement=apply_statement)
        elif math_object:
            text = math_object.to_display(format_="html", text=True)

            # Capitalize:
            utf8 = math_object.to_display(format_='utf8', text=True)
            first_word = utf8.split()[0]
            text = text.replace(first_word, first_word.capitalize(), 1)
        else:
            raise ValueError("GoalTextWidget needs either a goal or a "
                             "math_object")

        self.setHtml(text)


class GoalMathWidget(QWidget):
    """
    A QWidget to display a goal in math mode. Objects, properties and target
    are displayed in distinct QMathWidgets.
    """

    def __init__(self, goal, to_prove=False, open_problem=False):
        super().__init__()
        target = goal.target
        objects = goal.context_objects
        properties = goal.context_props

        # ───────────── Objects and properties ───────────── #
        propobj_lyt = QHBoxLayout()
        objects_wgt = MathObjectWidget(objects, use_boldface=False)
        properties_wgt = MathObjectWidget(properties, use_boldface=False)
        objects_lyt = QVBoxLayout()
        properties_lyt = QVBoxLayout()

        # Math font
        objects_wgt.adjustSize()
        # objects_wgt.setFont(self.math_fonts)
        properties_wgt.adjustSize()
        # properties_wgt.setFont(self.math_fonts)

        objects_lyt.addWidget(QLabel(_('Objects:')))
        properties_lyt.addWidget(QLabel(_('Properties:')))
        objects_lyt.addWidget(objects_wgt)
        properties_lyt.addWidget(properties_wgt)
        propobj_lyt.addLayout(objects_lyt)
        propobj_lyt.addLayout(properties_lyt)

        # ───────────────────── Target ───────────────────── #
        # target_wgt = MathObjectWidget(target=target)
        target_wgt = TargetLabel(target)
        # target_wgt.setFont(self.math_fonts)
        # Set target_wgt height to 1 line: USELESS with QLabel
        # font_metrics = QFontMetrics(math_font)
        # text_size = font_metrics.size(0, target.math_type_to_display())
        # text_height = text_size.height() * 2  # Need to tweak
        # target_wgt.setMaximumHeight(text_height)

        friendly_wgt_lyt = QVBoxLayout()
        friendly_wgt_lyt.addLayout(propobj_lyt)
        target_title = (_("True or False:") if open_problem
                        else _("Target:") if to_prove
                        else _("Conclusion"))
        friendly_wgt_lyt.addWidget(QLabel(target_title))

        friendly_wgt_lyt.addWidget(target_wgt)
        self.setLayout(friendly_wgt_lyt)
        friendly_wgt_lyt.setContentsMargins(0, 0, 0, 0)

    def set_goal(self, goal, to_prove=False, open_problem=False):
        # TODO
        target = goal.target
        objects = goal.context_objects
        properties = goal.context_props


class GoalWidget(QWidget):
    """
    A class to display a goal or a math_object,
    with a 'text mode' checkbox that allows usr to
    choose text or math view.
    """

    def __init__(self, goal=None, math_object=None,
                 to_prove=False, open_problem=False):
        super().__init__()

        # (1) Buttons layout with text mode checkbox
        self.__text_mode_checkbox = QCheckBox(_('Text mode'))
        self.__text_mode_checkbox.setChecked(True)
        self.__text_mode_checkbox.clicked.connect(self.toggle_text_mode)
        # self.__history_checkbox = QCheckBox(_('Show saved exercises'))
        # self.__history_checkbox.clicked.connect(self.toggle_history)
        btns_lyt = QHBoxLayout()
        # btns_lyt.addWidget(self.__history_checkbox)
        btns_lyt.addStretch()
        btns_lyt.addWidget(self.__text_mode_checkbox)

        # main_widget_lyt.setContentsMargins(0, 0, 0, 0)

        # Toggle text mode if needed TODO
        # text_mode = cvars.get('display.text_mode_in_chooser_window', False)
        # self.__text_mode_checkbox.setChecked(text_mode)

        # (2) Stackedlayout
        self.goal_lyt = QStackedLayout()

        if goal:
            goal_text_wdg = GoalTextWidget(goal=goal,
                                           to_prove=to_prove,
                                           open_problem=open_problem,
                                           apply_statement=True)
        elif math_object:
            goal_text_wdg = GoalTextWidget(math_object=math_object,
                                           to_prove=to_prove,
                                           open_problem=open_problem,
                                           apply_statement=True)

        else:
            raise ValueError("GoalWidget needs either a goal or a math_object")
        if goal and goal.context:
            goal_math_wdg = GoalMathWidget(goal, to_prove=to_prove,
                                           open_problem=open_problem)
        else:
            target = goal.target.math_type if goal else math_object
            text = target.to_display(format_='html')

            goal_math_wdg = MathTextWidget(text)

        self.goal_lyt.insertWidget(0, goal_text_wdg)
        self.goal_lyt.insertWidget(1, goal_math_wdg)

        # Main layout
        main_lyt = QVBoxLayout()
        main_lyt.addLayout(self.goal_lyt)
        main_lyt.addLayout(btns_lyt)
        self.setLayout(main_lyt)

    def toggle_text_mode(self):
        if self.__text_mode_checkbox.isChecked():
            self.goal_lyt.setCurrentIndex(0)
        else:
            self.goal_lyt.setCurrentIndex(1)
