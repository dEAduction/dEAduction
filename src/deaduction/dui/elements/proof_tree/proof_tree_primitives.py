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
from PySide2.QtGui import QColor, QPainter, QPolygon, QPen, QBrush

import deaduction.pylib.config.vars as cvars

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


def paint_layout(painter, item, item_depth=0, max_depth=10):
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

    def start_blinking(self):
        self.flag = True
        self.timer.start()
        # log.debug(f"Starting blinking gn {self.goal_nb}, text = {self.text}")

    def stop_blinking(self):
        # log.debug(f"Stop blinking gn {self.goal_nb}")
        self.timer.stop()

    def blink(self):
        self.setText(" "*len(self.text()) if self.flag else self.text())
        self.flag = not self.flag
        # log.debug(f"Blinking gn {self.goal_nb}, text = {self.text}")

    def deactivate(self, yes=True):
        self._is_deactivated = yes

    def set_msg(self):
        if not self.text():
            self.hide()
        elif not self._is_deactivated:
            self.setText(self.text())
            self.show()


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


def rectangle(item):
    if isinstance(item, QWidget):
        return item.rect()
    elif isinstance(item, QLayout):
        return item.contentsRect()


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

        # pen = QPen()
        # pen.setColor(QColor(self.color()))
        # pen.setWidth(self.pen_width)
        # pen.setJoinStyle(Qt.MiterJoin)
        # pen.setCapStyle(Qt.FlatCap)
        # painter.setPen(pen)
        # arrow_height = self.arrow_height
        # vect_x = QPoint(arrow_height, 0)
        # vect_y = QPoint(0, arrow_height)
        # end = end - vect_x
        #
        # pen.setStyle(self.style)
        # painter.setPen(pen)
        # painter.drawLine(origin, end-2*vect_x)
        # # Triangle
        # brush = QBrush(self.color(), Qt.SolidPattern)
        # painter.setBrush(brush)
        # pen.setStyle(Qt.SolidLine)
        # pen.setWidth(1)
        # painter.setPen(pen)
        # upper_vertex = end-2*vect_x - vect_y
        # lower_vertex = end-2*vect_x + vect_y
        # triangle = QPolygon([end, upper_vertex, lower_vertex, end])
        # painter.drawPolygon(triangle)
        # painter.end()

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
            txt = self.html_msg(use_color=self.isEnabled())
            if isinstance(self, ProofTitleLabel):
                txt += _(":")
            return pre + txt + post

        if isinstance(self.math_object, str):
            return self.math_object
        else:
            math_object = (self.math_object.math_type if self.is_prop
                           else self.math_object)
            txt = math_object.to_display(format_="html",
                                         use_color=self.isEnabled())
        return txt

    def changeEvent(self, event) -> None:
        """
        In case object is enabled/disabled, change to properly display colored
        variables.
        """
        self.setText(self.txt())
        event.accept()


class ProofTitleLabel(RawLabelMathObject):
    """
    A QLabel to display a mgs like "Proof of ...:".
    The colon is added on top of html_msg.
    """
    def __init__(self, html_msg):
        # def html_msg_with_colon(**kwargs):
        #     return html_msg(kwargs) + _(":")
        # super().__init__(html_msg=html_msg_with_colon)
        super().__init__(html_msg=html_msg)


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
                 |----------------
                 | status_label

    The content_layout contains is designed to welcome the content of the
    logical_children of the WidgetGoalBlock to which the TargetWidget belongs,
     It ends with the status_label.
    The status_label display the status of the target (goal solved?).
    Attribute html_msg is a callable that takes a parameter color=True/False.

    There is a special case when target has been re-written. Then an attribute
    target_substitution_arrow is provided (a QWidget).
    """

    def __init__(self, parent_wgb, target: MathObject, target_msg: callable,
                 hidden=False, status_label=None, title_label=None):
        super().__init__()
        self.hidden = False
        self.target = target
        self.target_msg = target_msg
        self.parent_wgb = parent_wgb
        # self.is_target_substitution = is_target_substitution
        self.content_layouts = []

        # Title and status:
        self.title_label = title_label
        self.title_label.setTextFormat(Qt.RichText)
        self.title_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.status_lbls = [status_label] if status_label else []
        self.substituted_title_lbls = []
        self.substitution_arrows = []
        # self.status_label = BlinkingLabel(self.status_msg,
        #                                   goal_nb=self.parent_wgb.goal_nb)
        # self.status_label.setStyleSheet("font-style: italic;")
        # self.status_label.setSizePolicy(QSizePolicy.Fixed,
        #                                 QSizePolicy.Fixed)
        # self.status_lbls.append(self.status_label)

        # Disclosure triangle and vertical line
        self.triangle = DisclosureTriangle(self.toggle, hidden=False)
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
    def current_status_label(self):
        return self.status_lbls[-1]

    @property
    def children_layout(self):
        return self.content_layout

    # @property
    # def target_is_substituted(self):
    #     """
    #     True if target has been substituted. This has several implications,
    #     e.g. status_label should never be shown since it is replaced by
    #     child's status_label.
    #     """
    #     # FIXME: does not work if self is itself a substitution
    #     return len(self.content_layouts) > 1

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

    def all_widgets(self):
        widgets = (self.substituted_title_lbls + self.substitution_arrows +
                   [self.current_status_label, self.vert_bar])
        for layout in self.content_layouts:
            more = [layout.itemAt(i).widget() for i in range(layout.count())]
            widgets.extend(more)
        return widgets

    def toggle(self):
        """
        Toggle on / off the display of the content.
        """

        # FIXME
        self.hidden = not self.hidden
        for wdg in self.all_widgets():
            wdg.hide() if self.hidden else wdg.show()

            # if self.hidden:
            # self.current_status_label.hide()
            # self.vert_bar.hide()
            # for wdg in self.substituted_title_lbls:
            #     wdg.hide()
            # for arrow in self.substitution_arrows:
            #     arrow.hide()
            # for layout in self.content_layouts:
            #     wdgs = [layout.itemAt(i) for i in range(layout.count())]
            #     for wdg in wdgs:
            #         wdg.widget().hide()
        # else:
            # self.status_label.show()
            # self.vert_bar.show()
            # for layout in self.content_layouts:
            #     wdgs = [layout.itemAt(i) for i in range(layout.count())]
            #     for wdg in wdgs:
            #         wdg.widget().show()

            # self.set_status()

    # @property
    # def status_msg(self) -> Optional[str]:
    #     """
    #     Compute the status msg for this part of the proof, to be displayed at
    #     the end of the block.
    #     """
    #
    #     if self.parent_wgb.is_recursively_solved():
    #         if self.parent_wgb.is_no_more_goals():
    #             msg = _("THE END")
    #         elif self.parent_wgb.is_recursively_sorry():
    #             msg = _("(admitted)")
    #         else:
    #             msg = _("Goal!") + str(self.parent_wgb.goal_nb)  # debug
    #     elif self.parent_wgb.is_conditionally_solved():
    #         msg = None
    #     else:
    #         msg = _("( ... under construction... )")
    #     # log.debug(f"Status msg for goal nb {self.parent_wgb.goal_nb} is {msg}")
    #     return msg

    def set_status(self):
        """
        Display the status msg, if any.
        """
        # FIXME: should be useless
        # log.debug(f"Setting status msg {self.status_msg} for goal nb "
        #           f"{self.parent_wgb.goal_nb}")

        # if self.target_is_substituted:
        #     self.status_label.hide()
        # elif not self.status_msg:
        #     self.status_label.hide()
        # else:
        #     self.status_label.show()
        #     self.status_label.setText(self.status_msg)
        #     self.status_label.text = self.status_msg
        self.current_status_label.set_msg()

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
        else:
            # log.debug("Adding target substitution child")
            # self.parent_wgb.set_target_substituted(True)
            nb_targets = len(self.content_layouts)
            child_title_lbl_pos = nb_targets*2
            self.main_layout.removeWidget(self.current_status_label)
            self.current_status_label.hide()
            self.current_status_label.deactivate()

            # child_title_lbl = RawLabelMathObject(html_msg=child.target_msg)
            child_title_lbl = child.proof_title_label
            child_status_lbl = child.status_label
            self.substituted_title_lbls.append(child_title_lbl)
            self.status_lbls.append(child_status_lbl)
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

            self.main_layout.addWidget(child.substitution_arrow,
                                       child_title_lbl_pos-2, 2, 3, 1)
            self.substitution_arrows.append(child.substitution_arrow)



