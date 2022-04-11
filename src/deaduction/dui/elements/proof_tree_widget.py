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

from typing import Union
from PySide2.QtWidgets import (QApplication, QFrame, QLayout,
                               QHBoxLayout, QVBoxLayout, QGridLayout,
                               QLineEdit, QListWidget, QWidget, QGroupBox,
                               QLabel, QTextEdit, QSizePolicy)
from PySide2.QtWidgets import QScrollArea
from PySide2.QtCore import Qt, Signal, Slot, QSettings
from PySide2.QtGui import QFont, QColor, QPalette, QIcon, QPainter, QPixmap
import sys

import deaduction.pylib.config.vars as cvars
import deaduction.pylib.config.dirs as cdirs

global _
_ = lambda x: x


def operator_arrow():
    # arrow_label.setScaledContents(True)
    # arrow_label.setMaximumSize(self.height(), self.height())
    arrow_label = QLabel()
    arrow_icon_path = cdirs.icons / "right_arrow.png"
    pixmap = QPixmap(str(arrow_icon_path.resolve()))
    arrow_label.setPixmap(pixmap)

    return arrow_label


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


class LabelMathObject(QLabel):
    """
    Display a MathObject which is not a property.
    """

    def __init__(self, math_object, new=True):
        super().__init__()
        txt = math_object  # FIXME .to_display(format_="html")
        self.setTextFormat(Qt.RichText)
        self.setText(txt)
        # TODO: distinguish objects / props
        if new:
            self.setStyleSheet("padding: 5px;"
                               "border-width: 2px;"
                               "border-color: blue;"
                               "border-style: solid;"
                               "border-radius: 10px;")

        else:
            self.setStyleSheet("padding: 5px;"
                               "border-width: 1px;"
                               "border-color: blue;"
                               "border-style: dotted;"
                               "border-radius: 10px;")


class LayoutMathObject(QHBoxLayout):
    """
    Display a LabelMathObject inside a h-layout so that the box is not too big.
    """

    def __init__(self, math_object, align=None, new=True):
        super().__init__()
        if align in (None, "right"):
            self.addStretch(1)
        self.addWidget(LabelMathObject(math_object, new=new))
        if align in (None, "left"):
            self.addStretch(1)


class LayoutMathobjects(QVBoxLayout):
    """
    Display a vertical pile of LayoutMathobjects.
    """

    def __init__(self, math_objects, align=None, new=True):
        super().__init__()
        self.addStretch(1)
        for math_object in math_objects:
            self.addLayout(LayoutMathObject(math_object, align=align, new=new))
        self.addStretch(1)


class LabelOperator(QLabel):
    """
    Display a MathObject which is a property operating on other objects.
    """

    def __init__(self, math_object):
        super().__init__()
        txt = math_object  # FIXME .to_display(format_="html")
        self.setTextFormat(Qt.RichText)
        self.setText(txt)
        self.setStyleSheet("padding: 5px;"
                           "border-width: 4px;"
                           "border-color: red;"
                           "border-style: solid;"
                           "border-radius: 10px;")
        self.setWordWrap(True)


class LayoutOperator(QWidget):
    """
    Display a LabelOperator inside a v-layout so that the box is not too big.
    """

    def __init__(self, math_object):
        super().__init__()
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(LabelOperator(math_object))
        layout.addStretch(1)
        self.setLayout(layout)


###########################
# Context / target blocks #
###########################
class ContextBlock(QWidget):
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
        self.math_objects.append(math_object)
        item = LabelMathObject(math_object)
        self.layout.insertWidget(self.layout.count()-1, item)


class PureContextBlock(ContextBlock):
    """
    A widget for displaying new context object from a pure context step,
    e.g. modus ponens, shown as output of an "operator" object receiving some
    "input objects", as in
    y --> [f surjective] --> x, f(x)=y.
    """

    def __init__(self, premises, operator, conclusions):
        super().__init__([])

        input_layout = LayoutMathobjects(premises, align="right", new=False)
        output_layout = LayoutMathobjects(conclusions, align="left")
        operator_wdg = LayoutOperator(operator)

        # Input -> Operator -> output:
        self.layout.addLayout(input_layout)
        self.layout.addWidget(operator_arrow())
        self.layout.addWidget(operator_wdg)
        self.layout.addWidget(operator_arrow())
        self.layout.addLayout(output_layout)

        self.layout.addStretch(1)


class TargetBlock(QWidget):
    """
    A widget for displaying a new target, with a target_msg (generally "Proof of
    ...") and a layout for displaying the proof of the new target.
    A disclosure triangle allows showing / hiding the proof.
    The layout is a 2x2 grid layout, with the following ingredients:
    triangle     |  "Proof of target"
    -----------------------------
    vertical bar | content widget (empty when created)
    """

    def __init__(self, target_msg="", hidden=False, cqfd=False):
        super().__init__()
        self.hidden = False
        self.logical_children: [WidgetGoalBlock] = []  # FIXME: refer to goal parent
        self.target_msg = target_msg
        self._cqfd = cqfd

        # Layout
        self.triangle = DisclosureTriangle(self.disclose, hidden=hidden)
        self.triangle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.vert_bar = VertBar()
        # self.vert_bar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.title_label = QLabel(text=self.target_msg)
        self.title_label.setTextFormat(Qt.RichText)
        self.title_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.content = QWidget()
        self.content_layout = QVBoxLayout()
        self.end_msg_label = QLabel(self.end_msg)
        self.end_msg_label.setStyleSheet("font-style: italic;")
        self.content_layout.addWidget(self.end_msg_label)
        self.content.setLayout(self.content_layout)
        self.content.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        layout = QGridLayout()  # 2x2
        layout.addWidget(self.triangle, 0, 0)
        layout.addWidget(self.vert_bar, 1, 0)
        layout.addWidget(self.title_label, 0, 1)
        layout.addWidget(self.content, 1, 1)
        layout.addWidget(QLabel(""), 0, 2)  # Just to add stretch
        layout.setColumnStretch(2, 1)
        layout.setAlignment(self.triangle, Qt.AlignHCenter)
        layout.setAlignment(self.vert_bar, Qt.AlignHCenter)

        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        self.setLayout(layout)

        if hidden:
            self.disclose()

    def changeEvent(self, event):
        """
        Dynamically change the end msg to display QED if proof is complete.
        """
        self.set_end_msg()

    @property
    def sub_targets(self):
        return filter(lambda it: isinstance(it, TargetBlock), self.logical_children)

    @property
    def cqfd(self):
        """
        True iff this goal is complete, and so are all its sub-goals.
        """
        # FIXME: refer to goal parent attribute
        children_cqfd = [child.cqfd for child in self.sub_targets]
        # print(len(self.logical_children), children_cqfd)
        return self._cqfd and all(children_cqfd)

    @property
    def end_msg(self) -> str:
        if self.cqfd:
            return _("Goal!")
        elif self._cqfd:  # Self will be proved when all children are
            return "(" + _("Goal") + ")"
        else:
            return "( ...under construction... )"

    def set_end_msg(self):
        self.end_msg_label.setText(self.end_msg)

    def disclose(self):
        """
        Toggle on / off the display of the content.
        """
        self.hidden = not self.hidden
        if self.hidden:
            self.layout().takeAt(3)  # Content_layout is the fourth layoutItem
            self.content.hide()
            self.title_label.setText(self.target_msg)
        else:
            self.layout().addWidget(self.content, 1, 1)
            self.title_label.setText(self.target_msg)
            self.content.show()

    def add_child(self, child: QWidget):
        """
        Add child, a widget of type WidgetGoalBlock, just before the end_msg label.
        """
        # FIXME: just insert widget ("display_child"?)
        self.logical_children.append(child)
        self.content_layout.insertWidget(self.content_layout.count()-1,
                                         child)


########################
# Abstract Goal blocks #
########################
class AbstractGoalBlock:
    """
    A generic class for dealing with the logical part of WidgetGoalBlock.
    An AbstractGoalBlock may have one target and two context lists,
    corresponding to new context element to be displayed before / after the
    target.
    """
    goal_nb = 0

    def __init__(self, logical_parent=None,
                 context1=None, target=None, context2=None):

        self._context1 = context1 if context1 else []
        self._context2 = context2 if context2 else []
        self._target = target

        self.logical_parent = logical_parent  # Usually set by parent
        self.logical_children = []
        self.goal_nb = AbstractGoalBlock.goal_nb
        AbstractGoalBlock.goal_nb += 1

    @property
    def context1(self):
        return self._context1

    @property
    def target(self):
        return self._target

    @property
    def context2(self):
        return self._context2

    def add_child(self, child):
        self.logical_children.append(child)
        child.logical_children = self


class AbstractIntroGB(AbstractGoalBlock):
    """
    This class handles the logical part of an intro block.
    """

    # FIXME: handle fusion up/down
    def __init__(self, context, target, logical_parent=None,
                 fusion_up=True, fusion_down=True):
        super().__init__(logical_parent=logical_parent,
                         context1=context, target=target)
        self.fusion_up = fusion_up
        self.fusion_down = fusion_down

    @property
    def context1(self):
        """
        Fusion self 's _context with child's context. Note that this will call
        recursively to all descendant's _context, as far as they are IntroWGB.
        """
        if self.logical_children and isinstance(self.logical_children[0],
                                                AbstractIntroGB):
            return self._context1 + self.logical_children[0].context1
        else:
            return self._context1


    @property
    def target(self):
        if self.logical_children and isinstance(self.logical_children[0],
                                                AbstractIntroGB):
            return self.logical_children[0].target
        else:
            return self._target

    @property
    def first_non_intro_descendants(self):
        """
        Return a descendant that should be displayed in self.target_widget
        (except if self.parent is also an IntroWGB).
        """
        if not self.logical_children:
            return None
        elif not isinstance(self.logical_children[0], IntroWGB):
            return self.logical_children
        else:
            return self.logical_children[0].first_non_intro_descendants


######################
# Widget Goal blocks #
######################
class WidgetGoalBlock(QWidget, AbstractGoalBlock):
    """
    A generic widget for displaying an AbstractGoalNode. It has
     - one widget for showing some context objects in a horizontal layout,
     - another one for showing a target,
     - and a third one for showing a second context list after the target.
    """
    def __init__(self, logical_parent=None,
                 context1=None, target=None, context2=None):
        super().__init__(logical_parent=logical_parent, context1=context1,
                         target=target, context2=context2)
        self.context1_widget: QWidget = None  # Created by set_layout().
        self.target_widget: QWidget = None
        self.context2_widget: QWidget = None
        self._children_layout = None

        self.main_layout = QVBoxLayout()
        self.main_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.set_layout()

    @property
    def children_layout(self) -> QHBoxLayout:
        """
        Return the layout that should welcome the children's widgets.
        After set_layout() is called, self has either a target_widget or a
        _children_layout.
        """
        return (self._children_layout if self._children_layout
                else self.target_widget if self.target_widget
                else None)

    def set_layout(self):
        """
        Populate main_layout from scratch.
        """
        # Clear target and context
        if self.target_widget:
            self.target_widget.deleteLater()
        if self.context1_widget:
            self.context1_widget.deleteLater()
        if self.context2_widget:
            self.context2_widget.deleteLater()

        # Create and insert new widget:
        if self.context1:
            self.context1_widget = ContextBlock(self.context1)
            # context_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.main_layout.insertWidget(0, self.context1_widget)

        if self.target:
            self.target_widget = TargetBlock(self.target)   # FIXME .to_display(
            # format_="html"))
            # target_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.main_layout.insertWidget(0, self.target_widget)
            # So that no space left when target_widget is disclosed:

        if self.context2:
            self.context2_widget = ContextBlock(self.context2)
            # context_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.main_layout.insertWidget(0, self.context2_widget)

        if not self.target_widget:
            if not self._children_layout:
                self._children_layout = QVBoxLayout()
            nb_item = self.main_layout.count()
            self.main_layout.insertLayout(nb_item-1, self._children_layout)

    def insert_child(self, child):
        """
        Insert child as a widget.
        """
        assert isinstance(child, WidgetGoalBlock)
        nb_item = self.children_layout.count()
        self.children_layout.insertWidget(nb_item - 1, child)

    def add_child(self, child):
        """
        Logically add child.
        """
        super().add_child(child)
        self.insert_child(child)


class ByCasesBlock(WidgetGoalBlock):
    """
    Display of one sub-case of a proof by cases.
    """


class ImpliesIntroBlock(WidgetGoalBlock):
    pass


class IntroWGB(WidgetGoalBlock, AbstractIntroGB):
    """
    Display of introduction of elements to prove universal props or
    implications. This block has a special behaviour in that it may "fusion"
    with its child, if its child is also an IntroWGB. In other words,
    the widget will display the new context items introduced by all
    the descendants, and only the last target. This is achieved by
    re-implementing self.context and self.target as properties.
    """

    def set_layout(self):
        """
        Call parent's set_layout if parent is an IntroWGB.
        If there is a first_non_intro_descendant and parent is an IntroWGB,
        it will be handled by parent. Else add it to the target_widget.
        """
        super().set_layout()
        if isinstance(self.parent, IntroWGB):
            self.parent.set_layout()
        elif self.first_non_intro_descendants:
            for child in self.first_non_intro_descendants:
                self.target_widget.add_child(child)


###############
# Main Window #
###############
class ProofTreeWindow(QWidget):
    """
    A widget for displaying the proof tree.
    """

    def __init__(self, context=None, target=None):
        """
        Context and target are the elements of the initial goal.
        """
        super().__init__()
        self.setWindowTitle("Proof Tree")
        settings = QSettings("deaduction")
        if settings.value("proof_tree/geometry"):
            self.restoreGeometry(settings.value("proof_tree/geometry"))

        main_layout = QVBoxLayout()
        self.main_window = QScrollArea()
        main_layout.addWidget(self.main_window)

        if context or target:
            main_block = WidgetGoalBlock(context, target)
            self.set_main_block(main_block)

        self.setLayout(main_layout)

    def set_main_block(self, block: WidgetGoalBlock):
        self.main_window.setWidget(block)

    def closeEvent(self, event):
        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("proof_tree/geometry", self.saveGeometry())
        event.accept()
        self.hide()


def main():
    app = QApplication()
    main_window = ProofTreeWindow()

    context0=["X", "Y", "f"]
    target0="f surjective ⇒ (∀A ⊂ Y, ∀A' ⊂ Y, ( f⁻¹(A) ⊂ f⁻¹(A') ⇒ A ⊂ A' ) )"
    main_block = WidgetGoalBlock(context0, target0)

    main_window.set_main_block(main_block)

    # TODO: change to successive IntroBlocks:
    intro1 = WidgetGoalBlock(["f surjective"], "(∀A ⊂ Y, ∀A' ⊂ Y, ( f⁻¹(A) ⊂ f⁻¹("
                                          "A') ⇒ A ⊂ A' ) )")
    intro2 = IntroWGB(["A", "A'"], "f⁻¹(A) ⊂ f⁻¹(A') ⇒ A ⊂ A'")
    intro3 = WidgetGoalBlock(["f⁻¹(A) ⊂ f⁻¹(A')"], "A ⊂ A'")
    context1 = ["f surjective", "A",
               "A'", "f⁻¹(A) ⊂ f⁻¹(A')"]
    main_block.add_child(intro1)
    intro1.add_child(intro2)
    intro2.add_child(intro3)
    # context_wdg = ContextBlock(context1)
    # context_wdg.show()

    target = "Proof of A ⊂ A'"
    # target_wdg = TargetBlock(target)
    # target_wdg.show()

    # TODO: change to successive IntroBlocks:
    # context2 = ["y", "y ∈ A"]
    # context_block1 = ContextBlock(context2)
    # main_block.add_child(context_block1)
    intro_block1 = IntroWGB(context=["y"], target="y ∈ A => y ∈ A'")
    intro3.add_child(intro_block1)

    intro_block2 = IntroWGB(context=["y ∈ A"], target="y ∈ A'")
    intro_block1.add_child(intro_block2)

    # intro_block1.show()
    # main_block.add_child(intro_block1)

    # target2 = "Proof of y ∈ A'"
    # target_block1 = TargetBlock(target2)
    # main_block.add_child(target_block1)

    operator = [PureContextBlock(["y"], "f surjective", ["x", "y = f(x)"]),
                PureContextBlock(["y ∈ A"], "y = f(x)", ["f(x) ∈ A"]),
                PureContextBlock(["f(x) ∈ A"],
                                 "definition image réciproque",
                                 ["x ∈ f⁻¹(A)"]
                                 ),
                PureContextBlock(["x ∈ f⁻¹(A)"], "f⁻¹(A) ⊂ f⁻¹(A')",
                                 ["x ∈ f⁻¹(A')"]),
                PureContextBlock(["x ∈ f⁻¹(A')"],
                                 "definition image réciproque",
                                 ["f(x) ∈ A'"]),
                PureContextBlock(["f(x) ∈ A'"], "y = f(x)", ["y ∈ A'"])]
    for op in operator:
        intro_block2.add_child(op)

    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

