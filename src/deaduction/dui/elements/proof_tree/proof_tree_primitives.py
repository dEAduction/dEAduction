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
from PySide2.QtWidgets import (QFrame, QLayout,
                               QHBoxLayout, QVBoxLayout, QGridLayout,
                               QWidget, QLabel, QSizePolicy)
from PySide2.QtCore import Qt, QRect, QPoint, QTimer, QPointF
from PySide2.QtGui import QColor, QPainter, QPolygon, QPen, QBrush, QPainterPath

import deaduction.pylib.config.vars as cvars

global _

if __name__ != "__main__":
    from deaduction.pylib.mathobj import MathObject, ContextMathObject
    from deaduction.pylib.coursedata import Statement
else:
    def _(x):
        return x

    class MathObject:
        pass

    class GoalNode:
        pass

    class Statement:
        pass


log = logging.getLogger(__name__)


def paint_layout(painter, item, item_depth=0, max_depth=10):
    """
    For debugging. Display all sub-widgets geometries.
    """
    if isinstance(item, QWidget):
        layout = item.layout()
        # geometry = item.geometry()
        # contents = item.contentsRect()
    elif isinstance(item, QLayout):
        layout = item
        # geometry = item.contentsRect()
    else:
        return
    if layout and item_depth < max_depth:
        for idx in range(layout.count()):
            layout_item = layout.itemAt(idx)
            paint_layout(painter, layout_item, item_depth+1)
    pen = QPen()
    pen.setColor("blue")
    pen.setWidth(2)
    painter.setPen(pen)
    painter.drawRect(item.contentsRect())
    # pen.setColor(QColor("purple"))
    pen.setColor("purple")
    pen.setWidth(1)
    painter.setPen(pen)
    color = QColor()
    color.setHsv((item_depth+1)*50, 100, 255-(item_depth+1) * 50)
    brush = QBrush(color)
    # painter.setBrush(brush)
    painter.drawRect(item.geometry())


class BlinkingLabel(QLabel):
    def __init__(self, text: callable, goal_nb=-1):
        super(BlinkingLabel, self).__init__(text())
        self.goal_nb = goal_nb
        self.text = text
        self.flag = None
        self.timer = QTimer(self, interval=1000)
        self.timer.timeout.connect(self.blink)
        # self.start_blinking()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._is_deactivated = False
        self.disclosed = True

    def start_blinking(self):
        """
        The size policy is modified to retain size, to avoid layout changes
        when blinking. It must be reset to retainSizeWhenHidden(False) when
        blinking stops, in case the msg will be hidden.
        """
        sp = self.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.setSizePolicy(sp)
        self.flag = True
        self.set_bold(True)
        self.timer.start()
        # log.debug(f"Starting blinking gn {self.goal_nb}, text = {self.text}")

    def stop_blinking(self):
        # log.debug(f"Stop blinking gn {self.goal_nb}")
        sp = self.sizePolicy()
        sp.setRetainSizeWhenHidden(False)
        self.setSizePolicy(sp)
        self.set_bold(False)
        self.timer.stop()

    def blink(self):
        # self.setText(" "*len(self.text()) if self.flag else self.text())
        if self.flag:
            self.hide()
        elif self.disclosed:
            self.show()
        self.flag = not self.flag
        # log.debug(f"Blinking gn {self.goal_nb}, text = {self.text}")

    def deactivate(self, yes=True):
        self._is_deactivated = yes

    def update_text(self):
        self.setText(self.text())

    def set_msg(self):
        if not self.text():
            self.hide()
        elif not self._is_deactivated:
            self.update_text()
            self.show()

    def set_bold(self, yes=True):
        self.bold = yes
        if yes:
            self.setStyleSheet("font-weight: bold;")
        else:
            self.setStyleSheet("")


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


def mid_top(rect: QRect) -> QPoint:
    return middle(rect.topRight(), rect.topLeft())


def mid_bottom(rect: QRect) -> QPoint:
    return middle(rect.bottomRight(), rect.bottomLeft())


def paint_arrow(origin, end, painter: QPainter,
                arrow_height=4, style=Qt.SolidLine,
                color=None, pen_width=1,
                direction="horizontal"):
    """
    Display a straight arrow.
    """
    if not color:
        color = cvars.get("display.color_for_operator_props")

    # Coordinates
    vect_x = QPoint(arrow_height, 0)
    vect_y = QPoint(0, arrow_height)
    if direction == "horizontal":
        end = end - vect_x
        upper_vertex = end - 2 * vect_x - vect_y
        lower_vertex = end - 2 * vect_x + vect_y
        end_line = end - 2*vect_x
    elif direction == "vertical":
        end = end - vect_y
        upper_vertex = end - 2 * vect_y + vect_x
        lower_vertex = end - 2 * vect_y - vect_x
        end_line = end - 2*vect_y

    # Pen
    pen = QPen()
    pen.setColor(QColor(color))
    pen.setWidth(pen_width)
    pen.setJoinStyle(Qt.MiterJoin)
    pen.setCapStyle(Qt.FlatCap)
    painter.setPen(pen)

    # Draw line
    pen.setStyle(style)
    painter.setPen(pen)
    painter.drawLine(origin, end_line)

    # Draw arrow
    brush = QBrush(color, Qt.SolidPattern)
    painter.setBrush(brush)
    pen.setStyle(Qt.SolidLine)
    pen.setWidth(1)
    painter.setPen(pen)
    triangle = QPolygon([end, upper_vertex, lower_vertex, end])
    painter.drawPolygon(triangle)
    painter.end()


def points_for_curved_arrow(origin_wdg: QWidget, end_wdg: QWidget,
                            parent_wdg: QWidget) -> [QPoint]:
    """
    Compute points for tracing a curved arrow from origin_wdg to end_wdg
    within parent_wdg.
    """
    rel_origin = mid_bottom(origin_wdg.rect())
    origin = origin_wdg.mapTo(parent_wdg, rel_origin)
    rel_end = mid_top(end_wdg.rect())
    end = end_wdg.mapTo(parent_wdg, rel_end)
    mid = middle(origin, end)
    control1 = QPoint(origin.x(), mid.y())
    control2 = QPoint(end.x(), mid.y())

    return [origin, control1, mid, control2, end]


def paint_curved_arrow(points: [QPoint],
                       painter: QPainter,
                       arrow_height=4, style=Qt.SolidLine,
                       color=None, pen_width=1):
    """
    Use painter to draw a (quadratic Bezier) curved arrow.
    """
    assert len(points) == 5
    if color is None:
        color = "Black"
    path = QPainterPath()
    path.moveTo(points[0])
    path.quadTo(points[1], points[2])
    path.quadTo(points[3], points[4])
    pen = QPen(QColor(color))
    pen.setStyle(Qt.DotLine)
    painter.setPen(pen)
    painter.drawPath(path)


def rectangle(item):
    if isinstance(item, QWidget):
        return item.rect()
    elif isinstance(item, QLayout):
        return item.contentsRect()


class CurvedArrow:
    def __init__(self, origin_wdg: QWidget, end_wdg: QWidget, parent):
        # super().__init__(parent=parent)
        color_var = cvars.get("display.color_for_variables")
        color_prop = cvars.get("display.color_for_props")
        self.origin_wdg = origin_wdg
        self.end_wdg = end_wdg
        self.parent_wdg = parent
        self.color = color_prop if self.origin_wdg.is_prop else color_var
        # rel_origin = mid_bottom(origin_wdg.rect())
        # self.origin = origin_wdg.mapTo(parent, rel_origin)
        # rel_end = mid_top(end_wdg.rect())
        # self.end = end_wdg.mapTo(parent, rel_end)
        #
        # # top_left = QPoint(min(self.origin.x(), self.end.x()),
        # #                   self.origin.y())
        # # bottom_right = QPoint(max(self.origin.x(), self.end.x()),
        # #                       self.end.y())
        # #
        # # rect = QRect(top_left, bottom_right)
        # # self.setGeometry(parent.geometry())
        # self.mid = middle(self.origin, self.end)
        # self.control1 = QPoint(self.origin.x(), self.mid.y())
        # self.control2 = QPoint(self.end.x(), self.mid.y())

        # rel_origin = mid_bottom(self.origin_wdg.rect())
        # origin = self.origin_wdg.mapTo(self.parent_wdg, rel_origin)
        # rel_end = mid_top(self.end_wdg.rect())
        # end = self.end_wdg.mapTo(self.parent_wdg, rel_end)
        # top_left = QPoint(min(origin.x(), end.x()), origin.y())
        # bottom_right = QPoint(max(origin.x(), end.x()), end.y())
        #
        # rect = QRect(top_left, bottom_right)
        # self.setGeometry(rect)
        # mid = middle(origin, end)
        # control1 = QPoint(origin.x(), mid.y())
        # control2 = QPoint(end.x(), mid.y())

        # self.points = [self.origin, self.control1, self.mid,
        #                self.control2, self.end]

    # def paintEvent(self, event):
    #     rel_origin = mid_bottom(self.origin_wdg.rect())
    #     origin = self.origin_wdg.mapTo(self.parent_wdg, rel_origin)
    #     rel_end = mid_top(self.end_wdg.rect())
    #     end = self.end_wdg.mapTo(self.parent_wdg, rel_end)
    #     mid = middle(origin, end)
    #     control1 = QPoint(origin.x(), mid.y())
    #     control2 = QPoint(end.x(), mid.y())
    #
    #     points = [origin, control1, mid, control2, end]
    #     self.setGeometry(self.parent_wdg.geometry())
    #
    #     # points = [self.origin, self.control1, self.mid, self.control2, self.end]
    #     painter = QPainter(self)
    #     paint_curved_arrow(points, painter)


class VerticalArrow(QWidget):
    def __init__(self, minimum_height=60, arrow_width=4, style=Qt.DashLine):
        super(VerticalArrow, self).__init__()
        self.setMinimumHeight(minimum_height)
        self.setFixedWidth(arrow_width*3)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.pen_width = 1
        self.arrow_width = arrow_width + self.pen_width
        self.style = style

    def color(self):
        if self.isEnabled():
            return cvars.get("display.color_for_operator_props")
        else:
            return "lightgrey"

    def paintEvent(self, e):
        painter = QPainter(self)

        rectangle = self.rect()
        origin = mid_top(rectangle)
        end = mid_bottom(rectangle)

        paint_arrow(origin=origin, end=end, painter=painter,
                    arrow_height=self.arrow_width, style=self.style,
                    color=self.color(), direction="vertical")


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

        rectangle = self.rect()

        origin = mid_left(rectangle)
        end = mid_right(rectangle)
        paint_arrow(origin=origin, end=end, painter=painter,
                    arrow_height=self.arrow_height, style=self.style,
                    color=self.color(),
                    direction="horizontal")

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

    Param math_object may be a MathObject instance or a string or a Statement.
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

        # self.setText(self.txt())

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
            txt = self.html_msg(use_color=self.isEnabled())
            if isinstance(self, ProofTitleLabel) and self.disclosed:
                txt += _(":")
            return pre + txt + post

        if isinstance(self.math_object, str):
            return self.math_object
        elif isinstance(self.math_object, Statement):
            return self.math_object.pretty_name
        elif isinstance(self.math_object, MathObject):
            math_object = (self.math_object.math_type if self.is_prop
                           else self.math_object)
            txt = math_object.to_display(format_="html",
                                         use_color=self.isEnabled())
        return txt

    def update(self):
        self.setText(self.txt())

    def changeEvent(self, event) -> None:
        """
        In case object is enabled/disabled, change to properly display colored
        variables.
        """
        self.setText(self.txt())
        event.accept()


class ProofTitleLabel(RawLabelMathObject):
    """
    A QLabel to display a mgs like "Proof of ...".
    The colon is added on top of html_msg by super class RawLabelMathObject
    iff self.disclosed is True.
    """
    def __init__(self, html_msg):
        super().__init__(html_msg=html_msg)
        self.disclosed = True


class GenericLMO(RawLabelMathObject):
    """
    A class for displaying MathObject inside a frame. math_object can be a
    MathObject instance or a string (e.g. a statement name).
    """
    def __init__(self, math_object, new=True):
        super().__init__(math_object)
        # The following is used in the style sheet
        is_new = "new" if new else "old"
        is_prop = "prop" if self.is_prop else "obj"
        self.setObjectName(is_new + "_" + is_prop)
        if isinstance(math_object, MathObject) and not self.is_prop:
            # print("Setting tooltip")
            tooltip = math_object.math_type_to_display(format_="utf8")
            self.setToolTip(tooltip)


class LayoutMathObject(QHBoxLayout):
    """
    Display a LabelMathObject inside a h-layout so that the box is not too big.
    """

    def __init__(self, math_object, align=None, new=True):
        super().__init__()
        self.math_wdg = GenericLMO(math_object, new=new)

        if align in (None, "right"):
            self.addStretch(1)
        self.addWidget(self.math_wdg)
        if align in (None, "left"):
            self.addStretch(1)

    @property
    def math_object(self):
        return self.math_wdg.math_object


class LayoutMathObjects(QVBoxLayout):
    """
    Display a vertical pile of LayoutMathObjects.
    """

    def __init__(self, math_objects, align=None, new=True):
        super().__init__()
        # self.math_objects = math_objects
        # self.lyt_math_objects = []
        self.addStretch(1)
        for math_object in math_objects:
            lyt = LayoutMathObject(math_object, align=align, new=new)
            # self.lyt_math_objects.append(lyt)
            self.addLayout(lyt)
        self.addStretch(1)

    @property
    def nb_objects(self):
        return self.layout().count()-2

    @property
    def lyt_math_objects(self):
        lyt = self.layout()
        return [lyt.itemAt(i+1) for i in range(self.nb_objects)]

    def math_wdg_at(self, i):
        return self.lyt_math_objects[i].math_wdg

    def math_object_at(self, i):
        return self.math_wdg_at(i).math_object

    @property
    def math_objects(self):
        return [self.math_object_at(i) for i in range(self.nb_objects)]

    @property
    def math_wdg_at_beginning(self):
        return self.math_wdg_at(0)

    @property
    def math_wdg_at_end(self):
        return self.math_wdg_at(self.nb_objects-1)

    def put_at_end(self, i):
        """
        Put at the end (before stretch) the object currently at position i.
        Mind that index of math_object is 1 less than index in layout,
        because of QSpacerItem at position 0.
        """
        item = self.layout().takeAt(i+1)
        end_pos = self.layout().count()-1
        self.layout().insertItem(end_pos, item)

    def put_at_beginning(self, j):
        """
        Put at the beginning (after stretch) the object currently at position i.
        """
        item = self.layout().takeAt(j+1)
        self.layout().insertItem(1, item)


class OperatorLMO(RawLabelMathObject):
    """
    Display a MathObject which is a property operating on other objects.
    """

    def __init__(self, math_object):
        super().__init__(math_object)


class RwItemLMO(RawLabelMathObject):
    """
    Display a MathObject which is a property used for rewriting.
    """

    def __init__(self, math_object):
        super().__init__(math_object)


class LayoutOperator(QWidget):
    """
    Display a OperatorLMO inside a v-layout so that the box is not too big.
    """

    def __init__(self, math_object):
        super().__init__()
        self.math_wdg = OperatorLMO(math_object)
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.math_wdg)
        layout.addStretch(1)
        self.setLayout(layout)


class TargetSubstitutionArrow(QWidget):
    """
    Display an arrow labelled by some Generic LMO, e.g. a rewriting rule as in
            |
            |    f(x) = y
            |
            V
    """
    def __init__(self, rw_item):
        if isinstance(rw_item, tuple):  # FIXME: this is just for now...
            rw_item = rw_item[0] + " " + rw_item[1]

        super().__init__()
        layout = QHBoxLayout()
        layout.addStretch(1)

        # Arrow
        arrow_layout = QVBoxLayout()
        self.arrow_wdg = VerticalArrow()
        arrow_layout.addStretch(1)
        arrow_layout.addWidget(self.arrow_wdg)
        arrow_layout.addStretch(1)
        layout.addLayout(arrow_layout)

        # Label
        label_layout = QVBoxLayout()
        self.rw_label = RwItemLMO(rw_item)
        label_layout.addStretch(1)
        label_layout.addWidget(self.rw_label)
        label_layout.addStretch(1)
        layout.addLayout(label_layout)

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
        self.rw_label.show()
        fake_label.hide()


###########################
# Context / target blocks #
###########################
class ContextWidget(QWidget):
    """
    A widget for displaying new context objects on one line.
    If called with math_objects, will just display those math_objects on 1 line.
    Descendant class OperatorContextWidget displays a logical inference.
    Descendant class SubstitutionContextWidget displays some context rewriting.
    """

    def __init__(self, math_objects):
        super().__init__()
        self.operator = None
        self.layout = QHBoxLayout()
        self.layout.addStretch(1)
        self.input_layout: Optional[LayoutMathObjects] = None
        self.output_layout: Optional[LayoutMathObjects] = None

        self.math_objects = math_objects if math_objects else []
        for math_object in math_objects:
            self.add_child(math_object)

        self.setLayout(self.layout)

    def add_child(self, math_object: QWidget):
        """
        Insert a child math_object at the end, just before the stretch item.
        """
        # self.math_objects.append(math_object)
        item = GenericLMO(math_object)
        self.layout.insertWidget(self.layout.count()-1, item)

    def math_wdg_at(self, i):
        if i < len(self.math_objects) and i < self.layout.count()-1:
            return self.layout.itemAt(i+1).widget()

    @property
    def premises(self):
        if not self.input_layout:
            return []
        return self.input_layout.math_objects

    @property
    def operator_wdg(self):
        """
        To be redefined in derived classes.
        """
        return None

    @property
    def conclusions(self):
        if not self.output_layout:
            return []
        return self.output_layout.math_objects

    def match_premises_math_object(self, other):
        """
        Check if some math_objects of self.premises is a descendant of one
        other.math_objects. If so, return a couple (i,j)
        where self.premises[i] is a descendant of other.math_objects[j].
        """
        match = None
        for mo1 in self.premises:
            for mo2 in other.math_objects:
                if mo1 == mo2 or mo1.is_descendant_of(mo2):
                    match = (mo1, mo2)
        if match:
            return self.premises.index(mo1), other.math_objects.index(mo2)

    def match_premises_conclusions(self, other):
        """
        Check if some math_objects of self.premises is a descendant of one
        math_object of other.conclusions. If so, return a couple (i,j)
        where self.premises[i] is a descendant of other.conclusions[j].
        """

        match = None
        for mo1 in self.premises:
            for mo2 in other.conclusions:
                if mo1 == mo2 or mo1.is_descendant_of(mo2):
                    match = (mo1, mo2)
        if match:
            return self.premises.index(mo1), other.conclusions.index(mo2)

    def match_operator_math_objects(self, other):
        """
        Check if the math_object represented by self.operator_wdg is a
        descendant of one math_object of other.conclusions. If so, return the
        index of the matching conclusion.
        """
        if not self.operator_wdg:
            return
        match = None
        operator = self.operator_wdg.math_object
        if not isinstance(operator, ContextMathObject):
            return
        for mo in other.math_objects:
            if operator == mo or operator.is_descendant_of(mo):
                match = mo
        if match:
            return other.math_objects.index(match)

    def match_operator_conclusions(self, other):
        """
        Check if the math_object represented by self.operator_wdg is a 
        descendant of one math_object of other.conclusions. If so, return the
        index of the matching conclusion.
        """
        if not self.operator_wdg:
            return
        match = None
        operator = self.operator_wdg.math_object
        if not isinstance(operator, ContextMathObject):
            return
        for mo in other.conclusions:
            if operator == mo or operator.is_descendant_of(mo):
                match = mo
        if match:
            return other.conclusions.index(match)

    def find_link(self, other):
        """
        Search if some object in self.conclusions match either a premise or
        the operator of other. If so, make sure that the matched conclusion
        is at the end of the conclusions (by swapping if necessary),
        and similarly make sure that the matched premise is at the beginning
        of the pile of premises.
        Return the couple of widgets corresponding to linked objects (or None).
        """
        assert isinstance(other, ContextWidget)

        # (1) Try other.math_objects
        if other.math_objects:
            # (1.1) With premises
            match = self.match_premises_math_object(other)
            if match:
                i, j = match
                # print("Link found math_objects:")
                # print(match)
                self.input_layout.put_at_beginning(i)
                return (other.math_wdg_at(j),
                        self.input_layout.math_wdg_at_beginning)
            else:
                # (1.2) With operator
                match = self.match_operator_math_objects(other)
                if match is not None:
                    return (other.math_wdg_at(match),
                            self.operator_wdg)

        else:  # (2) Try other.conclusions, with premises and operator
            match = self.match_premises_conclusions(other)
            if match:
                i, j = match
                # print("Link found premises:")
                # print(match)
                self.input_layout.put_at_beginning(i)
                other.output_layout.put_at_end(j)
                return (other.output_layout.math_wdg_at_end,
                        self.input_layout.math_wdg_at_beginning)
            else:
                match = self.match_operator_conclusions(other)
                if match is not None:
                    other.output_layout.put_at_end(match)
                    return (other.output_layout.math_wdg_at_end,
                            self.operator_wdg)


class OperatorContextWidget(ContextWidget):
    """
    A widget for displaying new context object from a pure context step,
    e.g. modus ponens, shown as output of an "operator" object receiving some
    "input objects", as in
    y --> [f surjective] --> x, f(x)=y.
    """

    def __init__(self, premises, operator, conclusions):
        super().__init__([])
        # self.premises: [MathObject] = premises
        self.operator: Union[MathObject, Statement] = operator
        # self.conclusions: [MathObject] = conclusions
        self.type_ = "operator"
        self.input_layout = None
        self.operator_layout = None

        assert operator and conclusions
        self.output_layout = LayoutMathObjects(conclusions, align="left")

        # Input -> Operator -> output:
        if premises:
            self.input_layout = LayoutMathObjects(premises, align="right",
                                                  new=False)
            self.layout.addLayout(self.input_layout)
            self.layout.addWidget(HorizontalArrow())

        if operator:
            self.operator_layout = LayoutOperator(operator)
            self.layout.addWidget(self.operator_layout)
            self.layout.addWidget(HorizontalArrow())

        self.layout.addLayout(self.output_layout)

        self.layout.addStretch(1)

    @property
    def operator_wdg(self):
        return self.operator_layout.math_wdg


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

        # FIXME: arrow length should never be less than operator length.
        super().__init__([])
        # self.premises = premises
        self.operator = rw_item
        # self.conclusions = conclusions
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

    @property
    def operator_wdg(self):
        return self.arrow_wdg.rw_label


class TargetWidget(QWidget):
    """
    A widget for displaying a new target, with a target_msg (generally "Proof of
    ...") and a layout for displaying the proof of the new target.
    A disclosure triangle allows showing / hiding the proof.
    The layout is a grid layout, with the following ingredients:
    triangle     |  "Proof of target"
    -----------------------------
    vertical bar | content_layout
                 |----------------
                 | status_label

    This grid may be extended when adding a child with target substitution (
    see below).
    The content_layout contains is designed to welcome the content of the
    logical_children of the WidgetGoalBlock to which the TargetWidget belongs.
    The status_label display the status of the target (goal solved?).
    Attribute target_msg is a callable that takes a parameter color=True/False.
    This is used for disabling colors when widget is disabled.
    """

    def __init__(self, parent_wgb, target: MathObject, target_msg: callable,
                 hidden=False,
                 status_label: Optional[BlinkingLabel] = None,
                 title_label: Optional[ProofTitleLabel] = None):
        super().__init__()
        self.target = target
        self.target_msg = target_msg
        self.parent_wgb = parent_wgb
        self.content_layouts = []
        self.curved_arrows = []

        # Title and status:
        self.title_label = title_label
        self.title_label.setTextFormat(Qt.RichText)
        self.title_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.status_lbls = [status_label] if status_label else []
        self.substituted_title_lbls = []
        self.substitution_arrows = []

        # Disclosure triangle and vertical line
        self.triangle = DisclosureTriangle(self.toggle)
        self.triangle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.vert_bar = VertBar()

        # Layouts
        self.content_layouts.append(QVBoxLayout())
        self.main_layout = QGridLayout()  # 2x3, five items
        self.main_layout.addWidget(self.triangle, 0, 0)
        self.main_layout.addWidget(self.vert_bar, 1, 0, -1, 1)
        self.main_layout.addWidget(self.title_label, 0, 1)
        self.main_layout.addWidget(QLabel(""), 0, 3)  # Just to add stretch
        self.main_layout.addLayout(self.content_layout, 1, 1)
        self.main_layout.addWidget(self.current_status_label, 2, 1)

        # layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.main_layout.setColumnStretch(3, 1)
        self.main_layout.setAlignment(self.triangle, Qt.AlignHCenter)
        self.main_layout.setAlignment(self.vert_bar, Qt.AlignHCenter)

        self.setLayout(self.main_layout)

        if hidden:
            self.toggle()

    @property
    def content_layout(self) -> QVBoxLayout:
        """
        The children should be added in the content_layout of the last
        substituted target.
        """
        return self.content_layouts[-1]

    @property
    def current_status_label(self) -> BlinkingLabel:
        return self.status_lbls[-1]

    @property
    def children_layout(self):
        return self.content_layout

    def set_as_current_target(self, yes=True, blinking=True):
        if yes:
            log.debug(f"Setting goal nb {self.parent_wgb.goal_nb} as current "
                      f"target")
            log.debug(f"Current status msg is "
                      f"{self.current_status_label.text()}")
            self.title_label.set_bold(True)
            if blinking:
                # self.set_status()
                self.current_status_label.start_blinking()
                self.parent_wgb.make_visible(self.current_status_label)  # Fixme
            else:
                self.current_status_label.stop_blinking()
                # This is not pertinent:
                # self.parent_wgb.make_visible(self.title_label)
        else:
            self.current_status_label.stop_blinking()
            # self.set_status()
            self.title_label.set_bold(False)

    @property
    def all_widgets(self):
        widgets = (self.substituted_title_lbls + self.substitution_arrows +
                   [self.current_status_label, self.vert_bar])
        for layout in self.content_layouts:
            more = [layout.itemAt(i).widget() for i in range(layout.count())]
            widgets.extend(more)
        return widgets

    def toggle(self):
        """
        Toggle on / off the display of the all content. The proof title is
        untouched, except for the "colon" at the end which should be there
        only when content is displayed.
        """

        # FIXME: colon, status_msg
        # self.hidden = not self.hidden
        self.title_label.disclosed = not self.title_label.disclosed
        self.title_label.update()
        self.current_status_label.disclosed = self.title_label.disclosed
        self.current_status_label.update_text()
        for wdg in self.all_widgets:
            wdg.show() if self.title_label.disclosed else wdg.hide()

    # def set_status(self):
    #     """
    #     Display the status msg, if any.
    #     """
    #     # FIXME: should be useless
    #     # log.debug(f"Setting status msg {self.status_msg} for goal nb "
    #     #           f"{self.parent_wgb.goal_nb}")
    #
    #     # if self.target_is_substituted:
    #     #     self.status_label.hide()
    #     # elif not self.status_msg:
    #     #     self.status_label.hide()
    #     # else:
    #     #     self.status_label.show()
    #     #     self.status_label.setText(self.status_msg)
    #     #     self.status_label.text = self.status_msg
    #     self.current_status_label.set_msg()

    def link_last_child(self):
        """
        Try to link input / operator of last child to output of previous child.
        """
        # TODO: try to link self.context2. Add color.
        match = None
        nb = self.content_layout.count()
        if nb < 2:
            return
        # Last two children:
        child1 = self.content_layout.itemAt(nb-1).widget()  # WidgetGoalBlock
        child2 = self.content_layout.itemAt(nb-2).widget()
        child1_widget = child1.pure_context_widget
        child2_widget = child2.pure_context_widget
        if child1_widget:
            match = child1_widget.find_link(
                child2_widget)
        if not match:
            return
        source_wdg, target_wdg = match
        arrow = CurvedArrow(source_wdg, target_wdg, self)
        self.curved_arrows.append(arrow)

    def add_child_wgb(self, child: QWidget):
        """
        Add a WidgetGoalBlock in self.content_layout. Handle the case of a
        substituted target: the title_lbl and status_lbl are "stolen" from
        the WGB, which is not displayed. In this case, a new content_layout
        is added, and we get thje following structure:

        vertical bar | content_layout_1 |
                     |----------------  | substitution_arrow
                     | child_title      |
                     |----------------  |
                     | content_layout_2 |
                     |----------------  |
                     | status_label

        """
        if not hasattr(child, "substitution_arrow"):
            child.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.content_layout.addWidget(child)
            self.content_layout.setAlignment(child, Qt.AlignLeft)
            self.link_last_child()
        else:
            # log.debug("Adding target substitution child")
            # Status label should not be displayed anymore:
            self.main_layout.removeWidget(self.current_status_label)
            self.current_status_label.hide()
            self.current_status_label.deactivate()

            nb_targets = len(self.content_layouts)
            child_title_lbl_pos = nb_targets*2
            child_title_lbl = child.proof_title_label
            child_status_lbl = child.status_label
            # Record new title and status labels:
            self.substituted_title_lbls.append(child_title_lbl)
            self.status_lbls.append(child_status_lbl)

            # Display new title, content, and status ; modify vertical bar:
            self.main_layout.addWidget(child_title_lbl,
                                       child_title_lbl_pos, 1)
            self.content_layouts.append(QVBoxLayout())
            self.main_layout.addLayout(self.content_layout,
                                       child_title_lbl_pos+1, 1)
            self.main_layout.addWidget(child_status_lbl, child_title_lbl_pos+2,
                                       1)
            # TODO: cut the vert line into pieces to show new targets?
            self.main_layout.addWidget(self.vert_bar, 1, 0,
                                       child_title_lbl_pos+2, 1)

            # Display and record substitution arrow:
            self.main_layout.addWidget(child.substitution_arrow,
                                       child_title_lbl_pos-2, 2, 3, 1)
            self.substitution_arrows.append(child.substitution_arrow)

    def paintEvent(self, event):
        """
        Paint the curved arrows linking successive output / inputs.
        """
        # FIXME: this way of doing is not compatible with disabling arrow.
        #  --> put the arrow in a widget, that can be disabled.
        painter = QPainter(self)
        for arrow in self.curved_arrows:
            # if arrow.origin_wdg.isEnabled() and arrow.end_wdg.isEnabled():
            points = points_for_curved_arrow(arrow.origin_wdg,
                                             arrow.end_wdg,
                                             arrow.parent_wdg)
            paint_curved_arrow(points, painter, color=arrow.color)

