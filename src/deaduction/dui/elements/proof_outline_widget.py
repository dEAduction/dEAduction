"""
# proof_outline_widget.py : A class derived from QTreeWidget to display
proof outline

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 07 2021 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the d∃∀duction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    d∃∀duction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""
import sys
import logging
from PySide2.QtCore import    ( Qt, Slot, QSettings )
from PySide2.QtGui import       QColor
from PySide2.QtWidgets import ( QTreeWidget,
                                QTreeWidgetItem,
                                QToolTip,
                                QApplication )

from deaduction.pylib.mathobj.proof_step import Proof, ProofNode, ProofStep

log = logging.getLogger(__name__)


class ProofNodeTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, parent, text: str):
        """
        """

        super().__init__(parent)
        self.setText(0, text)

    def insert(self, proof_item):
        # TODO: remove
        if isinstance(proof_item, ProofNode):
            # Insert proof node, and recursively insert items of its sub_proof
            #  as children
            proof_node_twi = ProofNodeTreeWidgetItem(self, proof_item.txt)
            proof_node_twi.setTextColor(0, QColor("blue"))
            for item in proof_item.sub_proof:
                proof_node_twi.insert(item)
        elif isinstance(proof_item, ProofStep):
            # Insert item
            proof_widget_item = QTreeWidgetItem(self)
            proof_widget_item.setText(0, proof_item.success_msg)
            if proof_item.is_action_button():
                proof_widget_item.setText(1, proof_item.button.symbol)
            elif proof_item.is_statement():
                name = proof_item.statement_item.statement.pretty_name
                proof_widget_item.setText(1, name)
            selection_names = [item.display_name for item in
                               proof_item.selection]
            selection = ', '.join(selection_names)
            proof_widget_item.setText(2, selection)

    # def clear(self):
    #     log.debug(f"Removing {self.childCount()} children")
    #     for child_nb in range(self.childCount()):
    #         self.removeChild(self.child(child_nb))


class ProofOutlineTreeWidget(QTreeWidget):
    """
    Nodes       = goal msgs (e.g. "Proof of first implication...")
    Items       =   success msgs (e.g. "Object x added to the context"),
                    buttons / statement name
                    objects/properties involved
    tooltips    = proof states
    User may travel in the history by clicking on an item.

    The widget is initialised with a proof outline which is a tree
        - whose nodes are goal msgs
        - whose leaves are success msgs and associated data
    e.g. ["Proof of first implication", [  ("Object x added to the context",
                                            "∀",
                                            "Goal"),
                                            [<data associated to next step>] ],
          "Proof of second implication", [ <list of steps for second
                                            implication> ]
            ]
    """
    proof_node_color = QColor('blue')

    def __init__(self):
        """
        """

        super().__init__()
        settings = QSettings("deaduction")
        if settings.value("proof_outline/geometry"):
            self.restoreGeometry(settings.value("proof_outline/geometry"))
        if settings.value("proof_outline/state"):
            self.setState(settings.value("proof_outline/state"))

        self.setColumnCount(3)
        header_labels = ["Success messages", "Action", "Objects involved"]
        self.setHeaderLabels(header_labels)
        self.setSortingEnabled(False)

        self.proof = []

    def insert(self, tree_widget_item, proof_item):
        # Fixme: static method
        if isinstance(proof_item, ProofNode):
            # Insert proof node, and recursively insert items of its sub_proof
            #  as children
            proof_node_twi = ProofNodeTreeWidgetItem(tree_widget_item,
                                                     proof_item.txt)
            proof_node_twi.setTextColor(0, self.proof_node_color)
            for item in proof_item.sub_proof:
                self.insert(proof_node_twi, item)
        elif isinstance(proof_item, ProofStep):
            # Insert item
            proof_widget_item = QTreeWidgetItem(tree_widget_item)
            proof_widget_item.setText(0, proof_item.success_msg)
            if proof_item.is_action_button():
                proof_widget_item.setText(1, proof_item.button.symbol)
            elif proof_item.is_statement():
                name = proof_item.statement_item.statement.pretty_name
                proof_widget_item.setText(1, name)
            selection_names = [item.display_name for item in
                               proof_item.selection]
            selection = ', '.join(selection_names)
            proof_widget_item.setText(2, selection)

    @Slot()
    def set_proof(self, proof: Proof, proof_step_number=-1):
        """

        :param proof:
        :param proof_step_number: the current proof step
        :return:
        """
        # FIXME: proof should not be built from scratch each time, otherwise
        #  it will not be possible to keep state (expanded items)
        #  We should rather compare the new proof with self.proof,
        #  and make changes accordingly
        # TODO: highlight current proof step
        # TODO: color for proof node msgs
        self.proof = proof
        # Clear widget
        self.clear()
        # Build it from scratch
        root = self.invisibleRootItem()
        for item in proof:
            self.insert(root, item)

    def closeEvent(self, event):
        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("proof_outline/geometry", self.saveGeometry())
        settings.setValue("proof_outline/state", self.state())
        event.accept()
        self.hide()

    #########
    # Slots #
    #########

    @Slot()
    def toggle(self):
        self.setVisible(not self.isVisible())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    potw = ProofOutlineTreeWidget(None)
    goal1 = QTreeWidgetItem(potw)
    goal1.setText(0, "Proof of first implication")
    step1 = QTreeWidgetItem(goal1)
    step1.setText(0, "Object x added to the context")
    step1.setText(1, "∀")
    step1.setText(2, "Goal")
    step2 = QTreeWidgetItem(goal1)
    step2.setText(0, "Object x' added to the context")
    step2.setText(1, "∀")
    step2.setText(2, "Goal")
    goal2 = QTreeWidgetItem(potw)
    goal2.setText(0, "Proof of second implication")
    step1 = QTreeWidgetItem(goal2)
    step1.setText(0, "Object y added to the context")
    step1.setText(1, "∀")
    step1.setText(2, "Goal")

    potw.show()

    sys.exit(app.exec_())
