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
from PySide2.QtCore import Qt, QRect, QPoint, QTimer, Signal
from PySide2.QtGui import QColor, QPainter, QPolygon, QPen, QBrush, QPainterPath

from deaduction.dui.primitives import MathLabel
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
    """
    A QLabel that displays a msg that can be made to blink in boldface.
    This is used to show the status of targets (solved / to be completed).
    """

    blinking_nb = 5  # Cursor blinks 5 times

    def __init__(self, text: callable, goal_nb=-1):
        super(BlinkingLabel, self).__init__(text())
        self.goal_nb = goal_nb
        self.text = text
        self.flag = None
        self.timer = QTimer(self, interval=1000)
        self.timer.timeout.connect(self.blink)
        # self.start_blinking()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._is_activated = None
        self.disclosed = True
        self._blinking_counter = None

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
        self._blinking_counter = self.blinking_nb
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
            self._blinking_counter -= 1
            if self._blinking_counter == 0:
                self.stop_blinking()

        self.flag = not self.flag

    def activate(self, yes=True):
        """
        A blinking label will be shown ONLY IF activated. The only way to be
        activated is to be displayed in a TargetWidget.
        """
        self._is_activated = yes

    def update_text(self):
        self.setText(self.text())

    def set_msg(self):
        if not self.text() or not self._is_activated or not self.disclosed:
            self.hide()
        elif self._is_activated:
            self.update_text()
            self.show()

    def set_bold(self, yes=True):
        self.bold = yes
        if yes:
            self.setStyleSheet("font-weight: bold;")
        else:
            self.setStyleSheet("")

    def enable_or_disable(self):
        """
        Disable self if text does not coincide with text in truncated mode.
        This indicates that the status is not valid at the time of history.
        """
        if self.text(truncate=True) != self.text():
            self.setEnabled(False)
        else:
            self.setEnabled(True)

# def display_object(math_objects):
#     """
#     Recursively convert MathObjects inside math_objects to str in html format.
#     """
#     if math_objects is None:
#         return None
#     elif isinstance(math_objects, str):
#         return math_objects
#     elif isinstance(math_objects, list):
#         return list([display_object(mo) for mo in math_objects])
#     elif isinstance(math_objects, tuple):
#         return tuple(display_object(mo) for mo in math_objects)
#     else:
#         if math_objects.math_type.is_prop():
#             return math_objects.math_type.to_display(format_="html")
#         else:
#             return math_objects.to_display(format_="html")


#######################################################################
# ----------------- Some geometry helper functions ------------------ #
#######################################################################
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


def max_width(wdg1, wdg2):
    """
    Return the max of the widths of both widgets.
    """
    o_width = wdg1.rect().width()
    e_width = wdg2.rect().width()
    # log.debug(f"Widths: {o_width}, {e_width}")
    return max(o_width, e_width)


#######################################################################
# ----------------- Some painting helper functions ------------------ #
#######################################################################
def paint_arrowhead(end_line, painter: QPainter,
                    direction="horizontal_right", arrow_height=5,
                    color=cvars.get("display.color_for_operator_props")):
    """
    Paint the head of an arrow.
    """

    # Coordinates
    vect_x = QPoint(arrow_height, 0)
    vect_y = QPoint(0, arrow_height)
    if direction == "horizontal_right":
        # end = end - vect_x
        # upper_vertex = end - 2 * vect_x - vect_y
        # lower_vertex = end - 2 * vect_x + vect_y
        upper_vertex = end_line - vect_y
        lower_vertex = end_line + vect_y
        end = end_line + vect_x
    elif direction == "horizontal_left":
        # end = end + vect_x
        upper_vertex = end_line - vect_y
        lower_vertex = end_line + vect_y
        end = end_line - vect_x
    elif direction == "vertical":
        # end = end - vect_y
        upper_vertex = end_line + vect_x
        lower_vertex = end_line - vect_x
        end = end_line + vect_y

    # Pen
    pen = QPen()
    pen.setColor(QColor(color))
    pen.setJoinStyle(Qt.MiterJoin)
    pen.setCapStyle(Qt.FlatCap)
    painter.setPen(pen)

    # Draw arrow
    brush = QBrush(color, Qt.SolidPattern)
    painter.setBrush(brush)
    pen.setStyle(Qt.SolidLine)
    pen.setWidth(1)
    painter.setPen(pen)
    triangle = QPolygon([end, upper_vertex, lower_vertex, end])
    painter.drawPolygon(triangle)


def paint_arrow(origin, end, painter: QPainter,
                arrow_height=5, style=Qt.SolidLine,
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
        # upper_vertex = end - 2 * vect_x - vect_y
        # lower_vertex = end - 2 * vect_x + vect_y
        end_line = end - 2*vect_x
    elif direction == "vertical":
        end = end - vect_y
        # upper_vertex = end - 2 * vect_y + vect_x
        # lower_vertex = end - 2 * vect_y - vect_x
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
    if direction == "horizontal":
        direction = "horizontal_right"
    paint_arrowhead(end_line, painter, direction, arrow_height, color)
    # brush = QBrush(color, Qt.SolidPattern)
    # painter.setBrush(brush)
    # pen.setStyle(Qt.SolidLine)
    # pen.setWidth(1)
    # painter.setPen(pen)
    # triangle = QPolygon([end, upper_vertex, lower_vertex, end])
    # painter.drawPolygon(triangle)
    painter.end()


def points_for_substitution_arrow(origin_wdg: QWidget, end_wdg: QWidget,
                                  middle_wdg: QWidget,
                                  parent_wdg: QWidget,
                                  inner_sep=10,
                                  shift_start=False) -> [QPoint]:
    """
    Compute points for tracing a curved substitution arrow. The arrow goes from
    the middle right of origin_wdg to the middle right of end_wdg, through
    the middle left of middle_wdg,  within parent_wdg. This is used for
    substitution in target.
    """
    shift = QPoint(inner_sep, 0)
    rel_origin = mid_right(origin_wdg.rect())
    origin = origin_wdg.mapTo(parent_wdg, rel_origin) + shift
    if shift_start:
        origin += shift
    rel_end = mid_right(end_wdg.rect())
    end = end_wdg.mapTo(parent_wdg, rel_end) + shift
    rel_mid = mid_left(middle_wdg.rect())
    mid = middle_wdg.mapTo(parent_wdg, rel_mid) - shift
    control1 = QPoint(mid.x(), origin.y())
    control2 = QPoint(mid.x(), end.y())

    return [origin, control1, mid, control2, end]


def points_for_curved_line(origin_wdg: QWidget, end_wdg: QWidget,
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


def paint_curved_line(points: [QPoint],
                      painter: QPainter,
                      style=Qt.DotLine,
                      color=None, pen_width=1):
    """
    Use painter to draw a (quadratic Bezier) curved line. This is used to
    link identical MathObjects.
    """
    assert len(points) == 5
    if color is None:
        color = "Black"
    path = QPainterPath()
    path.moveTo(points[0])
    path.quadTo(points[1], points[2])
    path.quadTo(points[3], points[4])
    pen = QPen(QColor(color))
    painter.setBrush(Qt.NoBrush)
    pen.setStyle(style)
    pen.setWidth(pen_width)
    painter.setPen(pen)
    painter.drawPath(path)


def paint_substitution_arrow(points: [QPoint],
                             painter: QPainter,
                             style=Qt.DashLine,
                             color=None, pen_width=1):
    paint_curved_line(points, painter, style, color, pen_width)
    end = points[-1]
    paint_arrowhead(end, painter, direction="horizontal_left", color=color)


def rectangle(item: Union[QWidget, QLayout]):
    if isinstance(item, QWidget):
        return item.rect()
    elif isinstance(item, QLayout):
        return item.contentsRect()


class CurvedLine:
    """
    A class to store info to draw a curved line. This is used to link
    identical MathObjects.
    """
    def __init__(self, origin_wdg: QWidget, end_wdg: QWidget, parent):
        color_var = cvars.get("display.color_for_variables")
        color_prop = cvars.get("display.color_for_props")
        self.origin_wdg = origin_wdg
        self.end_wdg = end_wdg
        self.parent_wdg = parent
        self.color = color_prop if self.origin_wdg.is_prop else color_var


class CurvedSubstitutionArrow:
    """
    A class for recording data for a target substitution arrow.
    """
    inner_sep = 20

    def __init__(self, origin_wdg: QWidget, end_wdg: QWidget,
                 middle_wdg: QWidget, parent):
        self.origin_wdg = origin_wdg
        self.middle_wdg = middle_wdg
        self.end_wdg = end_wdg
        self.parent_wdg = parent

    @property
    def color(self):
        if self.origin_wdg.isEnabled() and self.end_wdg.isEnabled():
            return cvars.get("display.color_for_operator_props")
        else:
            return "lightgrey"


# class VerticalArrow(QWidget):
#     """
#     A class to paint a vertical arrow
#     """
#     def __init__(self, minimum_height=60, arrow_width=4, style=Qt.DashLine):
#         super(VerticalArrow, self).__init__()
#         self.setMinimumHeight(minimum_height)
#         self.setFixedWidth(arrow_width*3)
#         self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
#         self.pen_width = 1
#         self.arrow_width = arrow_width + self.pen_width
#         self.style = style
#
#     def color(self):
#         if self.isEnabled():
#             return cvars.get("display.color_for_operator_props")
#         else:
#             return "lightgrey"
#
#     def paintEvent(self, e):
#         painter = QPainter(self)
#
#         rectangle = self.rect()
#         origin = mid_top(rectangle)
#         end = mid_bottom(rectangle)
#
#         paint_arrow(origin=origin, end=end, painter=painter,
#                     arrow_height=self.arrow_width, style=self.style,
#                     color=self.color(), direction="vertical")


class HorizontalArrow(QWidget):
    """
    Display a horizontal arrow. The width is computed via a callable, so that
    it can be determined on the flight, after the label widget is shown.
    """
    def __init__(self, width=50, arrow_height=4, style=Qt.SolidLine,
                 callable_width=None):
        super(HorizontalArrow, self).__init__()
        self.style = style
        self.width = width
        self.callable_width = callable_width
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
        if self.callable_width:
            self.set_width(self.callable_width())
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

    def toggle(self):
        """
        Modify self's appearance and call the slot function.
        """
        self.setText("▷" if self.text() == "▽" else "▽")
        self.slot()

    def mousePressEvent(self, ev) -> None:
        self.toggle()


class VertBar(QFrame):
    """
    A vertical bar, used to indicate the proof of a specific target.
    """
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(2)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)


class RawLabelMathObject(MathLabel):
    """
    Mother class for displaying a MathObject or a msg which is computed by
    the callable html_msg, which takes parameter use_color and bf.
    This allows to disable self by setting use_color=False, or to highlight
    it by setting bf=True.
    This QLabel may be highlighted, it can change its text dynamically thanks
    to its attribute html_msg which is a callable (and to the update_txt()
    method), and it can tell the main window when mouse is over by calling
    back the highlight_in_tree function.

    Param math_object may be a MathObject instance or a string or a Statement.
    """
    # highlight_in_tree = Signal(ContextMathObject) Fixme: Does not work ?!
    highlight_in_tree: callable = None

    def __init__(self, math_object: Union[MathObject, Statement, str] = None,
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
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

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
            txt = self.math_object.type_ + " " + self.math_object.pretty_name
            return txt
        elif isinstance(self.math_object, MathObject):
            math_object = (self.math_object.math_type if self.is_prop
                           else self.math_object)
            txt = math_object.to_display(format_="html",
                                         use_color=self.isEnabled())
            return txt

    def update_text(self):
        self.setText(self.txt())

    def changeEvent(self, event) -> None:
        """
        In case object is enabled/disabled, change to properly display colored
        variables.
        """
        self.setText(self.txt())
        event.accept()

    def highlight(self, yes=True):
        color = cvars.get(
            "display.color_for_highlight_in_proof_tree", "green")
        self.setStyleSheet(f'background-color: {color};' if yes
                           else 'background-color:;')

    def enterEvent(self, event):
        """
        If self display a ContextMathObject, call self.highlight_in_tree.
        to highlight all related RawLabelMO in the proof tree widget.
        """
        super().enterEvent(event)
        if isinstance(self.math_object, ContextMathObject):
            self.highlight()
            # self.highlight_in_tree.emit(self.math_object)
            if self.highlight_in_tree:
                self.highlight_in_tree(self.math_object, True)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if isinstance(self.math_object, ContextMathObject):
            self.highlight(False)
            if self.highlight_in_tree:
                self.highlight_in_tree(self.math_object, False)


class ProofTitleLabel(RawLabelMathObject):
    """
    A QLabel to display a mgs like "Proof of ...".
    The colon is added on top of html_msg by super class RawLabelMathObject
    iff self.disclosed is True.
    """
    def __init__(self, html_msg, toggle: Optional[callable]=None):
        super().__init__(html_msg=html_msg)
        self.disclosed = True
        self.toggle = toggle

    def set_toggle(self, toggle: callable):
        self.toggle = toggle

    def mouseDoubleClickEvent(self, event):
        if self.toggle:
            self.toggle()


class GenericLMO(RawLabelMathObject):
    """
    A class for displaying MathObject inside a frame. math_object can be a
    MathObject instance or a string (e.g. a statement name). A tooltip
    provides the type of the MathObject if pertinent.
    """
    def __init__(self, math_object: Union[MathObject, str], new=True):
        super().__init__(math_object)
        # The following is used in the style sheet
        is_new = "new" if new else "old"
        is_prop = "prop" if self.is_prop else "obj"
        self.setObjectName(is_new + "_" + is_prop)
        if isinstance(math_object, MathObject) and not self.is_prop:
            tooltip = math_object.math_type_to_display(format_="utf8")
            self.setToolTip(tooltip)


class LayoutMathObject(QHBoxLayout):
    """
    Display a single GenericLMO inside a h-layout so that the box is not too
    big.
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
    Display a vertical pile of LayoutMathObjects. Order may be changed
    dynamically, e.g. when links with next or previous widgets must be drawn.
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
        if 0 <= i <= self.nb_objects-1:
            return self.lyt_math_objects[i].math_wdg

    @property
    def math_wdgs(self):
        return [self.math_wdg_at(i) for i in range(self.nb_objects)]

    def math_object_at(self, i):
        if 0 <= i <= self.nb_objects-1:
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
        end_pos = self.layout().count()-2
        if i+1 != end_pos:
            item = self.layout().takeAt(i+1)
            self.layout().insertItem(end_pos, item)

    def put_at_beginning(self, j):
        """
        Put at the beginning (after stretch) the object currently at position i.
        """
        if j+1 != 1:
            item = self.layout().takeAt(j+1)
            self.layout().insertItem(1, item)


class OperatorLMO(RawLabelMathObject):
    """
    Display a MathObject which is a property operating on other objects. This
    should be displayed with a special style (e.g. red fat frame).
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


class TargetSubstitutionLabel(RwItemLMO):
    """
    Just store a rw_item, to be displayed along with a curved target
    substitution arrow.
    """

    def __init__(self, rw_item):
        if isinstance(rw_item, tuple):  # FIXME: this is just for now...
            rw_item = rw_item[0] + " " + rw_item[1]

        super().__init__(rw_item)


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
        self.arrow_wdg = HorizontalArrow(style=Qt.DashLine,
                                         callable_width=self.dynamic_width)
                                         # width=self.label_width + 100)
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

    def dynamic_width(self):
        return self.rw_label.geometry().width() + 50


###########################
# Context / target blocks #
###########################
class ContextWidget(QWidget):
    """
    A widget for displaying new context objects on one line.
    If called with math_objects, will just display those math_objects on 1 line.
    Descendant class OperatorContextWidget displays a logical inference.
    Descendant class SubstitutionContextWidget displays some context rewriting.

    Premises are stored in self.pure_premises. Displayed premises,
    as provided by the property, may be permuted along the way ; so
    self.pure_premises and self.pure_premises should coincide only up to
    a permutation.
    """

    def __init__(self, math_objects,
                 premises=None, operator=None, conclusions=None):
        super().__init__()
        self.pure_premises = premises
        self.operator = operator
        self.pure_conclusions = conclusions
        self.type_ = None
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
            return self.layout.itemAt(i).widget()

    @property
    def math_wdgs(self) -> [RawLabelMathObject]:
        """
        Return all math widgets displayed by self.
        """
        wdgs = []
        if self.math_objects:
            wdgs = [self.math_wdg_at(i) for i in range(len(self.math_objects))]
        if self.input_layout:
            wdgs.extend(self.input_layout.math_wdgs)
        if self.operator:
            wdgs.append(self.operator_wdg)
        if self.output_layout:
            wdgs.extend(self.output_layout.math_wdgs)

        return wdgs

    @property
    def pure_context_widget(self):
        """
        Artificial way of disguising self into a PureContextWGB.
        """
        return self

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
                    i1 = self.premises.index(mo1)
                    i2 = other.math_objects.index(mo2)
                    return i1, i2

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
                    i1 = self.premises.index(mo1)
                    i2 = other.conclusions.index(mo2)
                    return i1, i2

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
                return other.math_objects.index(mo)
        # if match:
        #     return other.math_objects.index(match)

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
                return other.conclusions.index(mo)

        # if match:
        #     return other.conclusions.index(match)

    def find_link(self, other):
        """
        Search if some object in self.conclusions match either a premise or
        the operator of other. If so, make sure that the matched conclusion
        is at the end of the conclusions (by swapping if necessary),
        and similarly make sure that the matched premise is at the beginning
        of the pile of premises.
        Return the couple of widgets corresponding to linked objects (or None).
        """
        if not isinstance(other, ContextWidget):
            return

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
                self.input_layout.put_at_beginning(i)  # FIXME!!!
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
        super().__init__([], premises, operator, conclusions)
        # self.premises: [MathObject] = premises
        # self.operator: Union[MathObject, Statement] = operator
        # self.conclusions: [MathObject] = conclusions
        self.type_ = "operator"
        self.input_layout = None
        self.operator_layout = None

        assert conclusions
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
        if self.operator_layout:
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

        super().__init__([], premises, rw_item, conclusions)
        # self.premises = premises
        # self.operator = rw_item
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


class TargetAndRwLayout(QGridLayout):
    """
    A class to display a part of the proof tree between two "Proof of..."
    inside a TargetWidget.
    """
    min_space = 100

    def __init__(self):
        super().__init__()
        self.rw_wdg: Optional[QWidget] = None
        self.first_column_width: Optional[callable()] = None
        self._content_count = 0
        self.width_updated = False

    def all_content_widgets(self):
        return [self.itemAtPosition(i, 0).widget()
                for i in range(self.content_count)]

    def all_widgets(self):
        wdgs = self.all_content_widgets()
        if self.rw_wdg:
            wdgs.append(self.rw_wdg)
        return  wdgs

    @property
    def content_count(self):
        return self._content_count

    def add_to_content(self, wdg):
        """
        Add wdg to content (column 0), in last position.
        """
        self.addWidget(wdg, self.content_count, 0)
        self.setAlignment(wdg, Qt.AlignLeft)
        self._content_count += 1

    def set_rw_wdg(self, width: callable, rw_wdg):
        """
        Set rw_wdg in the third column.
        """
        self.rw_wdg = rw_wdg
        self.first_column_width = width
        row_nb = self.rowCount()
        self.addWidget(rw_wdg, 0, 2, row_nb, 1)
        self.setAlignment(rw_wdg, Qt.AlignVCenter)

    def update_width(self):
        """
        Update width for nice display. This should be called once all sizes
        have been set up (with a QTimer).
        """
        self.setColumnMinimumWidth(0, self.first_column_width())
        self.setColumnMinimumWidth(1, self.min_space)
        self.width_updated = True


class TargetWidget(QWidget):
    """
    A widget for displaying a new target, with a target_msg (generally "Proof of
    ...") and a layout for displaying the proof of the new target.
    A disclosure triangle allows showing / hiding the proof.
    The layout is a grid layout, with the following ingredients:
    triangle     |  "Proof of target" (title_label)
    -----------------------------
    vertical bar | content_layout
                 |----------------
                 | "under construction" (status_label)

    This grid may be extended when adding a child with target substitution (
    see below).
    The content_layout contains is designed to welcome the content of the
    logical_children of the WidgetGoalBlock to which the TargetWidget belongs.
    The status_label display the status of the target (goal solved?).
    Attribute target_msg is a callable that takes a parameter color=True/False.
    This is used for disabling colors when widget is disabled.
    """

    def __init__(self, parent_wgb, target: MathObject,
                 hidden=False,
                 status_label: Optional[BlinkingLabel] = None,
                 title_label: Optional[ProofTitleLabel] = None):
        super().__init__()

        self.disclosed = True
        self.target = target
        # self.target_msg = target_msg
        self.parent_wgb = parent_wgb
        self.content_n_rw_lyts: [TargetAndRwLayout] = []
        self.curved_arrows: [CurvedLine] = []

        # Title and status:
        self.title_label: ProofTitleLabel = title_label
        self.status_lbls: [BlinkingLabel] = []
        self.add_status_lbl(status_label)
        self.substituted_title_lbls = []
        self.target_substitution_arrows: [CurvedSubstitutionArrow] = []

        # Disclosure triangle and vertical line
        self.triangle = DisclosureTriangle(self.toggle)
        self.title_label.set_toggle(self.triangle.toggle)
        self.triangle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.vert_bar = VertBar()

        # Layouts
        self.content_n_rw_lyts.append(TargetAndRwLayout())
        self.main_layout = QGridLayout()  # 2x3, five items
        self.main_layout.addWidget(self.triangle, 0, 0)
        self.main_layout.addWidget(self.vert_bar, 1, 0, -1, 1)
        self.main_layout.addWidget(self.title_label, 0, 1)
        self.main_layout.addLayout(self.content_n_rw_lyt, 1, 1)
        self.main_layout.addWidget(self.current_status_label, 2, 1)

        self.main_layout.setColumnStretch(3, 1)
        self.main_layout.setAlignment(self.triangle, Qt.AlignHCenter)
        self.main_layout.setAlignment(self.vert_bar, Qt.AlignHCenter)

        self.setLayout(self.main_layout)

        if hidden:
            self.toggle()

        # Hide first column (triangle and vert_bar) for the root_node
        if self.parent_wgb.is_root_node_or_substituted:
            self.hide_triangle_and_bar()

    @property
    def content_n_rw_lyt(self):
        return self.content_n_rw_lyts[-1]

    @property
    def content_layout(self) -> QVBoxLayout:
        """
        The children should be added in the content_layout of the last
        substituted target.
        """
        return self.content_n_rw_lyt.content_lyt

    @property
    def current_status_label(self) -> BlinkingLabel:
        return self.status_lbls[-1]

    def add_status_lbl(self, child_status_lbl):
        if self.status_lbls:
            self.current_status_label.activate(False)
        child_status_lbl.activate()
        self.status_lbls.append(child_status_lbl)

    @property
    def children_layout(self):
        return self.content_n_rw_lyt

    def hide_triangle_and_bar(self):
        self.vert_bar.hide()
        self.triangle.hide()

    def set_as_current_target(self, yes=True, blinking=True) \
            -> Optional[QWidget]:
        """
        Set self as current target, i.e. highlight target in boldface and make
        status_msg blinks. If blinking then return current_status_label,
        else return proof_title. The returned widget should be made visible in
        the ScrollArea.
        """
        if yes:
            log.debug(f"Setting goal nb {self.parent_wgb.goal_nb} as current "
                      f"target")
            log.debug(f"Current status msg is "
                      f"{self.current_status_label.text()}")
            self.title_label.set_bold(True)
            if blinking:
                self.current_status_label.start_blinking()
                return self.current_status_label
            else:
                self.current_status_label.stop_blinking()
                return self.title_label
        else:
            self.current_status_label.stop_blinking()
            self.title_label.set_bold(False)

    @property
    def all_widgets(self) -> list:
        """
        Return the list of all sub-widgets to be disclosed when the
        disclosure triangle is activated.
        """
        widgets = (self.substituted_title_lbls
                   + [self.current_status_label, self.vert_bar])
        for lyt in self.content_n_rw_lyts:
            widgets.extend(lyt.all_widgets())
        return widgets

    def disclose_or_not(self):
        self.title_label.disclosed = self.disclosed
        self.title_label.update_text()
        self.current_status_label.disclosed = self.disclosed
        self.current_status_label.update_text()
        for wdg in self.all_widgets:
            wdg.show() if self.disclosed else wdg.hide()

    def toggle(self):
        """
        Toggle on / off the display of the all content. The proof title is
        untouched, except for the "colon" at the end which should be there
        only when content is displayed.
        """
        self.disclosed = not self.disclosed
        self.disclose_or_not()

    def link_last_child(self):
        """
        Try to link input / operator of last child to output of previous child.
        Previous child's class is either WidgetGoalBlock, or ContextWidget
        (as context2 of a WidgetGoalBlock inserted as first child of
        self.content_layout).
        """

        # TODO: try to link self.context2.
        match = None
        # log.debug(f"Already {nb} children")
        nb = self.content_n_rw_lyt.content_count
        if nb < 2:
            return
        # Last two children:
        child1 = self.content_n_rw_lyt.itemAtPosition(nb-1, 0).widget()  #
        # WidgetGoalBlock
        child2 = self.content_n_rw_lyt.itemAtPosition(nb-2, 0).widget()
        child1_widget = child1.pure_context_widget
        # NB: child2 may be a ContextWidget, in which case
        # child2.pure_context_widget artificially refers to child2.
        child2_widget = child2.pure_context_widget
        if child1_widget:
            match = child1_widget.find_link(child2_widget)
        if not match:
            return
        source_wdg, target_wdg = match
        arrow = CurvedLine(source_wdg, target_wdg, self)
        self.curved_arrows.append(arrow)

    def add_child_wgb(self, child: QWidget):
        """
        Add a WidgetGoalBlock in self.content_layout. Handle the case of a
        substituted target: the title_lbl and status_lbl are "stolen" from
        the child WGB, which is not displayed. In this case, a new
        content_n_rw_lyt is added, and we get the following structure:

        vertical bar | content_n_rw_lyts[0] |
                     |----------------      |
                     | child_proof_title    |
                     |----------------      |
                     | content_n_rw_lyts[1] |
                     |----------------      |
                     | status_label         |

        """
        if not hasattr(child, "substitution_label"):
            log.debug(f"Adding child {child.goal_nb}")
            child.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.content_n_rw_lyt.add_to_content(child)
            # self.content_n_rw_lyt.setAlignment(child, Qt.AlignLeft)
            self.link_last_child()
        else:
            # log.debug(f"Adding target subs child {child.goal_nb}")

            # Status label should not be displayed anymore:
            self.main_layout.removeWidget(self.current_status_label)
            self.current_status_label.hide()
            self.current_status_label.activate(yes=False)

            nb_targets = len(self.content_n_rw_lyts)
            child_title_lbl_pos = nb_targets*2
            child_title_lbl = child.proof_title_label
            child_status_lbl = child.status_label

            # Record new title and status labels:
            self.substituted_title_lbls.append(child_title_lbl)
            self.add_status_lbl(child_status_lbl)

            # Display new title and substitution arrow
            self.main_layout.addWidget(child_title_lbl,
                                       child_title_lbl_pos, 1)
            stl = self.substituted_title_lbls
            origin_wdg = stl[-2] if len(stl) > 1 else self.title_label
            origin_math_wdg = origin_wdg
            end_math_wdg = stl[-1]

            def width():
                return max_width(origin_math_wdg, end_math_wdg)
            self.content_n_rw_lyt.set_rw_wdg(width, child.substitution_label)
            middle_wdg = child.substitution_label
            substitution_arrow = CurvedSubstitutionArrow(origin_math_wdg,
                                                         end_math_wdg,
                                                         middle_wdg,
                                                         self)
            self.target_substitution_arrows.append(substitution_arrow)

            # Display content and status ; modify vertical bar:
            self.content_n_rw_lyts.append(TargetAndRwLayout())
            self.main_layout.addLayout(self.content_n_rw_lyt,
                                       child_title_lbl_pos+1, 1)
            self.main_layout.addWidget(child_status_lbl, child_title_lbl_pos+2,
                                       1)
            # TODO: cut the vert line into pieces to show new targets?
            self.main_layout.addWidget(self.vert_bar, 1, 0,
                                       child_title_lbl_pos+2, 1)

    def paintEvent(self, event):
        """
        Paint the curved arrows linking successive output / inputs,
        and the target substitution arrows.
        """

        # FIXME: this is called each time status_msg blinks, not optimal.
        painter = QPainter(self)
        for arrow in self.curved_arrows:
            if arrow.origin_wdg.isEnabled() and arrow.end_wdg.isEnabled():
                points = points_for_curved_line(arrow.origin_wdg, arrow.end_wdg,
                                                arrow.parent_wdg)
                paint_curved_line(points, painter, color=arrow.color)

        init = True
        for (content_rw_lyt, arrow) in zip(self.content_n_rw_lyts,
                                           self.target_substitution_arrows):
            if arrow.origin_wdg.isVisible() and arrow.end_wdg.isVisible():
                # print("Painting")
                points = points_for_substitution_arrow(arrow.origin_wdg,
                                                       arrow.end_wdg,
                                                       arrow.middle_wdg,
                                                       arrow.parent_wdg,
                                                       inner_sep=arrow.inner_sep,
                                                       shift_start=not init)
                if not content_rw_lyt.width_updated:
                    QTimer.singleShot(0, content_rw_lyt.update_width)
                init = False
                paint_substitution_arrow(points, painter, color=arrow.color)
            # else:
                # print("Not painting")
        painter.end()

