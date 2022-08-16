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

from PySide2.QtCore    import ( Signal,
                                Slot,
                                Qt,
                                QModelIndex)
from PySide2.QtGui     import ( QBrush,
                                QColor,
                                QIcon,
                                QFont,
                                QStandardItem,
                                QStandardItemModel,
                                QPalette)
from PySide2.QtWidgets import ( QHBoxLayout,
                                QVBoxLayout,
                                QLabel,
                                QWidget,
                                QListView,
                                QAbstractItemView)

from .html_list_view                     import   HTMLDelegate
# from   deaduction.pylib.mathobj          import   MathObject

from   deaduction.pylib.utils.filesystem import path_helper

import deaduction.pylib.config.vars as cvars

from deaduction.dui.elements import ( StatementsTreeWidget,
                                      StatementsTreeWidgetItem)

log = logging.getLogger(__name__)
global _

################################
# MathObject widgets classes #
################################


class TargetLabel(QLabel):
    """
    A class to display the target. Can be used in ExerciseMainWindow via
    TargetWidget, and in the exercise chooser. Take the target as a
    parameter, and display it in richText format (html).
    """

    def __init__(self, target):
        super().__init__()
        # Display
        #   ∀ x ∈ X, ∃ ε, …
        # and not
        #   H : ∀ x ∈ X, ∃ ε, …
        # where H might be the lean name of the target. That's what
        # the .math_type is for.
        if target:
            # log.debug("updating target")
            text = target.math_type_to_display()
        else:
            text = '…'

        self.setText(text)
        self.setTextFormat(Qt.RichText)

    def replace_target(self, target):
        self.setText(target.math_type_to_display())

    # Debugging
    # def mouseReleaseEvent(self, ev) -> None:
    #     print("Clac!!")


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
        # icons_type = cvars.get('icons.context')  # e.g. 'blue'
        # icons_dir = path_helper(icons_base_dir) / icons_type

        icon_str = ''
        if tag not in ['=', '+', '≠']:
            raise ValueError('tag must be one of "=", "+", "≠". tag: {tag}.')
        elif tag in ('+', '≠'):
            icon_path = path_helper(icons_base_dir) / 'checked.png'
            icon_str = str(icon_path.resolve())
        super().__init__(icon_str)


# Classes for the two main widgets in 'Context' area of the exercise
# window, minus the target widget. Class MathObjectWidget is a parent
# widget containing a list of MathObjectWidgetItem. Both 'Objects' and
# 'Properties' widgets use those same two classes.


class MathObjectWidgetItem(QStandardItem):
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

    def __init__(self, context_math_object):
        """
        Init self with an instance of the class ContextMathObject.
        See self.__doc__.

        :param context_math_object: The ContextMathObject one wants to display.
        """

        super().__init__()

        self.context_math_object = context_math_object
        if context_math_object.is_new:
            self.tag = '+'
        elif context_math_object.is_modified:
            self.tag = '≠'
        else:
            self.tag = '='

        lean_name = context_math_object.to_display()
        math_expr = context_math_object.math_type_to_display()
        caption   = f'{lean_name} : {math_expr}'
        self.setText(caption)
        self.setIcon(_TagIcon(self.tag))
        # Uncomment to enable drag:
        self.setDragEnabled(True)

    @property
    def math_object(self):
        return self.context_math_object

    @property
    def logic(self):
        return self.math_object

    @property
    def display_name(self):
        return self.math_object.display_name

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

    def mark_user_selected(self, yes: bool = True):
        """
        Change self's background to green if yes or to normal color
        (e.g. white in light mode) if not yes.
        """
        background_color = cvars.get("display.color_for_selection", "LimeGreen")
        self.setBackground(QBrush(QColor(background_color)) if yes
                           else QBrush())


# class TargetWidgetItem(QStandardItem):
#     """
#     Widget to display a target in the chooser, with the same format as the
#     MathObjectWidgetItem.
#     """
#
#     # FIXME: not used.
#
#     def __init__(self, target):
#
#         super().__init__()
#         self.target = target
#         caption = target.math_type_to_display()
#         self.setText(caption)


class MathObjectWidget(QListView):
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

    # Signals
    statement_dropped = Signal(StatementsTreeWidgetItem)
    math_object_dropped = Signal(MathObjectWidgetItem)

    def __init__(self, context_math_objects=None, target=None):
        """
        Init self an ordered list of tuples (mathobject, tag), where
        mathobject is an instance of the class MathObject (not
        MathObjectWidgetItem!) and tag is mathobject's tag a str,
        (see _TagIcon.__doc__).

        :param tagged_mathobjects: The list of tagged instances of the
            class MathObject.
        """

        super().__init__()

        # Possible settings:
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        # list_view.setMovement(QListView.Free)
        # list_view.setRowHidden(1, True)
        # list_view.setAlternatingRowColors(True)

        # No text edition (!)
        # self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # By default, disable drag and drop. This may be changed at creation.
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)

        # After filling content?
        # model = QStandardItemModel(self)
        self.setModel(QStandardItemModel())  # parent=self?
        self.setItemDelegate(HTMLDelegate())  # parent=self?

        self.items = []

        # set fonts for maths display FIXME: put this in delegate
        # math_font_name = cvars.get('display.mathematics_font', 'Default')
        # main_font_size   = int(cvars.get('display.main_font_size')[:-2])
        # font = QFont(math_font_name)
        # font.setPointSize(main_font_size)
        # self.setFont(font)  # FIXME: does not do anything

        # self.setStyle(f'{{font - size: {main_font_size};}}')

        if context_math_objects:
            self.add_math_objects(context_math_objects)

        # elif target:
        #     self.add_target(target)

        # self.horizontalScrollBar().setRange(0, self.width)
        # log.debug(f"Horizontal context width: {self.width}")
        # log.debug(f"Size hint for col 0: {self.sizeHintForColumn(0)}")

    # def add_target(self, target):
    #     item = TargetWidgetItem(target)
    #     self.model().appendRow(item)
    #
    # def set_target(self, target):
    #     model = self.model()
    #     model.removeRows(0, model.rowCount())
    #     self.add_target(target)

    def add_math_objects(self, math_objects):
        for math_object in math_objects:
            item = MathObjectWidgetItem(math_object)
            self.model().appendRow(item)
            self.items.append(item)
            # item.setDragEnabled(True)
            # item.setDropEnabled(True)

    def set_math_objects(self, math_objects):
        self.items = []
        model = self.model()
        model.removeRows(0, model.rowCount())
        self.add_math_objects(math_objects)

    def currentChanged(self, current, previous) -> None:
        """
        Prevent current index setting (which would be highlighted in light
        blue, interfering with deaduction's own selection mechanism).
        """
        self.setCurrentIndex(QModelIndex())

    def item_from_index(self, index_):
        item = self.model().itemFromIndex(index_)
        return item

    # @Slot(MathObjectWidgetItem)
    # def _emit_apply_math_object(self, item):
    #     """
    #     Emit the signal self.apply_math_object_triggered with self as an
    #     argument. This slot is connected to ActionButton.clicked signal in
    #     self.__init__.
    #     """
    #     item.setSelected(False)
    #     self.apply_math_object_triggered.emit(item)

    def current_item(self):
        return self.item_from_index(self.currentIndex())

    def item_from_logic(self, math_object) -> MathObjectWidgetItem:
        """
        Return MathObjectWidgetItem whose math_object is math_object.
        """
        # Fixme: obsolete
        items = [item for item in self.items
                 if item.math_object == math_object]
        if items:
            return items[0]
        else:
            return None

    def item_from_nb(self, idx: int) -> MathObjectWidgetItem:
        items = self.items
        if idx in range(len(items)):
            return items[idx]

    # def accept_drops(self):
    #     if (self.DragDropMode() is QAbstractItemView.DragDrop or
    #             self.DragDropMode() is QAbstractItemView.DragOnly):
    #         self.setDragDropMode(QAbstractItemView.DragDrop)
    #     else:
    #         self.setDragDropMode(QAbstractItemView.DropOnly)
    #
    # def accept_drags(self):
    #     if (self.DragDropMode() is QAbstractItemView.DragDrop or
    #             self.DragDropMode() is QAbstractItemView.DropOnly):
    #         self.setDragDropMode(QAbstractItemView.DragDrop)
    #     else:
    #         self.setDragDropMode(QAbstractItemView.DragOnly)
    #         self.setDragEnabled(True)

    def item_from_event(self, event):
        pos = event.pos()
        index = self.indexAt(pos)
        item = self.item_from_index(index)
        return item

    def drop_enabled(self):
        return (self.dragDropMode() == QAbstractItemView.DragDrop or
                self.dragDropMode() == QAbstractItemView.DropOnly)

    def dragEnterEvent(self, event):
        """
        Mark enterEvent by changing background color.
        """
        super().dragEnterEvent(event)
        source = event.source()
        if isinstance(source, StatementsTreeWidget) and self.drop_enabled():
            self.setStyleSheet('background-color: yellow;')
            self.setDropIndicatorShown(False)  # Do not show "where to drop"

    def dragLeaveEvent(self, event):
        super().dragLeaveEvent(event)
        # No source for dragLeaveEvent
        # source = event.source()
        # if isinstance(source, StatementsTreeWidget):
        self.setStyleSheet('background-color: white;')
        self.setDropIndicatorShown(True)

    def dropEvent(self, event):
        """
        Call action corresponding to dropEvent:
        - drop of a statementWidget --> add statement to context.
        """
        source = event.source()
        if isinstance(source, StatementsTreeWidget):
            dragged_widget = source.currentItem()
            self.statement_dropped.emit(dragged_widget)
            self.setStyleSheet('background-color: white;')
        elif isinstance(source, MathObjectWidget):
            # dragged_widget = source.currentIndex()
            # print("Math Obj dropped")
            self.math_object_dropped.emit(self.item_from_event(event))
            event.accept()


# Obsolete:
# MathObjectWidget.apply_math_object_triggered = Signal(MathObjectWidget)


##########################
# Target widgets classes #
##########################

# Classes to display and store the target in the main exercise window.

class TargetWidget(QWidget):
    """
    A class to display a tagged target and store both the target and the
    tag as attributes. To display a target in ExerciseCentralWidget, use
    this class and not _TargetLabel as this one also manages layouts!
    """

    def __init__(self, target=None, goal_count: int = 0):
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

        # ───────────────────── Widgets ──────────────────── #
        self.caption_label = QLabel()
        self.set_pending_goals_counter(goal_count)
        self.target_label = TargetLabel(target)
        self.target_label.setAutoFillBackground(True)  # For highlighting

        self.setToolTip(_('To be proved'))
        # TODO: put the pre-set size of group boxes titles
        # caption_label.setStyleSheet('font-size: 11pt;')

        # TODO: method setfontstyle
        # size = cvars.get('display.target_font_size')
        # self.target_label.unselected_style = f'font-size: {size};'
        # self.target_label.unselected_style = ''
        # self.target_label.selected_style = self.target_label.unselected_style \
        #     + f'background-color: limegreen;'
        # self.target_label.setStyleSheet(self.target_label.unselected_style)

        # Set fonts for maths display
        # math_font_name = cvars.get('display.mathematics_font', 'Default')
        # self.target_label.setFont(QFont(math_font_name))

        self.selected_style = ""  # Set in _exercise_main_window_widgets
        self.unselected_style = ""
        # ───────────────────── Layouts ──────────────────── #

        central_layout = QVBoxLayout()
        central_layout.addWidget(self.caption_label)
        central_layout.addWidget(self.target_label)
        central_layout.setAlignment(self.caption_label, Qt.AlignHCenter)
        central_layout.setAlignment(self.target_label, Qt.AlignHCenter)

        main_layout = QHBoxLayout()
        main_layout.addStretch()
        main_layout.addLayout(central_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

    # For debugging
    # def mousePressEvent(self, event) -> None:
    #     print("Clac!")
    #
    # def mouseReleaseEvent(self, event) -> None:  # DOES NOT WORK
    #     print("Click!")
    #
    # def mouseDoubleClickEvent(self, event) -> None:
    #     print("Double click!")

    def mark_user_selected(self, yes: bool=True):
        """
        Change self's background to green if yes or to normal color
        (e.g. white in light mode) if not yes.

        :param yes: See paragraph above.
        """
        if hasattr(self, 'target_label'):
            if yes:
                # self.target_label.setStyleSheet(self.selected_style)
                self.target_label.setBackgroundRole(QPalette.Highlight)
                self.target_label.setForegroundRole(QPalette.WindowText)
            else:
                self.target_label.setBackgroundRole(QPalette.Window)
                # self.target_label.setStyleSheet(self.unselected_style)
        else:
            log.warning("Attempt to use deleted attribute target_label")

    @property
    def math_object(self):
        return self.target

    @property
    def logic(self):
        return self.target

    def replace_target(self, target):
        self.target_label.replace_target(target)

    def set_pending_goals_counter(self, pgn: int):
        text = _("Target") + " " + str(pgn) if pgn else _("Target")
        self.caption_label.setText(text)

