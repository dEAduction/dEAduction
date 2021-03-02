"""
#########################################################
# context_widgets_classes.py : exercise context widgets #
#########################################################

    Provide widgets classes for an exercise's context area, that is its
    target, objects (e.g. f:X->Y a function) and properties (e.g. f is
    continuous).

    Those widgets will be instantiated in ExerciseCentralWidget, which
    itself will be instantiated as an attribute of ExerciseMainWindow.
    Provided classes:
        - MathObjectWidget;
        - MathObjectWidgetItem;
        - TargetWidget.

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
Date           : July 2020

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
import logging
from pathlib import Path
from typing  import Tuple

from PySide2.QtCore    import ( Signal,
                                Slot)
from PySide2.QtGui     import ( QBrush,
                                QColor,
                                QIcon,
                                QFont)
from PySide2.QtWidgets import ( QHBoxLayout,
                                QVBoxLayout,
                                QLabel,
                                QWidget,
                                QListWidget,
                                QListWidgetItem)

from   deaduction.pylib.config.i18n      import   (_)
from   deaduction.pylib.mathobj          import   MathObject
from   deaduction.pylib.actions          import   explain_how_to_apply

from   deaduction.pylib.utils.filesystem import path_helper

import deaduction.pylib.config.vars as cvars

log = logging.getLogger(__name__)

################################
# MathObject widgets classes #
################################

# A usefull class.


class _TagIcon(QIcon):
    """
    A QIcon (self) depending on the tag (one of '+', '=', '≠') given
    as an argument of self.__init__. Mapping is the following:
        * '=' -> empty icon;
        * '+' -> blue icon;
        * '≠' -> purple icon.
    An exception is risen if a wrong tag is input.

    This class may be deleted in the future. Instead, a function would
    be used to map the tag to the icon pathlib.Path and one would have
    to instantiate the right class (QIcon, QLabel) depending on one's
    needs.
    """

    def __init__(self, tag: str):
        """
        Init self with a tag given as a str. See self.__doc__.

        :param tag: One of '+', '=', '≠'.
        """

        icons_base_dir = cvars.get('icons.path')
        icons_type = cvars.get('icons.context')  # e.g. 'blue'
        icons_dir = path_helper(icons_base_dir) / icons_type

        if tag not in ['=', '+', '≠']:
            # TODO: catch the exception below?
            raise ValueError('tag must be one of "=", "+", "≠". tag: {tag}.')
        elif tag == '=':
            super().__init__('')  # No icon, empty icon trick
            return None
        elif tag == '+':
            icon_path = icons_dir / 'tag_plus.png'
        elif tag == '≠':
            icon_path = icons_dir / 'tag_different.png'

        super().__init__(str(icon_path.resolve()))


# Classes for the two main widgets in 'Context' area of the exercise
# window, minus the target widget. Class MathObjectWidget is a parent
# widget containing a list of MathObjectWidgetItem. Both 'Objects' and
# 'Properties' widgets use those same two classes.


class MathObjectWidgetItem(QListWidgetItem):
    """
    Widget in charge of containing an instance of the class MathObject
    as an attribute and displaying it in a list (MathObjectWidget)
    other such instances. Objects (e.g. f:X->Y a function) and
    properties (e.g. f is continuous) are coded as instances of the
    class MathObject.

    On top of that, a so-called tag icon is displayed. That is, a
    different icon is displayed whether the MathObject is new or
    modified in comparison with the previous goal / context. See
    _TagIcon.__doc__.

    :attribute mathobject MathObject: The instance of the class
        one wants to display and keep as an attribute.
    :attribute tag str: The current tag (e.g. '+', '=' or '≠', see
        _TagIcon) of mathobject.
    """

    def __init__(self, mathobject: MathObject, tag: str='='):
        """
        Init self with an instance of the class MathObject and a tag.
        See self.__doc__.

        :param mathobject: The MathObject one wants to display.
        :param tag: The tag of mathobject.
        """

        super().__init__()

        self.mathobject = mathobject
        self.tag        = tag

        lean_name = mathobject.to_display()
        math_expr = mathobject.math_type.to_display(is_math_type=True)
        caption   = f'{lean_name} : {math_expr}'
        self.setText(caption)
        self.setIcon(_TagIcon(tag))
        # set tool_tips (merge several tool_tips if needed)
        tool_tips = explain_how_to_apply(mathobject)
        log.debug(f"Setting tooltips {tool_tips}")
        if len(tool_tips) == 1:
            tool_tip = _("Double click to") + " " + tool_tips[0]
            self.setToolTip(tool_tip)
        elif len(tool_tips) > 1:
            text = _("Double click to:")
            for tool_tip in tool_tips:
                text += "\n" + "• " + tool_tip
            self.setToolTip(text)

    def __eq__(self, other):
        """
        Define the operator == for the class MathObjectWidgetItem. Do
        not delete! It is useful to check if a given instance of the
        class MathObjectWidgetItem is or not in a list of such
        instances (the 'for item in mathobject_list:' test).

        :param other: An instance of the class MathObjectWidgetItem.
        :return: A boolean.
        """

        return self is other  # Brutal but that is what we need.

    def mark_user_selected(self, yes: bool=True):
        """
        Change self's background to green if yes or to normal color
        (e.g. white in light mode) if not yes.

        :param yes: See paragraph above.
        """

        # TODO: change color for double-click

        self.setBackground(QBrush(QColor('limegreen')) if yes else QBrush())


class MathObjectWidget(QListWidget):
    """
    A container class to display an ordered list of tagged (see
    _TagIcon.__doc__) instances of the class MathObject. Each element
    of this list inits an instance of the class MathObjectWidgetItem;
    this instance is set to be a child of self and is kept as an
    attribute in self.items. The two widgets 'Objects' and 'Properties'
    are instances of this class.

    :attribute items [MathObjectWidgetItem]: The displayed ordered
        list of instances of the class MathObjectWidgetItem. This
        attribute makes accessing them painless.
    """

    def __init__(self, tagged_mathobjects: [Tuple[MathObject, str]]=[]):
        """
        Init self an ordered list of tuples (mathobject, tag), where
        mathobject is an instance of the class MathObject (not
        MathObjectWidgetItem!) and tag is mathobject's tag a str,
        (see _TagIcon.__doc__).

        :param tagged_mathobjects: The list of tagged instances of the
            class MathObject.
        """

        super().__init__()

        # TODO: make self.items a property?
        self.items = []
        # set fonts for maths display
        math_font_name = cvars.get('mathematics_font', 'Default')
        self.setFont(QFont(math_font_name))
        for mathobject, tag in tagged_mathobjects:
            item = MathObjectWidgetItem(mathobject, tag)
            self.addItem(item)
            self.items.append(item)

        self.itemDoubleClicked.connect(self._emit_apply_math_object)

    @Slot(MathObjectWidgetItem)
    def _emit_apply_math_object(self, item):
        """
        Emit the signal self.apply_math_object_triggered with self as an
        argument. This slot is connected to ActionButton.clicked signal in
        self.__init__.
        """
        item.setSelected(False)
        self.apply_math_object_triggered.emit(item)


MathObjectWidget.apply_math_object_triggered = Signal(MathObjectWidget)


##########################
# Target widgets classes #
##########################

# Classe to display and store the target in the main exercise window.


class TargetWidget(QWidget):
    """
    A class to display a tagged target and store both the target and the
    tag as attributes. To display a target in ExerciseCentralWidget, use
    this class and not _TargetLabel as this one also manages layouts!

    :attribute target MathObject: The target one wants to display.
    :attribute tag str: The tag associated to target.
    """

    def __init__(self, target: MathObject=None, tag: str=None,
                 goal_count: str=''):
        """"
        Init self with an target (an instance of the class ProofStatePO)
        and a tag. If those are None, display an empty tag and '…' in
        place of the target. A caption is added on top of the target.

        :param target: The target to be displayed.
        :param tag: The tag associated to target.
        :param goal_count: a string indicating the goal_count state,
        e.g. "  2 / 3" means the goal number 2 out of 3 is currently being
        studied
        """

        super().__init__()

        self.target = target
        self.tag    = tag

        # ───────────────────── Widgets ──────────────────── #
        caption_label = QLabel(_('Target') + goal_count)
        self.setToolTip(_('To be proved'))
        # TODO: put the pre-set size of group boxes titles
        caption_label.setStyleSheet('font-size: 11pt;')

        # Display
        #   ∀ x ∈ X, ∃ ε, …
        # and not
        #   H : ∀ x ∈ X, ∃ ε, …
        # where H might be the lean name of the target. That's what
        # the .math_type is for.
        # 'is_math_type=True' triggers the bound variables naming
        if target:
            log.debug("updating target")
            text = target.math_type.to_display(is_math_type=True)
        else:
            text = '…'
        target_label = QLabel(text)
        size = cvars.get('display.target_font_size')
        target_label.setStyleSheet(f'font-size: {size};')
        # Set fonts for maths display
        math_font_name = cvars.get('mathematics_font', 'Default')
        target_label.setFont(QFont(math_font_name))


        # ───────────────────── Layouts ──────────────────── #

        central_layout = QVBoxLayout()
        central_layout.addWidget(caption_label)
        central_layout.addWidget(target_label)

        main_layout = QHBoxLayout()
        main_layout.addStretch()
        main_layout.addLayout(central_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)
