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
from PySide2.QtWidgets import ( QApplication, QFrame, QLayout,
                                QHBoxLayout, QVBoxLayout, QGridLayout,
                                QLineEdit, QListWidget, QWidget, QGroupBox,
                                QLabel, QTextEdit, QSizePolicy)
from PySide2.QtWidgets import QScrollArea
from PySide2.QtCore import Qt, QLine, QRect
from PySide2.QtGui import QFont, QColor, QBrush, QIcon, QPainter, QPen, QPixmap
import sys

import deaduction.pylib.config.vars as cvars
import deaduction.pylib.config.dirs as cdirs


def right_arrow():
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

    def mousePressEvent(self, ev) -> None:
        """
        Modify self's appearance and call the slot function.
        """
        self.setText("▷" if self.text() == "▽" else "▽")
        self.slot()


class ProofStepBlock(QWidget):
    """
    This widget is responsible for displaying one step of a proof, involving
    only context objects (e.g. modus ponens).
    """

    def __init__(self, premises, operator, conclusions):
        super().__init__()
        premises_layout = QVBoxLayout()
        conclusions_layout = QVBoxLayout()
        main_layout = QHBoxLayout()

        self.premises = premises
        self.operator = operator
        self.conclusions = conclusions

        for hypo in self.premises:
            premises_layout.addWidget(QLabel(hypo))
        premises_layout.setAlignment(Qt.AlignRight)

        for prop in self.conclusions:
            conclusions_layout.addWidget(QLabel(prop))
        conclusions_layout.setAlignment(Qt.AlignLeft)

        operator_label = QLabel(self.operator)
        operator_label.setFrameShape(QFrame.StyledPanel)
        operator_label.setFrameShadow(QFrame.Sunken)

        main_layout.addLayout(premises_layout)
        main_layout.addWidget(right_arrow())
        main_layout.addWidget(operator_label)
        main_layout.addWidget(right_arrow())
        main_layout.addLayout(conclusions_layout)
        main_layout.setAlignment(Qt.AlignLeft)

        self.setLayout(main_layout)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


class GoalBlockContent(QWidget):
    """
    This widget draws the content of some GoalBlock.
    """

    # FIXME: bad frame line, add an empty widget with width = title_width
    #  as a first widget?
    def __init__(self, title_width: callable, end_msg=""):
        super().__init__()
        self.title_width = title_width  # NB: this is a function (real time)
        self.end_msg_label = QLabel(end_msg)
        self.end_msg_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.cqfd = False  # Modified by parent

        self.vert_layout = QVBoxLayout()
        self.vert_layout.addWidget(self.end_msg_label)
        self.setLayout(self.vert_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        my_color = QColor(0, 0, 255, 255)
        my_pen = QPen(my_color)
        my_pen.setWidth(5)
        painter.setPen(my_pen)
        # brush = QBrush(my_color)
        # painter.setBrush(brush)
        # painter.drawRect(0, 0, self.title_width(), self.height())
        # painter.begin(self)
        painter.drawLine(0, 0, self.title_width(), 0)
        painter.drawLine(0, 0, 0, self.height())
        if self.cqfd:
            painter.drawLine(0, self.height(),
                             self.end_msg_label.width(), self.height())

        painter.end()

    def add_child(self, child: QWidget):
        """
        Add the child just before the last widget (which is the end msg)
        """
        self.vert_layout.insertWidget(self.vert_layout.count()-1, child)

    def set_end_msg(self, msg):
        self.end_msg_label.setText(msg)


class GoalBlock(QWidget):
    """
    This widget displays a proof block, with a title which indicates
    what is proved. The display has two versions, hidden or disclosed.
    """

    def __init__(self, title="", hidden=False, cqfd=False):
        super().__init__()
        self.hidden = False
        self.children: [Union[GoalBlock, ProofStepBlock]] = []
        self.title = title
        self._cqfd = cqfd

        # Layout
        self.triangle = DisclosureTriangle(self.disclose, hidden=hidden)
        self.triangle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.title_label = QLabel(text=self.title + ":")  # Fixme: translation
        self.title_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.content = GoalBlockContent(title_width=self.title_label.width,
                                        end_msg=self.end_msg)
        self.content.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout = QGridLayout()  # 2x2
        layout.addWidget(self.triangle, 0, 0)
        layout.addWidget(self.title_label, 0, 1)
        layout.addWidget(self.content, 1, 1)
        layout.setAlignment(Qt.AlignLeft)
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        self.setLayout(layout)

        if hidden:
            self.disclose()

    @property
    def sub_goals(self):
        return filter(lambda it: isinstance(it, GoalBlock), self.children)

    @property
    def cqfd(self):
        """
        True iff this goal is complete, and so are all its sub-goals.
        """
        children_cqfd = [child.cqfd for child in self.sub_goals]
        # print(len(self.children), children_cqfd)
        return self._cqfd and all(children_cqfd)

    @property
    def end_msg(self) -> str:
        if self.cqfd:
            return "Goal!"
        else:
            return "(under construction...)"

    def changeEvent(self, event):
        """
        Dynamically change the end msg to display QED if proof is complete.
        """
        if self.cqfd != self.content.cqfd:
            self.content.set_end_msg(self.end_msg)
            self.content.cqfd = self.cqfd

    def disclose(self):
        self.hidden = not self.hidden
        if self.hidden:
            self.layout().takeAt(2)  # Content is the third layoutItem
            self.content.hide()
            self.title_label.setText(self.title)
        else:
            self.layout().addWidget(self.content, 1, 1)
            self.title_label.setText(self.title + ":")
            self.content.show()

    def add_child(self, child):
        self.children.append(child)
        self.content.add_child(child)


class GraphicProof(QScrollArea):
    """
    This class holds the main proof tree window.
    Its widget is a GoalBlock that holds the initial goal of the proof.
    """
    def __init__(self, title):
        super().__init__()
        main_proof_block = GoalBlock(title=title, cqfd=True)
        # self.current_goal_block = main_proof_block
        self.setWidget(main_proof_block)
        self.setWindowTitle("Proof Tree")

    def add_child(self, child: Union[GoalBlock, ProofStepBlock]):
        # if self.current_goal_block.is_solved():
        #     pass
        self.widget().add_child(child)
        # if isinstance(child, GoalBlock):
        #     self.current_goal_block = child  # Fixme

    @classmethod
    def from_proof_tree(cls):
        pass


def main():
    app = QApplication()

    # Tests
    child3 = GoalBlock(title="SubGoal1bis", hidden=False, cqfd=True)
    child3.add_child(ProofStepBlock([], "", []))
    child4 = GoalBlock(title="SubGoal2", hidden=False)
    child4.add_child(ProofStepBlock([], "", []))
    child4.add_child(ProofStepBlock([], "", []))
    child4.add_child(ProofStepBlock([], "", []))
    title = "Proof of: (f surjective) ⇒ (∀ A ⊂ Y, ∀ A' ⊂ Y, ( f⁻¹(A) ⊂ f⁻¹(A') " \
            "⇒ A ⊂ A' ) )"
    proof = GraphicProof(title)

    proof.show()

    proof.add_child(QLabel("f surjective"))
    proof.add_child(QLabel("A ⊂ Y"))
    proof.add_child(QLabel("A' ⊂ Y"))
    proof.add_child(QLabel("f⁻¹(A) ⊂ f⁻¹(A')"))
    child1 = GoalBlock(title="Proof of A ⊂ A'", cqfd=True)
    proof.add_child(child1)

    child1.add_child(QLabel("y"))
    child1.add_child(QLabel("y ∈ A"))

    child2 = GoalBlock(title="Proof of y ∈ A'", hidden=False, cqfd=True)
    child1.add_child(child2)

    child2.add_child(ProofStepBlock(["y"], "f surjective", ["x", "y = f(x)"]))
    child2.add_child(ProofStepBlock(["y ∈ A"], "y = f(x)", ["f(x) ∈ A"]))
    child2.add_child(ProofStepBlock(["f(x) ∈ A"], "definition", ["x ∈ f⁻¹(A)"]))
    child2.add_child(ProofStepBlock(["x ∈ f⁻¹(A)"], "f⁻¹(A) ⊂ f⁻¹(A')",
                                    ["x ∈ f⁻¹(A')"]))
    child2.add_child(ProofStepBlock(["x ∈ f⁻¹(A')"], "definition", ["f(x) ∈ "
                                                                    "A'"]))
    child2.add_child(ProofStepBlock(["f(x) ∈ A'"], "y = f(x)", ["y ∈ A'"]))

    # proof.add_child(child4)

    # child3.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()





