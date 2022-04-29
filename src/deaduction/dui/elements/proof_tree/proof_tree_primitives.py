"""
# Primitives for the proof tree widget. #

Author(s)     : F Le Roux
Maintainer(s) : F. Le Roux
Created       : 04 2022 (creation)
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

import deaduction.pylib.config.vars as cvars
import deaduction.pylib.config.dirs as cdirs

global _

if __name__ != "__main__":
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
    # FIXME: obsolete
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

    # painter.begin()  # FIXME: already started?
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


def rectangle(item):
    if isinstance(item, QWidget):
        return item.rect()
    elif isinstance(item, QLayout):
        return item.contentsRect()


def arrow(item1, item2, painter):
    """
    Paint an arrow between two widgets.
    """
    rect1 = rectangle(item1)
    rect2 = rectangle(item2)
    if rect1.right() < rect2.left():
        origin = mid_right(rect1)
        end = mid_left(rect2)
        paint_arrow(origin, end, painter)


class HorizontalArrow(QWidget):
    def __init__(self, width=50, arrow_height=4, style=Qt.SolidLine):
        super(HorizontalArrow, self).__init__()
        self.style = style
        self.width = width
        self.setFixedWidth(width)
        self.setFixedHeight(arrow_height*3)
        self.pen_width = 1
        self.arrow_height = arrow_height + self.pen_width

    def color(self):
        if self.isEnabled():
            return cvars.get("display.color_for_operator_props")
        else:
            return "lightgrey"

    def paintEvent(self, e):
        painter = QPainter(self)
        pen = QPen()
        pen.setColor(QColor(self.color()))
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
        brush = QBrush(self.color(), Qt.SolidPattern)
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
        # self.setObjectName("operator")


class RwItemLMO(RawLabelMathObject):
    """
    Display a MathObject which is a property operating on other objects.
    """

    def __init__(self, math_object):
        super().__init__(math_object)
        # self.setObjectName("operator")


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
    def __init__(self, rw_item):
        if isinstance(rw_item, tuple):  # FIXME: this is just for now...
            rw_item = rw_item[0] + " " + rw_item[1]

        super().__init__()
        layout = QVBoxLayout()
        layout.addStretch(1)
        # Label
        label_layout = QHBoxLayout()
        self.rw_label = RwItemLMO(rw_item)
        # self.rw_label = OperatorLMO(rw_item)
        self.rw_label.show()
        self.label_width = self.rw_label.geometry().width()
        self.rw_label.hide()
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
        fake_label = RwItemLMO(rw_item)
        size_pol = fake_label.sizePolicy()
        size_pol.setRetainSizeWhenHidden(True)
        fake_label.setSizePolicy(size_pol)
        layout.addWidget(fake_label)
        layout.addStretch(1)
        self.setLayout(layout)
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
        self.type_ = "operator"

        assert conclusions
        output_layout = LayoutMathObjects(conclusions, align="left")

        # Input -> Operator -> output:
        if premises:
            input_layout = LayoutMathObjects(premises, align="right", new=False)
            self.layout.addLayout(input_layout)
            self.layout.addWidget(HorizontalArrow())

        if operator:
            operator_wdg = LayoutOperator(operator)
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

    def __init__(self, premises, rw_item, conclusions):
        """
        rw_item is either a math_object, or a string, or a couple of
        MathObjects/strings to be written above and below the arrow.
        """

        #FIXME!!!!
        super().__init__([])
        self.premises = premises
        self.operator = rw_item
        self.conclusions = conclusions
        self.type_ = "substitution"

        self.input_layout = LayoutMathObjects(premises, align="right",
                                              new=False)
        self.output_layout = LayoutMathObjects(conclusions, align="left")

        self.arrow_wdg = SubstitutionArrow(rw_item)

        # Input -> Operator -> output:
        self.layout.addLayout(self.input_layout)
        # self.layout.addWidget(HorizontalArrow())
        self.layout.addWidget(self.arrow_wdg)
        # self.layout.addWidget(HorizontalArrow())
        self.layout.addLayout(self.output_layout)

        self.layout.addStretch(1)

    # def paintEvent(self, e):
    #     painter = QPainter(self)
    #     arrow(self.input_layout, self.output_layout, painter)


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
    Attribute html_msg is a callable that takes a parameter color=True/False.
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
            if self.parent_wgb.is_sorry():
                return _("(admitted)")
            else:
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

    def merge_down(self):
        """
        When a target undergoes a substitution, it merges down with the new
        target block. This method then turns the layout to display into

        triangle     |  "Proof of target"
        -----------------------------
        vertical bar | arrow_layout
        -----------------------------
        children_layout (which then contains a new target block).

        The status_label is not displayed.
        """
        pass




