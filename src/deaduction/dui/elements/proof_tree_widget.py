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

from deaduction.pylib.proof_tree import ProofTree, GoalNode


global _
_ = lambda x: x


def display_object(math_objects):
    """
    Recursively convert MathObjects inside math_objects to str in html format.
    """
    if math_objects is None:
        return None
    elif isinstance(math_objects, str):
        return math_objects
    elif isinstance(math_objects, list):
        return [display_object(mo) for mo in math_objects]
    elif isinstance(math_objects, tuple):
        return (display_object(mo) for mo in math_objects)
    else:
        if math_objects.math_type.is_prop():
            return math_objects.math_type.to_display(format_="html")
        else:
            return math_objects.to_display(format_="html")


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
        item = LabelMathObject(math_object)
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


class TargetWidget(QWidget):
    """
    A widget for displaying a new target, with a target_msg (generally "Proof of
    ...") and a layout for displaying the proof of the new target.
    A disclosure triangle allows showing / hiding the proof.
    The layout is a 4x2 grid layout, with the following ingredients:
    triangle     |  "Proof of target"
    -----------------------------
    vertical bar | content_layout
    -----------------------------
                 | children_layout
    -----------------------------
                 | status_label

    The content_layout contains at most one widget, displaying context
    introduced at the same step as the new target.
    The children_layout is designed to welcome the content of the
    logical_children of the WidgetGoalBlock to which the TargetWidget belongs.
    The status_label display the status of the target (goal solved?).
    """

    def __init__(self, target_msg="", disclosed=False, cqfd=False):
        super().__init__()
        self.disclosed = False
        self.target_msg = target_msg
        self._cqfd = cqfd

        # Title and frame:
        self.triangle = DisclosureTriangle(self.disclose, hidden=False)
        self.triangle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.vert_bar = VertBar()
        self.title_label = QLabel(text=self.target_msg)
        self.title_label.setTextFormat(Qt.RichText)
        self.title_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Content, children, status:
        # self.content = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget = None
        # self.content_layout.addWidget(self.status_label)
        # self.content.setLayout(self.content_layout)
        # self.content.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.children_layout = QVBoxLayout()
        self.children_wgt = []
        self.status_label = QLabel(self.status)
        self.status_label.setStyleSheet("font-style: italic;")

        layout = QGridLayout()  # 2x2
        layout.addWidget(self.triangle, 0, 0)
        layout.addWidget(self.vert_bar, 1, 0)
        layout.addWidget(self.title_label, 0, 1)
        # layout.addWidget(self.content, 1, 1)
        layout.addWidget(QLabel(""), 0, 2)  # Just to add stretch
        layout.setColumnStretch(2, 1)
        layout.setAlignment(self.triangle, Qt.AlignHCenter)
        layout.setAlignment(self.vert_bar, Qt.AlignHCenter)

        layout.addLayout(self.content_layout, 1, 1)
        layout.addLayout(self.children_layout, 2, 1)
        layout.addWidget(self.status_label, 3, 1)
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        self.main_layout = layout
        self.setLayout(layout)

        if disclosed:
            self.disclose()

    def changeEvent(self, event):
        """
        Dynamically change the end msg to display QED if proof is complete.
        """
        self.set_status()

    def disclose(self):
        """
        Toggle on / off the display of the content.
        """
        self.disclosed = not self.disclosed
        if self.disclosed:  # Content_layout is the fourth layoutItem
            self.main_layout.takeAt(3)
            self.content.hide()
            self.title_label.setText(self.target_msg)
        else:
            self.main_layout.addWidget(self.content, 1, 1)
            self.title_label.setText(self.target_msg)
            self.content.show()

    @property
    def cqfd(self):
        """
        True iff this goal is complete, and so are all its sub-goals.
        """
        # FIXME: refer to goal parent attribute
        # children_cqfd = [child.cqfd for child in self.sub_targets]
        # # print(len(self.logical_children), children_cqfd)
        # return self._cqfd and all(children_cqfd)
        return True  # FIXME

    @property
    def status(self) -> str:
        if self.cqfd:
            return _("Goal!")
        elif self._cqfd:  # Self will be proved when all children are
            return "(" + _("Goal") + ")"
        else:
            return "( ...under construction... )"

    def set_status(self):
        self.status_label.setText(self.status)

    def set_content(self, content_widget):
        """
        Put content_widget in self.content_layout. NB: this layout can
        contain at most one widget.
        """
        if self.content_widget:
            self.content_layout.replaceWidget(self.content_widget,
                                              content_widget)
        else:
            self.content_layout.addWidget(content_widget)
        self.content_widget = content_widget

    def clear_children_layout(self):
        """
        Remove all widget from children_layout.
        """
        for child_wgt in self.children_wgt:
            child_wgt.deleteLater()
        self.children_wgt = []

    def insert_child(self, child: QWidget):
        """
        Add child, a widget of type WidgetGoalBlock, at the end of the
        children_layout.
        """
        self.children_wgt.append(child)
        self.children_layout.addWidget(child)
        # self.children_layout.insertWidget(self.content_layout.count()-1, child)

    def set_children(self, children):
        """
        Reset all children from scratch.
        """
        self.clear_children_layout()
        for child in children:
            self.insert_child(child)


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
                 context1=None, target=None, context2=None,
                 merge_up=False, merge_down=False):

        self._context1 = display_object(context1) if context1 else []
        self._target = display_object(target)
        self.context2 = display_object(context2) if context2 else []

        self.logical_parent = logical_parent  # Usually set by parent
        self.logical_children = []
        self.goal_nb = AbstractGoalBlock.goal_nb
        AbstractGoalBlock.goal_nb += 1

        self.wanna_merge_up = merge_up
        self.wanna_merge_down = merge_down

        self.goal_node = None

    def set_goal_node(self, goal_node):
        self.goal_node = goal_node

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

    @property
    def first_non_merged_descendants(self):
        """
        Return a descendant that should be displayed in self.target_widget
        (except if self.merge_up).
        """
        # FIXME: unused?
        if not self.logical_children:
            return []
        elif not self.merge_down:
            return self.logical_children
        else:
            return self.logical_children[0].first_non_merged_descendants

    @property
    def merge_up(self):
        """
        True if self's content should be merged with parent's.
        """
        return (self.wanna_merge_up and self.logical_parent
                and self.logical_parent.wanna_merge_down)

    @property
    def merge_down(self):
        """
        True if self's content should be merged with (lonely) child's.
        """
        return (self.wanna_merge_down and len(self.logical_children) == 1
                and self.logical_children[0].wanna_merge_up)

    def add_logical_child(self, child):
        self.logical_children.append(child)
        child.logical_parent = self

    def set_children(self, children):
        self.logical_children = []
        for child in children:
            self.add_logical_child(child)


######################
# Widget Goal blocks #
######################
class WidgetGoalBlock(QWidget, AbstractGoalBlock):
    """
    A generic widget for displaying an AbstractGoalNode. It has
     - one widget for showing some context objects in a horizontal layout,
     - another one for showing a target,
     - and a third one for showing a second context list under the target.
    """
    def __init__(self, logical_parent=None,
                 context1=None, target=None, context2=None,
                 merge_down=False, merge_up=False):
        super().__init__()
        AbstractGoalBlock.__init__(self, logical_parent=logical_parent,
                                   context1=context1,
                                   target=target, context2=context2,
                                   merge_down=merge_down, merge_up=merge_up)

        self.context1_widget: QWidget = None  # Created by set_layout().
        self.target_widget: TargetWidget = None
        self.context2_widget: QWidget = None

        self.main_layout = QVBoxLayout()
        self.main_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.set_layout()

    def set_layout(self):
        """
        Populate main_layout from scratch.
        """
        # Clear target and context.
        if self.context2_widget:
            self.context2_widget.deleteLater()
        if self.target_widget:
            self.target_widget.deleteLater()
        if self.context1_widget:
            self.context1_widget.deleteLater()

        # Create and insert new widgets (at pole position, in reverse order):
        if self.target:
            self.target_widget = TargetWidget(self.target)
            # format_="html"))
            self.main_layout.insertWidget(0, self.target_widget)

        if self.context1:
            if isinstance(self.context1, list):
                self.context1_widget = ContextWidget(self.context1)
            elif isinstance(self.context1, tuple):
                premises, operator, conclusions = self.context1
                self.context1_widget = PureContextWidget(premises, operator,
                                                         conclusions)
            self.main_layout.insertWidget(0, self.context1_widget)

        if self.context2 and self.target:
            self.context2_widget = ContextWidget(self.context2)
            self.target_widget.set_content([self.context2_widget])

        # self._set_children()

    def set_children(self, children):
        """
        Set all children as widgets, either in target_widget, or in main_layout
        if self has no target.
        """
        # FIXME: unused?
        super().set_children(children)
        if self.target_widget:
            self.target_widget.set_children(self.first_non_merged_descendants)
            # for child in self.first_non_merged_descendants:
            #     self.target_widget.insert_child(child)
        else:
            for child in self.first_non_merged_descendants:
                nb_item = self.main_layout.count()
                self.main_layout.insertWidget(nb_item-1, child)
        if self.merge_up:
            self.logical_parent.set_layout()

    def display_child_here(self, child):
        """
        Insert a child widget either in target_widget or in main_layout.
        """
        if self.target_widget:
            self.target_widget.insert_child(child)
        else:
            nb_item = self.main_layout.count()
            self.main_layout.insertWidget(nb_item-1, child)

    def manage_new_child(self, child):
        if self.merge_up:  # Children are displayed by parent
            self.logical_parent.manage_new_child(child)
        else:
            self.display_child_here(child)

    def add_logical_child(self, child):
        """
        Add a logical child and update self or parent according to where the
        widget should be displayed.
        """
        super().add_logical_child(child)
        self.manage_new_child(child)


class ByCasesWGB(WidgetGoalBlock):
    """
    Display of one sub-case of a proof by cases.
    """
    def __init__(self, context, target, logical_parent=None):
        super().__init__(logical_parent, target=target, context2=context,
                         merge_down=False, merge_up=False)


class IntroWGB(WidgetGoalBlock):
    """
    Display of introduction of elements to prove universal props.
    Try to merge with parent and child.
    """
    def __init__(self, logical_parent=None, context=None, target=None):
        super().__init__(logical_parent, context, target,
                         merge_down=True, merge_up=True)


class IntroImpliesWGB(WidgetGoalBlock):
    """
    Display of introduction of elements to prove universal props or
    implications. Try to merge with parent but not child.
    """
    def __init__(self, logical_parent=None, context=None, target=None):
        super().__init__(logical_parent, context, target,
                         merge_down=False, merge_up=True)


class PureContextWGB(WidgetGoalBlock):

    def __init__(self, premises, operator, conclusions):
        super().__init__(context1=(premises, operator, conclusions))


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

        self.main_block = None

    def set_main_block(self, block: WidgetGoalBlock):
        self.main_block = block
        self.main_window.setWidget(block)

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

def widget_goal_block(goal_node: GoalNode) -> WidgetGoalBlock:
    """
    All WidgetGoalBlock to be inserted in the ProofTreeWidget should be
    created by calling this method.
    """
    # FIXME: goal solved case!!
    new_context = goal_node.goal.new_context
    target = goal_node.goal.target.math_type
    if goal_node.is_intro:
        wgb = IntroWGB(context=new_context, target=target)
    elif goal_node.is_implies:
        wgb = IntroImpliesWGB(context=new_context, target=target)
    elif goal_node.is_by_cases:
        wgb = ByCasesWGB(context=new_context, target=target)
    elif goal_node.is_pure_context:
        premises, operator, conclusions = goal_node.is_pure_context
        wgb = PureContextWGB(premises, operator, conclusions)
    else:
        wgb = WidgetGoalBlock(target=target, context2=new_context)

    wgb.set_goal_node(goal_node)
    return wgb


# def update_from_nodes(wgb: WidgetGoalBlock, gn: GoalNode):
#     """
#     Recursively update the WidgetProofTree from (under) the given node.
#     """
#     modified_wgb_children = []
#     index = 0
#     modified = (len(wgb.logical_children) != len(gn.children_goal_nodes))
#     for child_gn in gn.children_goal_nodes:
#         if (len(wgb.logical_children) > index
#                 and wgb.logical_children[index].goal_node is child_gn):
#             modified_wgb_children.append(wgb.logical_children[index])
#         else:  # Create new child_wgb reflecting child_gn:
#             modified = True
#             modified_wgb_children.append(widget_goal_block(child_gn))
#         index += 1
#
#     if modified:  # Some child has been modified, re-set all children
#         wgb.set_children(modified_wgb_children)
#
#     Recursively update children
    # assert len(gn.children_goal_nodes) == len(modified_wgb_children)
    # for wgb, gn in zip(modified_wgb_children, gn.children_goal_nodes):
    #     update_from_nodes(wgb, gn)


def update_from_nodes(wgb: WidgetGoalBlock, gn: GoalNode):
    """
    Recursively update the WidgetProofTree from (under) the given node.
    """
    

class ProofTreeController:
    """
    A class to create and update a ProofTreeWindow that reflects a ProofTree.
    """
    def __init__(self):
        self.proof_tree = None
        self.proof_tree_window = ProofTreeWindow()

    def set_proof_tree(self, proof_tree):
        self.proof_tree = proof_tree

    def update(self):
        if not self.proof_tree.root_node:
            return
        elif not self.proof_tree_window.main_block:
            main_block = widget_goal_block(self.proof_tree.root_node)
            self.proof_tree_window.set_main_block(main_block)

        update_from_nodes(self.proof_tree_window.main_block,
                          self.proof_tree.root_node)


def main():
    app = QApplication()
    main_window = ProofTreeWindow()

    context0=["X", "Y", "f"]
    target0="f surjective ⇒ (∀A ⊂ Y, ∀A' ⊂ Y, ( f⁻¹(A) ⊂ f⁻¹(A') ⇒ A ⊂ A' ) )"
    main_block = WidgetGoalBlock(context1=context0, target=target0)

    main_window.set_main_block(main_block)
    main_window.show()

    # TODO: change to successive IntroBlocks:
    intro1 = IntroImpliesWGB(context=["f surjective"],
                             target="(∀A ⊂ Y, ∀A' ⊂ Y, ( f⁻¹(A) ⊂ f⁻¹(A')"
                                    " ⇒ A ⊂ A' ) )")
    intro2a = IntroWGB(context=["A"],
                       target="∀A' ⊂ Y, f⁻¹(A) ⊂ f⁻¹(A') ⇒ A ⊂ A'")
    intro2b = IntroWGB(context=["A'"], target="f⁻¹(A) ⊂ f⁻¹(A') ⇒ A ⊂ A'")
    intro3 = IntroImpliesWGB(context=["f⁻¹(A) ⊂ f⁻¹(A')"], target="A ⊂ A'")

    main_block.add_children([intro1])
    intro1.add_children([intro2a])
    intro2a.add_children([intro2b])
    intro2b.add_children([intro3])

    intro4 = IntroWGB(context=["y"], target="y ∈ A => y ∈ A'")
    intro5 = IntroImpliesWGB(context=["y ∈ A"], target="y ∈ A'")
    intro3.add_children([intro4])
    intro4.add_children([intro5])

    operator = [(["y"], "f surjective", ["x", "y = f(x)"]),
                (["y ∈ A"], "y = f(x)", ["f(x) ∈ A"]),
                (["f(x) ∈ A"], "definition image réciproque", ["x ∈ f⁻¹(A)"]),
                (["x ∈ f⁻¹(A)"], "f⁻¹(A) ⊂ f⁻¹(A')", ["x ∈ f⁻¹(A')"]),
                (["x ∈ f⁻¹(A')"], "definition image réciproque", ["f(x) ∈ A'"]),
                (["f(x) ∈ A'"], "y = f(x)", ["y ∈ A'"])]
    previous_block = intro5
    for op in operator:
        pure_block = PureContextWGB(*op)
        previous_block.add_children([pure_block])
        previous_block = pure_block

    case_block1 = ByCasesWGB(["y ∈ A"], "First case: y ∈ A")
    case_block2 = ByCasesWGB(["y ∉ A"], "Second case: y ∉ A")
    # case_block1.show()
    previous_block.add_children([case_block1, case_block2])

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

