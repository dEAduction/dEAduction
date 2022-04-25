"""
# Display trials for proof trees #

Author(s)     : F Le Roux
Maintainer(s) : F. Le Roux
Created       : 03 2022 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

This file is part of dEAduction.

    dEAduction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    dEAduction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
from typing import Union, Optional
from PySide2.QtWidgets import (QApplication, QFrame, QLayout,
                               QHBoxLayout, QVBoxLayout, QGridLayout,
                               QLineEdit, QListWidget, QWidget, QGroupBox,
                               QLabel, QTextEdit, QSizePolicy)
from PySide2.QtWidgets import QScrollArea
from PySide2.QtCore import Qt, Signal, Slot, QSettings, QEvent, QRect, \
    QPoint, QTimer
from PySide2.QtGui import QFont, QColor, QPalette, QIcon, QPainter, QPixmap, \
    QPainterPath, QPolygon, QPen, QBrush

import sys

import deaduction.pylib.config.vars as cvars
import deaduction.pylib.config.dirs as cdirs

global _

if __name__ != "__main__":
    from deaduction.pylib.proof_tree import GoalNode
    from deaduction.pylib.mathobj import MathObject
else:
    def _(x):
        return x

    class MathObject:
        pass

    class GoalNode:
        pass


log = logging.getLogger(__name__)


class BlinkingLabel(QLabel):
    def __init__(self, text=None):
        super(BlinkingLabel, self).__init__(text)
        self.text = text
        self.flag = None
        self.timer = QTimer(self, interval=1000)
        self.timer.timeout.connect(self.blink)
        # self.start_blinking()

    def start_blinking(self):
        self.flag = True
        self.timer.start()

    def stop_blinking(self):
        self.timer.stop()

    def blink(self):
        self.setText(" " if self.flag else self.text)
        self.flag = not self.flag


def display_object(math_objects):
    """
    Recursively convert MathObjects inside math_objects to str in html format.
    """
    if math_objects is None:
        return None
    elif isinstance(math_objects, str):
        return math_objects
    elif isinstance(math_objects, list):
        return list([display_object(mo) for mo in math_objects])
    elif isinstance(math_objects, tuple):
        return tuple(display_object(mo) for mo in math_objects)
    else:
        if math_objects.math_type.is_prop():
            return math_objects.math_type.to_display(format_="html")
        else:
            return math_objects.to_display(format_="html")


def middle(p, q) -> QPoint:
    return (p+q)/2


def mid_left(rect: QRect) -> QPoint:
    return middle(rect.topLeft(), rect.bottomLeft())


def mid_right(rect: QRect) -> QPoint:
    return middle(rect.topRight(), rect.bottomRight())


def operator_arrow():
    # arrow_label.setScaledContents(True)
    # arrow_label.setMaximumSize(self.height(), self.height())
    arrow_label = QLabel()
    arrow_icon_path = cdirs.icons / "right_arrow.png"
    pixmap = QPixmap(str(arrow_icon_path.resolve()))
    arrow_label.setPixmap(pixmap)

    return arrow_label


def paint_arrow(origin, end, painter: QPainter,
                arrow_height=4, style=Qt.SolidLine,
                color=None, pen_width=1):
    if not color:
        color = cvars.get("display.color_for_operator_props")

    painter.begin()
    pen = QPen()
    pen.setColor(QColor(color))
    pen.setWidth(pen_width)
    pen.setJoinStyle(Qt.MiterJoin)
    pen.setCapStyle(Qt.FlatCap)
    painter.setPen(pen)
    arrow_height = arrow_height
    vect_x = QPoint(arrow_height, 0)
    vect_y = QPoint(0, arrow_height)
    end = end - vect_x
    pen.setStyle(style)
    painter.setPen(pen)
    painter.drawLine(origin, end - 2 * vect_x)
    # Triangle
    brush = QBrush(color, Qt.SolidPattern)
    painter.setBrush(brush)
    pen.setStyle(Qt.SolidLine)
    pen.setWidth(1)
    painter.setPen(pen)
    upper_vertex = end - 2 * vect_x - vect_y
    lower_vertex = end - 2 * vect_x + vect_y
    triangle = QPolygon([end, upper_vertex, lower_vertex, end])
    painter.drawPolygon(triangle)
    painter.end()


def arrow(wdg1: QLayout, wdg2: QLayout, painter):
    """
    Paint an arrow between two widgets.
    """
    rect1 = wdg1.rect()
    rect2 = wdg2.rect()
    if rect1.right() < rect2.left():
        origin = mid_left(rect1)
        end = mid_right(rect2)
        paint_arrow(origin, end, painter)


class HorizontalArrow(QWidget):
    def __init__(self, width=50, arrow_height=4, style=Qt.SolidLine):
        super(HorizontalArrow, self).__init__()
        self.color = cvars.get("display.color_for_operator_props")
        self.style = style
        self.width = width
        self.setFixedWidth(width)
        self.setFixedHeight(arrow_height*3)
        self.pen_width = 1
        self.arrow_height = arrow_height + self.pen_width

    def paintEvent(self, e):
        painter = QPainter(self)
        pen = QPen()
        pen.setColor(QColor(self.color))
        pen.setWidth(self.pen_width)
        pen.setJoinStyle(Qt.MiterJoin)
        pen.setCapStyle(Qt.FlatCap)
        painter.setPen(pen)
        rectangle = self.rect()
        # self.paint_arrow(painter, mid_left(rectangle), mid_right(rectangle))

        origin = mid_left(rectangle)
        end = mid_right(rectangle)
        arrow_height = self.arrow_height
        vect_x = QPoint(arrow_height, 0)
        vect_y = QPoint(0, arrow_height)
        end = end - vect_x
        pen.setStyle(self.style)
        painter.setPen(pen)
        painter.drawLine(origin, end-2*vect_x)
        # Triangle
        brush = QBrush(self.color, Qt.SolidPattern)
        painter.setBrush(brush)
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(1)
        painter.setPen(pen)
        upper_vertex = end-2*vect_x - vect_y
        lower_vertex = end-2*vect_x + vect_y
        triangle = QPolygon([end, upper_vertex, lower_vertex, end])
        painter.drawPolygon(triangle)
        painter.end()

    # def paint_arrow(self, painter: QPainter, origin: QPoint, end: QPoint):
    #     arrow_height = self.arrow_height
    #     vect_x = QPoint(arrow_height, 0)
    #     vect_y = QPoint(0, arrow_height)
    #     end = end - vect_x
    #     painter.pen().setStyle(self.style)
    #     # painter.drawLine(origin, end-vect_x)
    #     # Triangle
    #     painter.pen().setStyle(Qt.SolidLine)
    #     upper_vertex = end-2*vect_x - vect_y
    #     lower_vertex = end-2*vect_x + vect_y
    #     triangle = QPolygon([end, upper_vertex, lower_vertex, end])
    #     painter.drawPolygon(triangle)

    def set_width(self, width):
        self.setFixedWidth(width)


class DisclosureTriangle(QLabel):
    """
    A dynamic QLabel that changes appearance and call a function when clicked.
    """

    def __init__(self, slot: callable, hidden=False):
        super().__init__()
        self.slot = slot
        self.setText("▷" if hidden else "▽")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def mousePressEvent(self, ev) -> None:
        """
        Modify self's appearance and call the slot function.
        """
        self.setText("▷" if self.text() == "▽" else "▽")
        self.slot()


class VertBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(2)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)


class RawLabelMathObject(QLabel):
    """
    Mother class for displaying a MathObject or a msg which is computed by
    the callable html_msg, which takes parameter use_color and bf.
    This allows to disable self by setting use_color=False, or to highlight
    it by setting bf=True.
    """

    def __init__(self, math_object=None,
                 html_msg: Optional[callable] = None):
        """
        Either math_object or html_msg is not None. If html_msg is not None
        then it is a callable with parameter use_color.
        """
        super().__init__()
        assert math_object or html_msg
        self.html_msg = html_msg
        self.math_object = math_object
        self.setTextFormat(Qt.RichText)
        self.bold = False

        self.setText(self.txt())

    def set_bold(self, yes=True):
        self.bold = yes
        if yes:
            self.setStyleSheet("font-weight: bold;")
        else:
            self.setStyleSheet("")

    @property
    def is_prop(self):
        if self.math_object and isinstance(self.math_object, MathObject):
            return self.math_object.math_type.is_prop()

    def txt(self):
        """
        Return text msg adapted to self.isEnabled and self.bold.
        """
        pre = "<b>" if self.bold else ""
        post = "</b>" if self.bold else ""
        if self.html_msg:
            return pre + self.html_msg(use_color=self.isEnabled()) + post

        use_color = self.isEnabled()
        if isinstance(self.math_object, str):
            return self.math_object
        else:
            math_object = (self.math_object.math_type if self.is_prop
                           else self.math_object)
            txt = math_object.to_display(format_="html", use_color=use_color)
        return txt

    def changeEvent(self, event) -> None:
        """
        In case object is enabled/disabled, change to display colored variables.
        """
        self.setText(self.txt())
        event.accept()


class GenericLMO(RawLabelMathObject):
    """
    A class for displaying MathObject inside a frame.
    """
    def __init__(self, math_object, new=True):
        super().__init__(math_object)
        # The following is used in the style sheet
        is_new = "new" if new else "old"
        is_prop = "prop" if self.is_prop else "obj"
        self.setObjectName(is_new + "_" + is_prop)


class LayoutMathObject(QHBoxLayout):
    """
    Display a LabelMathObject inside a h-layout so that the box is not too big.
    """

    def __init__(self, math_object, align=None, new=True):
        super().__init__()
        if align in (None, "right"):
            self.addStretch(1)
        self.addWidget(GenericLMO(math_object, new=new))
        if align in (None, "left"):
            self.addStretch(1)


class LayoutMathObjects(QVBoxLayout):
    """
    Display a vertical pile of LayoutMathObjects.
    """

    def __init__(self, math_objects, align=None, new=True):
        super().__init__()
        self.addStretch(1)
        for math_object in math_objects:
            self.addLayout(LayoutMathObject(math_object, align=align, new=new))
        self.addStretch(1)


class OperatorLMO(RawLabelMathObject):
    """
    Display a MathObject which is a property operating on other objects.
    """

    def __init__(self, math_object):
        super().__init__(math_object)
        self.setObjectName("operator")


class LayoutOperator(QWidget):
    """
    Display a OperatorLMO inside a v-layout so that the box is not too big.
    """

    def __init__(self, math_object):
        super().__init__()
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(OperatorLMO(math_object))
        layout.addStretch(1)
        self.setLayout(layout)


class SubstitutionArrow(QWidget):
    """
    Display an arrow labelled by some Generic LMO, e.g. a rewriting rule as in
                f(x) = y
            ------------------>.
    """
    def __init__(self, rw_rule):
        super().__init__()
        layout = QVBoxLayout()
        layout.addStretch(1)
        # Label
        label_layout = QHBoxLayout()
        self.rw_label = GenericLMO(rw_rule, new=False)
        self.rw_label.show()
        self.label_width = self.rw_label.geometry().width()
        # self.rw_label.hide()
        label_layout.addStretch(1)
        label_layout.addWidget(self.rw_label)
        label_layout.addStretch(1)
        layout.addLayout(label_layout)

        # Arrow
        arrow_layout = QHBoxLayout()
        self.arrow_wdg = HorizontalArrow(width=self.label_width + 100,
                                         style=Qt.DashLine)
        arrow_layout.addStretch(1)
        arrow_layout.addWidget(self.arrow_wdg)
        arrow_layout.addStretch(1)
        layout.addLayout(arrow_layout)

        # Get a symmetric geometry:
        fake_label = GenericLMO(rw_rule, new=False)
        size_pol = fake_label.sizePolicy()
        size_pol.setRetainSizeWhenHidden(True)
        fake_label.setSizePolicy(size_pol)
        layout.addWidget(fake_label)
        layout.addStretch(1)
        self.setLayout(layout)  # FIXME: arrow does not show!
        fake_label.hide()

    # def changeEvent(self, e):
    #     label_width = self.rw_label.geometry().width()
    #     self.arrow_wdg.set_width(label_width)


###########################
# Context / target blocks #
###########################
class ContextWidget(QWidget):
    """
    A widget for displaying new context object on one line.
    """

    def __init__(self, math_objects):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.addStretch(1)

        self.math_objects = []
        for math_object in math_objects:
            self.add_child(math_object)

        self.setLayout(self.layout)

    def add_child(self, math_object: QWidget):
        """
        Insert a child math_object at the end, just before the stretch item.
        """
        # FIXME: unused?
        self.math_objects.append(math_object)
        item = GenericLMO(math_object)
        self.layout.insertWidget(self.layout.count()-1, item)


class PureContextWidget(ContextWidget):
    """
    A widget for displaying new context object from a pure context step,
    e.g. modus ponens, shown as output of an "operator" object receiving some
    "input objects", as in
    y --> [f surjective] --> x, f(x)=y.
    """

    def __init__(self, premises, operator, conclusions):
        super().__init__([])
        self.premises = premises
        self.operator = operator
        self.conclusions = conclusions

        input_layout = LayoutMathObjects(premises, align="right", new=False)
        output_layout = LayoutMathObjects(conclusions, align="left")
        operator_wdg = LayoutOperator(operator)

        # Input -> Operator -> output:
        if premises:
            self.layout.addLayout(input_layout)
            self.layout.addWidget(HorizontalArrow())
        self.layout.addWidget(operator_wdg)
        self.layout.addWidget(HorizontalArrow())
        self.layout.addLayout(output_layout)

        self.layout.addStretch(1)


class SubstitutionContextWidget(ContextWidget):
    """
    A widget for displaying new context object from a rewriting, e.g.
            f(x) = y
    y in A ----------> f(x) in A.
    """

    def __init__(self, premises, operator, conclusions):
        super().__init__([])
        self.premises = premises
        self.operator = operator
        self.conclusions = conclusions

        self.input_layout = LayoutMathObjects(premises, align="right",
                                              new=False)
        self.output_layout = LayoutMathObjects(conclusions, align="left")
        arrow_wdg = SubstitutionArrow(operator)

        # Input -> Operator -> output:
        self.layout.addLayout(self.input_layout)
        # self.layout.addWidget(HorizontalArrow())
        self.layout.addWidget(arrow_wdg)
        # self.layout.addWidget(HorizontalArrow())
        self.layout.addLayout(self.output_layout)

        self.layout.addStretch(1)

    def paintEvent(self, e):
        painter = QPainter(self)
        arrow(self.input_layout, self.output_layout, painter)
        # painter.end()


# goal_msg_dict = {"solved": _("Goal!"),
#                  "conditionally_solved": "",
#                  "under_construction": _("(to be solved...)")}


class TargetWidget(QWidget):
    """
    A widget for displaying a new target, with a target_msg (generally "Proof of
    ...") and a layout for displaying the proof of the new target.
    A disclosure triangle allows showing / hiding the proof.
    The layout is a 4x2 grid layout, with the following ingredients:
    triangle     |  "Proof of target"
    -----------------------------
    vertical bar | content_layout

    The content_layout contains
        - self.children_layout
        _ self.status_label
    The children_layout is designed to welcome the content of the
    logical_children of the WidgetGoalBlock to which the TargetWidget belongs,
    which will be gathered in a single widget.
    The status_label display the status of the target (goal solved?).
    Attribute html_msg is a callable that take a parameter color=True/False.
    """

    def __init__(self, parent_wgb, target: MathObject, target_msg: callable,
                 hidden=False):
        super().__init__()
        self.hidden = False
        self.target = target
        self.target_msg = target_msg
        self.parent_wgb = parent_wgb

        # Title and frame:
        self.triangle = DisclosureTriangle(self.toggle, hidden=False)
        self.triangle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.vert_bar = VertBar()
        self.title_label = RawLabelMathObject(html_msg=self.target_msg)
        self.title_label.setTextFormat(Qt.RichText)
        self.title_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Children, status:
        self.content_layout = QVBoxLayout()
        self.children_layout = QVBoxLayout()
        self.status_label = BlinkingLabel(self.status_msg)
        self.status_label.setStyleSheet("font-style: italic;")
        self.content_layout.addLayout(self.children_layout, 0)
        self.content_layout.addWidget(self.status_label, 1)
        # self.content_layout.addWidget(QLabel(""), 0, 2)  # Just to add stretch
        # self.content_layout.setColumnStretch(2, 1)
        self.status_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # self.children_wgt = []

        layout = QGridLayout()  # 2x3, five items
        layout.addWidget(self.triangle, 0, 0)
        layout.addWidget(self.vert_bar, 1, 0)
        layout.addWidget(self.title_label, 0, 1)
        layout.addWidget(QLabel(""), 0, 2)  # Just to add stretch
        layout.addLayout(self.content_layout, 1, 1)

        # layout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        layout.setColumnStretch(2, 1)
        layout.setAlignment(self.triangle, Qt.AlignHCenter)
        layout.setAlignment(self.vert_bar, Qt.AlignHCenter)
        self.main_layout = layout
        self.setLayout(layout)

        if hidden:
            self.toggle()

    def set_as_current_target(self, yes=True, blinking=True):
        if yes:
            self.title_label.set_bold(True)
            if blinking:
                self.status_label.start_blinking()
            else:
                self.status_label.stop_blinking()
        else:
            self.status_label.stop_blinking()
            self.set_status()
            self.title_label.set_bold(False)

    def toggle(self):
        """
        Toggle on / off the display of the content.
        """
        self.hidden = not self.hidden
        if self.hidden:  # Content_layout is the fourth layoutItem
            self.main_layout.takeAt(4)
            self.status_label.hide()
        else:
            self.main_layout.addLayout(self.content_layout, 1, 1)
            self.status_label.show()

    @property
    def status_msg(self) -> Optional[str]:
        if self.parent_wgb.is_recursively_solved():
            return _("Goal!")
        elif self.parent_wgb.is_conditionally_solved():
            return None
        else:
            return "( ... under construction... )"

    def set_status(self):
        if not self.status_msg:
            self.status_label.hide()
        else:
            self.status_label.show()
            self.status_label.setText(self.status_msg)


########################
# Abstract Goal blocks #
########################
class AbstractGoalBlock:
    """
    A generic class for dealing with the logical part of WidgetGoalBlock.
    An AbstractGoalBlock may have one target and two context lists,
    corresponding to new context element to be displayed before / after the
    target.
    - rw = None / "rw" / "implicit_rw".
    """
    merge = True  # Set to False to prevent any merging
    # goal_nb = 0

    def __init__(self, logical_parent, goal_node,
                 context1: [MathObject] = None,
                 target: MathObject = None, context2=None,
                 pure_context: tuple = None,
                 merge_up=False, merge_down=False, rw=None):

        self._context1 = context1 if context1 else []
        self._target = target
        self.context2 = context2 if context2 else []
        self.pure_context = pure_context if pure_context else ()

        self.logical_parent = logical_parent  # Usually set by parent
        self.logical_children = []
        # self.goal_nb = AbstractGoalBlock.goal_nb
        # AbstractGoalBlock.goal_nb += 1

        self.wanna_merge_up = merge_up
        self.wanna_merge_down = merge_down
        self.rw = rw

        self.goal_node = goal_node

    @property
    def goal_nb(self):
        return self.goal_node.goal_nb

    @property
    def step_nb(self):
        return self.goal_node.proof_step_nb

    def is_recursively_solved(self):
        return self.goal_node.is_recursively_solved()

    @property
    def merge_up(self):
        """
        True if self's content should be merged with parent's.
        """
        return (AbstractGoalBlock.merge
                and self.wanna_merge_up and self.logical_parent is not None
                and self.logical_parent.wanna_merge_down
                and self.isEnabled() == self.logical_parent.isEnabled())

    @property
    def merge_down(self):
        """
        True if self's content should be merged with (lonely) child's.
        """
        return (AbstractGoalBlock.merge
                and self.wanna_merge_down and len(self.logical_children) == 1
                and self.logical_children[0].wanna_merge_up
                and self.isEnabled() == self.logical_children[0].isEnabled())

    @property
    def context1(self):
        """
        Fusion self 's _context with child's context. Note that this will call
        recursively to all descendant's _context, as far as they are IntroWGB.
        """
        if self.merge_down:
            return self._context1 + self.logical_children[0].context1
        else:
            return self._context1

    @property
    def target(self):
        if self.merge_down:
            return self.logical_children[0].target
        else:
            return self._target

    def set_invisible(self, yes=True):
        """
        This is used for instance for WGB corresponding to end of proof,
        which are not supposed to be displayed.
        """
        self._is_visible = not yes

    def is_visible(self, reference_level=-1):
        if self._is_visible is not None:
            return self._is_visible

        if reference_level == -1:
            reference_level = WidgetGoalBlock.rw_level
        return self.rw_level <= reference_level
        # and not self.merge_up

    @property
    def target_msg(self) -> callable:
        if self.merge_down:
            return self.logical_children[0].target_msg  # No parentheses!
        else:
            return self.goal_node.html_msg  # (callable)

    def add_logical_child(self, child):
        self.logical_children.append(child)


######################
# Widget Goal blocks #
######################
class WidgetGoalBlock(QWidget, AbstractGoalBlock):
    """
    A generic widget for displaying an AbstractGoalNode. It has four
    optional widgets:
     - one widget for showing some context objects in a horizontal layout,
     - another one for showing a target,
     - and a third one for showing a second context list under the target.
     - If all of these are None, then maybe the fourth one,
     pure_context_widget, is not.

    If self has a target_widget, then it has a children_layout inside to
    welcome children (and descendants). If not, children are passed to
    logical_parent.

    Self can be "merged up": in this case its information are displayed by
    one of its ascendant, and self's layout is never set. In particular,
    self has no target_widget and no children_layout.

    More generally, self should have a target_widget (and a children_layout) iff
    it is actually displayed.

    self.children_widget reflects the children WidgetGoalBlock that should
    really be displayed in self's children_layout.
    """
    rw_level = 1  # show rw but not implicit rw  # FIXME: not implemented

    def __init__(self, logical_parent, goal_node,
                 context1=None, target=None, context2=None, pure_context=None,
                 merge_down=False, merge_up=False, rw_level=0):
        """
        rw_level =  0 if self is not a rw operation,
                    1 if self is a rw operation
                    2 if self is an implicit rw operation
        self will be displayed only if self.rw_level <= cls.rw_level.
        """
        assert (pure_context is None or (context1 is None and target is None
                                         and context2 is None))
        super().__init__()
        AbstractGoalBlock.__init__(self, logical_parent=logical_parent,
                                   goal_node=goal_node,
                                   context1=context1,
                                   target=target, context2=context2,
                                   pure_context=pure_context,
                                   merge_down=merge_down, merge_up=merge_up)
        # self should be displayed in self.parent_widget's children_layout
        self.parent_widget = None
        self._is_visible = None

        # Main widgets containers:
        self.pure_context_widget: Optional[PureContextWidget] = None
        self.context1_widget: Optional[ContextWidget] = None
        self.target_widget: Optional[TargetWidget] = None
        self.context2_widget: Optional[ContextWidget] = None
        self.children_widgets = []

        # Set main_layout with just one stretch
        self.main_layout = QVBoxLayout()
        self.main_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # self.parent_wgb = None  # Real parent, self should be in children_layout
        if self.logical_parent:  # Case of root
            self.logical_parent.add_logical_child(self)
        # if self.merge_up:
        #     self.logical_parent.update()
        # else:
        #     self.set_layout_without_children()
        # self.set_layout_without_children()
        # if not self.merge_up:
        #     self.set_layout_without_children()

    def __repr__(self):
        return self.context1, self.target, self.context2, self.pure_context

    @property
    def children_layout(self):
        if self.is_visible() and self.target_widget:
            return self.target_widget.children_layout
        else:
            return None

    def set_layout_without_children(self):
        """
        Populate main_layout from scratch, but does NOT take care of children.
        """

        # Clear target and context. Context2_widget is a child of target_widget.
        for wdg in (self.pure_context_widget,
                    self.target_widget,
                    self.context1_widget):
            if wdg and self.main_layout.indexOf(wdg) != -1:
                self.main_layout.removeWidget(wdg)
                wdg.hide()
            self.context1_widget = None
            self.context2_widget = None
            self.target_widget = None
            self.pure_context_widget = None

        # if self.merge_up:
        #     # Children must be added afterwards
        #     # self.logical_parent.set_layout_without_children()
        #     self.logical_parent.update()
        #     return
        if not self.is_visible or self.merge_up:
            return

        # Create and insert new widgets (at pole position, in reverse order):
        if self.pure_context:
            premises, operator, conclusions, type_ = self.pure_context
            if type_ == "operator":
                self.pure_context_widget = PureContextWidget(premises,
                                                             operator,
                                                             conclusions)
            else:
                self.pure_context_widget = SubstitutionContextWidget(premises,
                                                                     operator,
                                                                     conclusions
                                                                     )

            self.main_layout.insertWidget(0, self.pure_context_widget)

        if self.target:
            self.target_widget = TargetWidget(parent_wgb=self,
                                              target=self.target,
                                              target_msg=self.target_msg)
            self.main_layout.insertWidget(0, self.target_widget)

        if self.context1:
            self.context1_widget = ContextWidget(self.context1)
            self.main_layout.insertWidget(0, self.context1_widget)

        if self.context2 and self.target_widget:
            self.context2_widget = ContextWidget(self.context2)
            self.children_layout.addWidget(self.context2_widget)

    @property
    def displayable_children(self):
        """
        Return the list of children that should be displayed (either here or
        by an ascendant).
        """
        return [child for child in self.logical_children if
                child.is_visible() and not child.merge_up]

    @property
    def descendants_not_displayed_by_self(self):
        """
        Return the ordered list of descendants that are not displayed by their
        parent, and should be displayed by one of self's ascendants.
        """
        if self.children_layout and not self.merge_up:
            # Self will handle descendants
            return []
        else:
            descendants = []
            for child in self.logical_children:
                descendants.extend(child.descendants_not_displayed_by_self)
            return self.displayable_children + descendants

    @property
    def descendants_displayed_by_self(self):
        """
        Determine the ordered list of widgets that should be displayed in
        self.children_layout.
        """
        if not self.children_layout or self.merge_up:
            return []
        else:
            descendants = []
            for child in self.logical_children:
                descendants.extend(child.descendants_not_displayed_by_self)
            return self.displayable_children + descendants

    def add_widget_child(self, child):
        """
        Add the child if self has a children_layout, else call parent.This
        method is called when adding a logical child or by a child who
        delegates the display of its children widgets.
        """
        if not child.is_visible():
            return

        if self.children_layout:
            child.parent_widget = self
            self.children_widgets.append(child)
            self.children_layout.addWidget(child)
        else:
            self.logical_parent.add_widget_child(child)

    def add_logical_child(self, child):
        """
        This method must be called to add a new child, but NOT to reset an
        existing child.
        """
        super().add_logical_child(child)
        self.add_widget_child(child)
        # if self.target_widget:  # Maybe goal has been solved by child
        #     self.target_widget.set_status()

    def set_children_widgets(self):
        """
        Display directly descendants_to_be_displayed.
        """
        self.children_widgets = []
        if self.children_layout:
            for child in self.descendants_displayed_by_self:
                log.debug(f"Putting wgb {child.goal_nb} in {self.goal_nb}'s "
                          f"children layout")
                child.parent_widget = self
                self.children_widgets.append(child)
                self.children_layout.addWidget(child)

            log.debug(f"--> {self.children_layout.count()} displayed children")

    def is_conditionally_solved(self):
        """
        True if self is not solved but will be as soon as the descendant
        target are.
        """
        if self.is_recursively_solved() or not self.logical_children:
            return False
        if self.merge_down:
            return self.logical_children[0].is_conditionally_solved()
        else:
            return all([child.target or child.is_conditionally_solved() or
                        child.is_recursively_solved()
                        for child in self.logical_children])

    def enable_recursively(self, till_step_nb):
        """
        Recursively disable self from the indicated goal_node nb.
        Note that tree must be updated to adapt merging.
        """
        if self.step_nb > till_step_nb:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
        for child in self.logical_children:
            child.enable_recursively(till_step_nb)

    def check_context1(self):
        """
        Check if context1_widget displays the content of context1.
        """
        if not self.context1:
            return self.context1_widget is None
        elif not self.context1_widget:
            return False

        if len(self.context1) != len(self.context1_widget.math_objects):
            return False
        tests = [math_obj in self.context1 for math_obj in
                 self.context1_widget.math_objects]
        return all(tests)

    def check_context2(self):
        """
        Check if context1_widget displays the content of context1.
        """
        if not self.context2:
            return self.context2_widget is None
        elif not self.context2_widget:
            return False
        if len(self.context2) != len(self.context2_widget.math_objects):
            return False
        tests = [math_obj in self.context2 for math_obj in
                 self.context2_widget.math_objects]
        return all(tests)

    def check_target(self):
        """
        Check if target_widget displays the content of target.
        """
        if not self.target_widget:
            return self.target is None
        else:
            return self.target == self.target_widget.target

    def check_children(self):
        """
        Check if children_widget displays descendants_to_be_displayed.
        """
        return self.children_widgets == self.descendants_displayed_by_self

    def is_up_to_date(self):
        """
        Check if display is coherent with datas. Specifically,
        compare the contents of
        - context1 and context1_widget,
        - target and target_widget,
        - context2 and context2_widget,
        - descendants_to_be_displayed and children_widgets.
        """
        return all([self.check_context1(),
                    self.check_target(),
                    self.check_context2(),
                    self.check_children()])

    def update_display(self):
        # log.debug(f"Updating WGB for nb {self.goal_nb}: {self.goal_node}...")
        # log.debug(f"merge down: {self.merge_down}, enabled: {self.isEnabled()}")
        if self.target_widget:
            self.target_widget.set_status()
        if self.is_up_to_date():
            # log.debug("... is up to date")
            return
        else:
            # log.debug("...setting layout and children")
            self.set_layout_without_children()
            self.set_children_widgets()

    def update_display_recursively(self):
        self.update_display()
        for child in self.logical_children:
            child.update_display_recursively()

    def set_as_current_target(self, yes=True, blinking=True):
        """
        If self has a target_widget, then its target will be set as current.
        If not, then self is inside a children_layout, of some target_widget
        of some ascendant, and this target_widget should be set as current.
        """
        if self.target_widget:
            self.target_widget.set_as_current_target(yes, blinking)
        elif yes:
            self.logical_parent.set_as_current_target(True, blinking)
        # if self.target_widget and not self.merge_up:
        #     self.target_widget.set_as_current_target(yes)
        #     if yes:
        #         print(f"Current target: {self.goal_nb}")
        # else:
        #     self.logical_parent.set_as_current_target(yes)

    def set_current_target_recursively(self, goal_nb, blinking=True):
        if self.goal_nb == goal_nb:
            self.set_as_current_target(yes=True, blinking=blinking)
        else:
            self.set_as_current_target(False)

        for child in self.logical_children:
            child.set_current_target_recursively(goal_nb, blinking=blinking)


class GoalSolvedWGB(WidgetGoalBlock):
    """
    This WGB reflects GoalNode.goal_solved, a fake goal node with target
    "goal solved". It should remain invisible.
    """
    def __init__(self, logical_parent, goal_node):
        super().__init__(logical_parent, goal_node)
        self.set_invisible()


class ByCasesWGB(WidgetGoalBlock):
    """
    Display of one sub-case of a proof by cases.
    """
    def __init__(self, logical_parent, goal_node, target, context):
        super().__init__(logical_parent, goal_node,
                         target=target, context2=context,
                         merge_down=False, merge_up=False)


class IntroWGB(WidgetGoalBlock):
    """
    Display of introduction of elements to prove universal props.
    Try to merge with parent and child.
    """
    def __init__(self, logical_parent, goal_node, context=None, target=None):
        super().__init__(logical_parent, goal_node, context, target,
                         merge_down=True, merge_up=True)


class IntroImpliesWGB(WidgetGoalBlock):
    """
    Display of introduction of elements to prove universal props or
    implications. Try to merge with parent but not child.
    """
    def __init__(self, logical_parent, goal_node, context=None, target=None):
        super().__init__(logical_parent, goal_node, context, target,
                         merge_down=False, merge_up=True)


class PureContextWGB(WidgetGoalBlock):

    def __init__(self, logical_parent, goal_node,
                 premises, operator, conclusions):
        super().__init__(logical_parent, goal_node,
                         pure_context=(premises, operator, conclusions,
                                       "operator"))


class SubstitutionWGB(WidgetGoalBlock):

    def __init__(self, logical_parent, goal_node,
                 premises, definition, conclusions):
        super().__init__(logical_parent, goal_node,
                         pure_context=(premises, definition, conclusions,
                                       "substitution"))


###############
# Main Window #
###############
class ProofTreeWindow(QWidget):
    """
    A widget for displaying the proof tree.
    """

    def __init__(self, context=None, target=None):
        """
        Context and target are the elements of the initial goal, if any.
        """
        super().__init__()
        self.setWindowTitle("Proof Tree")
        self.current_wgb = None
        settings = QSettings("deaduction")
        if settings.value("proof_tree/geometry"):
            self.restoreGeometry(settings.value("proof_tree/geometry"))

        main_layout = QVBoxLayout()
        self.main_window = QScrollArea()
        main_layout.addWidget(self.main_window)

        if context or target:
            main_block = WidgetGoalBlock(context, target)
            self.set_main_block(main_block)
        else:
            self.main_block: Optional[WidgetGoalBlock] = None

        self.setLayout(main_layout)

        self.set_style_sheet()

    def set_style_sheet(self):
        color_var = cvars.get("display.color_for_variables")
        color_prop = cvars.get("display.color_for_props")
        color_op = cvars.get("display.color_for_operator_props")
        new_border_width = "2px"
        old_border_width = "1px"
        op_border_width = "4px"
        old_border_style = "dotted"
        self.setStyleSheet("QLabel#new_obj:enabled {padding: 5px;"
                               f"border-width: {new_border_width};"
                               f"border-color: {color_var};"
                               "border-style: solid;"
                               "border-radius: 10px;}"
                           "QLabel#new_obj:!enabled {padding: 5px;"
                                f"border-width: {new_border_width};"
                                "border-color: lightgrey;"
                                "border-style: solid;"
                                "border-radius: 10px;}"
                           "QLabel#old_obj:enabled {padding: 5px;"
                               f"border-width: {old_border_width};"
                               f"border-color: {color_var};"
                               f"border-style: {old_border_style};"
                               "border-radius: 10px;}"
                           "QLabel#old_obj:!enabled {padding: 5px;"
                               f"border-width: {old_border_width};"
                               "border-color: lightgrey;"
                               f"border-style: {old_border_style};"
                               "border-radius: 10px;}"
                           "QLabel#new_prop:enabled {padding: 5px;"
                               f"border-width: 2px;"
                               f"border-color: {color_prop};"
                               "border-style: solid;"
                               "border-radius: 10px;}"
                           "QLabel#new_prop:!enabled {padding: 5px;"
                               f"border-width: {new_border_width};"
                               "border-color: lightgrey;"
                               "border-style: solid;"
                               "border-radius: 10px;}"
                           "QLabel#old_prop:enabled {padding: 5px;"
                               f"border-width: {old_border_width};"
                               f"border-color: {color_prop};"
                               f"border-style: {old_border_style};"
                               "border-radius: 10px;}"
                           "QLabel#old_prop:!enabled {padding: 5px;"
                               f"border-width: {old_border_width};"
                               "border-color: lightgrey;"
                               f"border-style: {old_border_style};"
                               "border-radius: 10px;}"
                           "OperatorLMO:enabled {padding: 5px;"
                               f"border-width: {op_border_width};"
                               f"border-color: {color_op};"
                               "border-style: solid;"
                               "border-radius: 10px;}"
                           "OperatorLMO:!enabled {padding: 5px;" 
                               f"border-width: {op_border_width};"
                               "border-color: lightgrey;"
                               "border-style: solid;"
                               "border-radius: 10px;}"
                           )

    def set_main_block(self, block: WidgetGoalBlock):
        self.main_block = block
        self.main_window.setWidget(block)
        self.current_wgb = block
        # self.main_block.set_as_current_target()

    def update_display(self):
        if self.main_block:
            self.main_block.update_display_recursively()

    def set_current_target(self, goal_nb, blinking=True):
        self.main_block.set_current_target_recursively(goal_nb, blinking)

    def closeEvent(self, event):
        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("proof_tree/geometry", self.saveGeometry())
        event.accept()
        self.hide()
        # TODO: save tree state

    @Slot()
    def toggle(self):
        self.setVisible(not self.isVisible())


##############
# Controller #
##############
# if __name__ != "__main__":
def widget_goal_block(parent_widget: Optional[WidgetGoalBlock],
                      goal_node: GoalNode) -> WidgetGoalBlock:
    """
    All WidgetGoalBlock to be inserted in the ProofTreeWidget should be
    created by calling this method.
    """
    # FIXME: goal solved case!!
    new_context = goal_node.goal.new_context
    target = goal_node.goal.target.math_type
    if goal_node.is_intro:
        wgb = IntroWGB(logical_parent=parent_widget, goal_node=goal_node,
                       context=new_context, target=target)
    elif goal_node.is_implies:
        wgb = IntroImpliesWGB(logical_parent=parent_widget,
                              goal_node=goal_node,
                              context=new_context, target=target)
    elif goal_node.is_by_cases:
        wgb = ByCasesWGB(logical_parent=parent_widget,
                         goal_node=goal_node,
                         context=new_context, target=target)
    elif goal_node.is_pure_context:
        premises, operator, conclusions = goal_node.is_pure_context
        wgb = PureContextWGB(parent_widget, goal_node,
                             premises, operator, conclusions)
    elif goal_node.is_all_goals_solved():  # or goal_node.is_goals_solved():
        wgb = GoalSolvedWGB(parent_widget, goal_node)
    elif goal_node.is_context_substitution:  # TODO: clean this up
        if goal_node.parent.statement:
            definition = goal_node.parent.statement.pretty_name
            premises = goal_node.parent.selection
        else:
            definition = goal_node.parent.selection[0]
            premises = goal_node.parent.selection[1:]
        conclusions = goal_node.goal.new_context

        wgb = SubstitutionWGB(parent_widget, goal_node,
                              premises, definition, conclusions)
    else:
        wgb = WidgetGoalBlock(logical_parent=parent_widget,
                              goal_node=goal_node,
                              target=target, context2=new_context)

    return wgb


def update_from_node(wgb: WidgetGoalBlock, gn: GoalNode):
    """
    Recursively update the WidgetProofTree from (under) the given node.
    We have the following alternative:
    - either there is a new child goal_node for which we will create a
    child wgb;
    - or some child_wgb does not match the corresponding child goal_node:
    in this case all children_wgb should be deleted and new ones will be
    created.
    - or all children wgb match corresponding children goal_nodes.
    """
    pairs = list(zip(wgb.logical_children, gn.children_goal_nodes))
    if (len(wgb.logical_children) > len(gn.children_goal_nodes)
        or any([child_wgb.goal_node is not child_gn
                for child_wgb, child_gn in pairs])):
        # Case 1: Some child_wgb is obsolete: reset all children
        wgb.logical_children = []
        wgb.set_layout_without_children()
        for child_gn in gn.children_goal_nodes:
            child_wgb = widget_goal_block(wgb, child_gn)
        pairs = zip(wgb.logical_children, gn.children_goal_nodes)

    elif len(wgb.logical_children) < len(gn.children_goal_nodes):
        # Case 2: new children
        new_index = len(wgb.logical_children)
        new_children_gn = gn.children_goal_nodes[new_index:]
        for child_gn in new_children_gn:
            child_wgb = widget_goal_block(wgb, child_gn)
        pairs = zip(wgb.logical_children, gn.children_goal_nodes)

    # In any case, recursively update children
    for child_wgb, child_gn in pairs:
        update_from_node(child_wgb, child_gn)


class ProofTreeController:
    """
    A class to create and update a ProofTreeWindow that reflects a ProofTree.
    """
    def __init__(self):
        self.proof_tree = None
        self.proof_tree_window = ProofTreeWindow()

    def set_proof_tree(self, proof_tree):
        self.proof_tree = proof_tree

    def enable(self, till_step_nb):
        """
        Enable all WGB until a given goal_nb, disabled the others.
        Disabled WGB will be displayed in light grey. This is used when usr
        moves in the history.
        """
        main_block = self.proof_tree_window.main_block
        main_block.enable_recursively(till_step_nb=till_step_nb)

    def is_at_end(self):
        return self.proof_tree.is_at_end()

    def update(self):
        if not self.proof_tree.root_node:
            return
        elif not self.proof_tree_window.main_block:
            main_block = widget_goal_block(None,
                                           self.proof_tree.root_node)
            self.proof_tree_window.set_main_block(main_block)

        current_goal_node = self.proof_tree.current_goal_node
        # Adapt display of ProofTreeWindow to ProofTree:
        log.info("Updating proof tree widget from proof tree.")
        update_from_node(self.proof_tree_window.main_block,
                         self.proof_tree.root_node)

        # Enable / disable to adapt to history move:
        # proof_tree.next_proof_step_nb is the first proof_step that will be
        # deleted if usr send an action from here
        proof_step_nb = self.proof_tree.next_proof_step_nb
        if proof_step_nb is not None:
            log.debug(f"Enabling till {proof_step_nb-1}")
            self.enable(till_step_nb=proof_step_nb-1)
        else:
            self.enable(till_step_nb=100000)
        log.info("Updating display")

        # Update display:
        self.proof_tree_window.update_display()

        # Set current target:
        log.info("Setting current target")
        goal_nb = current_goal_node.goal_nb
        self.proof_tree_window.set_current_target(goal_nb,
                                                  blinking=self.is_at_end())

    def wgb_from_goal_nb(self, goal_nb: int, from_wgb=None) -> \
            WidgetGoalBlock:
        """ For debugging only."""
        if not from_wgb:
            from_wgb = self.proof_tree_window.main_block
        if from_wgb.goal_nb == goal_nb:
            return from_wgb
        for child in from_wgb.logical_children:
            wgb = self.wgb_from_goal_nb(goal_nb, from_wgb=child)
            if wgb:
                return wgb


def main():
    app = QApplication()
    wdg = QWidget()
    layout = QVBoxLayout()
    label_bf = QLabel("TOTO est gras")
    label_bf.setStyleSheet("font-weight: bold")
    # label_bf.setStyleSheet("{font-weight: bold;}")
    label = QLabel("TOTO est maigre")
    layout.addWidget(label_bf)
    layout.addWidget(label)
    wdg.setLayout(layout)
    wdg.show()
    # pcw = HorizontalArrow(100)
    # pcw = SubstitutionArrow("f(x)=y mais aussi TOTO le clown")
    # pcw = SubstitutionContextWidget(["y dans A"], "f(x)=y et aussi toto",
    #                                 ["f(x) dans A"])

    # main_window = ProofTreeWindow()
    # AbstractGoalBlock.merge = True
    #
    # context0 = ["X", "Y", "f"]
    # target0 = "f surjective ⇒ (∀A ⊂ Y, ∀A' ⊂ Y, ( f⁻¹(A) ⊂ f⁻¹(A') ⇒ A ⊂ A' ) )"
    # main_block = WidgetGoalBlock(logical_parent=None, goal_node = None,
    #                              context1=context0, target=target0)
    #
    # main_window.set_main_block(main_block)
    # main_window.show()
    #
    # # TODO: change to successive IntroBlocks:
    # intro1 = IntroImpliesWGB(logical_parent=main_block,
    #                          context=["f surjective"],
    #                          target="(∀A ⊂ Y, ∀A' ⊂ Y, ( f⁻¹(A) ⊂ f⁻¹(A')"
    #                                 " ⇒ A ⊂ A' ) )")
    # intro2a = IntroWGB(logical_parent=intro1,
    #                    context=["A"],
    #                    target="∀A' ⊂ Y, f⁻¹(A) ⊂ f⁻¹(A') ⇒ A ⊂ A'")
    # intro2b = IntroWGB(logical_parent=intro2a,
    #                    context=["A'"], target="f⁻¹(A) ⊂ f⁻¹(A') ⇒ A ⊂ A'")
    # intro3 = IntroImpliesWGB(logical_parent=intro2b,
    #                          context=["f⁻¹(A) ⊂ f⁻¹(A')"], target="A ⊂ A'")
    #
    # intro4 = IntroWGB(logical_parent=intro3,
    #                   context=["y"], target="y ∈ A => y ∈ A'")
    # intro5 = IntroWGB(logical_parent=intro4,
    #                          context=["y ∈ A"], target="y ∈ A'")
    # # intro2b.show()
    #
    #
    # operator = [(["y"], "f surjective", ["x", "y = f(x)"]),
    #             (["y ∈ A"], "y = f(x)", ["f(x) ∈ A"]),
    #             (["f(x) ∈ A"], "definition image réciproque", ["x ∈ f⁻¹(A)"]),
    #             (["x ∈ f⁻¹(A)"], "f⁻¹(A) ⊂ f⁻¹(A')", ["x ∈ f⁻¹(A')"]),
    #             (["x ∈ f⁻¹(A')"], "definition image réciproque", ["f(x) ∈ A'"]),
    #             (["f(x) ∈ A'"], "y = f(x)", ["y ∈ A'"])]
    # previous_block = intro5
    # # op = operator[0]
    # # pure_block0 = PureContextWGB(logical_parent=None,
    # #                              premises=op[0],
    # #                              operator=op[1],
    # #                              conclusions=op[2])
    # # pure_block0.show()
    # for op in operator:
    #     pure_block = PureContextWGB(previous_block,
    #                                 premises=op[0],
    #                                 operator=op[1],
    #                                 conclusions=op[2])
    #     previous_block.add_logical_child(pure_block)
    #     previous_block = pure_block
    #
    # # case_block1 = ByCasesWGB(logical_parent=previous_block,
    # #                          context=["y ∈ A"], target="First case: y ∈ A")
    # # case_block2 = ByCasesWGB(logical_parent=previous_block,
    # #                          context=["y ∉ A"], target="Second case: y ∉ A")
    # # case_block1.show()
    # # previous_block.set_children([case_block1, case_block2])
    # #
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

