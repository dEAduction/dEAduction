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

from typing import Optional

from PySide2.QtCore    import ( Signal,
                                Slot,
                                Qt,
                                QMimeData,
                                QModelIndex,
                                QItemSelectionModel)
from PySide2.QtGui     import ( QBrush,
                                QColor,
                                QIcon,
                                QFont,
                                QStandardItem,
                                QStandardItemModel,
                                QPixmap,
                                QDrag,
                                QPalette)
from PySide2.QtWidgets import ( QHBoxLayout,
                                QVBoxLayout,
                                QSizePolicy,
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

    from_math_object = dict()  # Set in _exercise_main_window_widgets

    def __init__(self, context_math_object):
        """
        Init self with an instance of the class ContextMathObject.
        See self.__doc__.

        :param context_math_object: The ContextMathObject one wants to display.
        """

        super().__init__()

        # The following will be set when inserted:
        self.math_object_wdg: Optional[MathObjectWidget] = None
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

    def select(self):
        self.math_object_wdg.select_item(self)

    # def mark_user_selected(self, yes: bool = True):
    #     """
    #     Change self's background to green if yes or to normal color
    #     (e.g. white in light mode) if not yes.
    #     """
    #     # Fixme: obsolete
    #     background_color = cvars.get("display.color_for_selection", "LimeGreen")
    #     self.setBackground(QBrush(QColor(background_color)) if yes
    #                        else QBrush())

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


class DraggedItems(QWidget):
    """
    Display a stack of MathObjects in QLabels, to be used as dragged
    MathObjectWidgetItems. Note that currently only one item at a time may be
    dragged.
    """

    def __init__(self, items: [MathObjectWidgetItem]):
        super().__init__()

        self.items = items
        math_objects = [item.math_object for item in items]
        # lyt = LayoutMathObjects(math_objects, new=False)
        lyt = QVBoxLayout()
        for mo in math_objects:
            is_prop = mo.math_type.is_prop()
            label = QLabel()
            label.setObjectName("prop" if is_prop else "obj")
            text = mo.math_type_to_display(format_='html') if is_prop \
                else mo.to_display(format_='html')
            label.setText(text)
            label.setTextFormat(Qt.RichText)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            lyt.addWidget(label)

        self.setLayout(lyt)

        # The following is copied from proof_tree_widget.py:
        color_var = cvars.get("display.color_for_variables")
        color_prop = cvars.get("display.color_for_props")
        old_border_width = "2px"  # 1px
        old_border_style = "dashed"

        style_sheet = ("QWidget {background-color: transparent;}"
                       "QLabel#obj:enabled {padding: 5px;"
                       f"border-width: {old_border_width};"
                       f"border-color: {color_var};"
                       f"border-style: {old_border_style};"
                       "font-size: 20pt;"  # Added
                       "background-color: transparent;"  # Adde
                       "border-radius: 15px;}"
                       "QLabel#prop:enabled {padding: 5px;"
                       f"border-width: {old_border_width};"
                       f"border-color: {color_prop};"
                       f"border-style: {old_border_style};"
                       "font-size: 20pt;"
                       "background-color: transparent;"
                       "border-radius: 15px;}")
        self.setStyleSheet(style_sheet)

    def pixmap(self):
        return self.grab()


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
    math_object_dropped = Signal(MathObjectWidgetItem, MathObjectWidgetItem)

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
        self._saved_style_sheet = None
        self._current_index = None  # Last clicked item
        # Current dragged item, if any. Must be reset to None when dropped.
        self.dragged_index = None

        # The following are set by ExerciseCentralWidget:
        self.is_props_wdg = False
        self.context_selection: callable = None
        self.clear_context_selection: callable = None

        # Possible settings:
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        # list_view.setMovement(QListView.Free)
        # list_view.setRowHidden(1, True)
        # list_view.setAlternatingRowColors(True)

        # No text edition (!)
        # self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # By default, disable drag and drop. This may be changed at creation
        # (see _exercise_main_window_widgets).
        self.setDragEnabled(False)
        self.setDragDropMode(QAbstractItemView.NoDragDrop)

        # After filling content?
        # model = QStandardItemModel(self)
        self.setModel(QStandardItemModel())  # parent=self?
        self.setItemDelegate(HTMLDelegate())  # parent=self?

        self.items = []
        self._potential_drop_receiver = None

        # set fonts for maths display FIXME: put this in delegate
        # math_font_name = cvars.get('display.mathematics_font', 'Default')
        # main_font_size   = int(cvars.get('display.main_font_size')[:-2])
        # font = QFont(math_font_name)
        # font.setPointSize(main_font_size)
        # self.setFont(font)  # FIXME: does not do anything

        # self.setStyle(f'{{font - size: {main_font_size};}}')

        if context_math_objects:
            self.add_math_objects(context_math_objects)

    @property
    def accept_dropped_statements(self):
        return self.is_props_wdg

    def select_index(self, index, yes=True):
        # self.selectionModel().select(index, QItemSelectionModel.SelectCurrent)
        self.selectionModel().select(index, QItemSelectionModel.Select if yes
                                     else QItemSelectionModel.Deselect)

    def select_item(self, item: MathObjectWidgetItem):
        self.select_index(item.index())

    def add_math_objects(self, math_objects):
        for math_object in math_objects:
            item = MathObjectWidgetItem(math_object)
            self.model().appendRow(item)
            self.items.append(item)
            item.math_object_wdg = self
            # item.setDragEnabled(True)
            # item.setDropEnabled(True)

    def set_math_objects(self, math_objects):
        self.items = []
        model = self.model()
        model.removeRows(0, model.rowCount())
        self.add_math_objects(math_objects)

    def item_from_index(self, index_):
        item = self.model().itemFromIndex(index_)
        return item

    def selected_items(self):
        return [self.item_from_index(index) for index in self.selectedIndexes()]

    # @Slot(MathObjectWidgetItem)
    # def _emit_apply_math_object(self, item):
    #     """
    #     Emit the signal self.apply_math_object_triggered with self as an
    #     argument. This slot is connected to ActionButton.clicked signal in
    #     self.__init__.
    #     """
    #     item.setSelected(False)
    #     self.apply_math_object_triggered.emit(item)

    # def current_item(self):
    #     return self.item_from_index(self.currentIndex())

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

    def index_from_event(self, event):
        return self.indexAt(event.pos())

    def item_from_event(self, event):
        return self.item_from_index(self.index_from_event(event))

    def drop_enabled(self):
        return (self.dragDropMode() == QAbstractItemView.DragDrop or
                self.dragDropMode() == QAbstractItemView.DropOnly)

    @property
    def potential_drop_receiver(self):
        return self._potential_drop_receiver

    @potential_drop_receiver.setter
    def potential_drop_receiver(self, receiver: QModelIndex):
        if (self.potential_drop_receiver and
                receiver != self.potential_drop_receiver):
            self.select_index(self._potential_drop_receiver, False)
            self._potential_drop_receiver = None
        if receiver and receiver not in self.selectedIndexes():
            self._potential_drop_receiver = receiver
            self.select_index(receiver)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self._current_index = self.index_from_event(event)

    def startDrag(self, supported_actions) -> None:
        drag = QDrag(self)

        if not self._current_index:
            # log.debug("Drag aborted")
            return

        # # Drag all selected items or just last one? OBSOLETE
        # several_items = cvars.get('functionality.drag_several_items', False)
        # if several_items:
        #     if self._current_item not in items:
        #         items.append(self._current_item)
        # else:
        # log.debug("Selecting item")

        # Set selection to dragged item
        self.dragged_index = self._current_index
        item = self.item_from_index(self.dragged_index)
        self.set_selection([item])

        mime_data = QMimeData([item])
        drag.setMimeData(mime_data)

        # Set image of dragged item
        pixmap = DraggedItems(self.selected_items()).pixmap()
        drag.setPixmap(pixmap)
        drag.exec_(Qt.IgnoreAction)

    def dragEnterEvent(self, event):
        """
        Mark enterEvent of StatementTreeWidgetItem by changing background color.
        """

        source = event.source()
        if isinstance(source, StatementsTreeWidget):
            if self.drop_enabled() and self.accept_dropped_statements:
                self._saved_style_sheet = self.styleSheet()
                color = cvars.get("display.color_for_selection", "LimeGreen")
                self.setStyleSheet(f'background-color: {color};')
                self.setDropIndicatorShown(False)  # Do not show "where to drop"
                event.acceptProposedAction()
            else:
                event.ignore()  # No dropped statement
        else:
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        """
        Restore normal styleSheet (background color).
        """
        self.setStyleSheet(self._saved_style_sheet)
        self._saved_style_sheet = None
        self.setDropIndicatorShown(True)
        self.potential_drop_receiver = None  # Unselect automatically

    def dragMoveEvent(self, event) -> None:
        """
        When a MathWidgetItem is dragged over a potential receiver, select it
        temporarily.
        """

        index = self.index_from_event(event)
        if index != self.potential_drop_receiver:
            self.potential_drop_receiver = None  # Unselect automatically

        # if index:
        item: MathObjectWidgetItem = self.item_from_index(index)
        if item and item.isDropEnabled():
            self.potential_drop_receiver = index

        event.accept()

    def set_selection(self, items):
        """
        Set selection to items, clearing previous selection.
        """
        if self.clear_context_selection:
            self.clear_context_selection()
        for item in items:
            item.select()

    def dropEvent(self, event):
        """
        Emit signal corresponding to dropEvent:
        - drop of a statementTreeItem   -> statement_dropped
        - drop a MathWidgetItem         -> math_object_dropped.
        """
        source = event.source()
        if isinstance(source, StatementsTreeWidget):
            dragged_widget = source.currentItem()
            self.statement_dropped.emit(dragged_widget)
            self.setStyleSheet('background-color: white;')
        elif isinstance(source, MathObjectWidget):

            dragged_index = source.dragged_index
            source.dragged_index = None
            index = self.index_from_event(event)
            if dragged_index == index:  # Absurd auto-drop, abort
                source.select_index(dragged_index, False)
                self.select_index(index, False)
                return

            print(f"Source : {source}, dragged index: {dragged_index}")
            # # print(f"Source selected items: {len(source.selected_items())}")
            # if dragged_index not in source.selectedIndexes():
            #     source.select_index(dragged_index)
            # # print(f"Source selected items: {len(source.selected_items())}")
            # # Add receiver to selection
            # if index not in self.selectedIndexes():
            #     self.select_index(index)

            # Emit signal
            premise = source.item_from_index(dragged_index)
            operator = self.item_from_index(index)
            print(premise, operator)
            if premise and operator:
                self.set_selection([premise, operator])
            self.math_object_dropped.emit(premise, operator)

        event.accept()
        self.setDropIndicatorShown(False)

    def currentChanged(self, current, previous) -> None:
        """
        Prevent current index setting (which would be highlighted in light
        blue, interfering with deaduction's own selection mechanism).
        """
        self.setCurrentIndex(QModelIndex())

# Obsolete:
# MathObjectWidget.apply_math_object_triggered = Signal(MathObjectWidget)


##########################
# Target widgets classes #
##########################

# Classes to display and store the target in the main exercise window.

class TargetLabel(QLabel):
    """
    A class to display the target. Can be used in ExerciseMainWindow via
    TargetWidget, and in the exercise chooser. Take the target as a
    parameter, and display it in richText format (html).
    """

    clicked = Signal()
    double_clicked = Signal()

    def __init__(self, target):
        super().__init__()
        self._double_clicked = False
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

    def mouseReleaseEvent(self, event):
        """
        Emit the clicked signal only if this is not a double click.
        """
        if not self._double_clicked:
            # print("target label clicked")
            self.clicked.emit()
        else:
            self._double_clicked = False

    def mouseDoubleClickEvent(self, event):
        # print("target label double clicked")
        self._double_clicked = True
        self.double_clicked.emit()


class TargetWidget(QWidget):
    """
    A class to display a tagged target and store both the target and the
    tag as attributes. To display a target in ExerciseCentralWidget, use
    this class and not _TargetLabel as this one also manages layouts!
    """

    def __init__(self, target=None, goal_count: int = 0):
        """"
        Init self with a target (an instance of the class ProofStatePO)
        and a tag. If those are None, display an empty tag and '…' in
        place of the target. A caption is added on top of the target.

        :param target: The target to be displayed.
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
        self.target = target

    def set_pending_goals_counter(self, pgn: int):
        text = _("Target") + " " + str(pgn) if pgn else _("Target")
        self.caption_label.setText(text)

