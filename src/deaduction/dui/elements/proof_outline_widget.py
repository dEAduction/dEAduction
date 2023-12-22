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
from typing import Union
from PySide2.QtCore import    ( Qt, Signal, Slot, QSettings )
from PySide2.QtGui import     ( QColor, QBrush, QKeySequence )
from PySide2.QtWidgets import ( QTreeWidget,
                                QTreeWidgetItem,
                                QApplication,
                                QWidget,
                                QPushButton,
                                QCheckBox,
                                QVBoxLayout,
                                QHBoxLayout)

from deaduction.pylib.proof_step.proof_step import ProofNode, ProofStep

log = logging.getLogger(__name__)
global _


class ProofTreeWidgetItem(QTreeWidgetItem):
    """
    A QTreeWidgetItem corresponding to some proof_step.
    Note that for a proof_step that is a node, two ProofTreeWidgetItem will
    be created, one for the proof_step itself and one for the node.
    """
    proof_node_color = QColor('blue')

    def __init__(self, parent, proof_item: Union[ProofStep, ProofNode]):
        """
        An item in the ProofOutlineTreeWidget, representing proof_item.
        """
        super().__init__(parent)
        self.proof_item = proof_item
        self.expansion_memory = True
        if isinstance(proof_item, ProofNode):
            self.setText(0, proof_item.txt)
            self.setTextColor(0, self.proof_node_color)
        else:
            self.setText(0, proof_item.txt)
            if proof_item.is_action_button():
                self.setText(1, _(proof_item.button_symbol))
            elif proof_item.is_statement():
                name = proof_item.statement.pretty_name
                self.setText(1, name)
            selection_names = [item.display_name for item in
                               proof_item.selection]
            selection = ', '.join(selection_names)
            self.setText(2, selection)
            if proof_item.proof_state:
                goal = proof_item.proof_state.goals[0]
                if goal:
                    tooltip = goal.to_tooltip()
                    self.setToolTip(0, tooltip)

    def __eq__(self, other):
        """
        Necessary since it is not implemented in some versions of PyQt!!
        :param other:
        :return:
        """
        return self is other

    def mark_user_selected(self, yes: bool=True):
        """
        Change self's background to green if yes or to normal color
        (e.g. white in light mode) if not yes.

        :param yes: See paragraph above.
        """

        # TODO: change color for double-click

        self.setBackground(0,QBrush(QColor('limegreen')) if yes else QBrush())

    def is_node(self):
        return isinstance(self.proof_item, ProofNode)

    @property
    def debug(self):
        proof_item = self.proof_item
        return proof_item.txt
        # if isinstance(proof_item, ProofNode):
        #     return proof_item.txt
        # else:
        #     return proof_item.success_msg


class ProofOutlineTreeWidget(QTreeWidget):
    """
    At every moment, there is at most one selected item, which is the
    current item if it exists.
    There is also exactly one marked item, which corresponds to current
    state of the Lean file.
    """

    def __init__(self):

        super().__init__()
        self.setColumnCount(3)
        header_labels = [_("Messages"), _("Action"), _("Objects involved")]
        self.setHeaderLabels(header_labels)
        self.setSortingEnabled(False)

        # Set columns width
        # Fixme: does not work
        settings = QSettings("deaduction")
        default_col_width = [300, 50, 50]
        for col_nb in (0, 1, 2):
            col_width = settings.value(f"proof_outline_tree/{col_nb}")
            try:  # Fixme
                col_width = int(col_width)
            except:  # ValueError, TypeError
                log.warning(f"col_width is not str or int, type = "
                            f"{type(col_width)}")
                col_width = default_col_width[col_nb]
            self.setColumnWidth(col_nb, col_width)

        self.widgets: [ProofOutlineTreeWidget] = []

        # Signals
        self.itemClicked.connect(self.item_clicked)
        self.currentItemChanged.connect(self.current_item_changed)

    @property
    def widgets_debug(self):
        return [widget.debug for widget in self.widgets]

    def save_state(self):
        """
        Called when parent window is closed. Save columns width.
        """
        # Save columns width
        settings = QSettings("deaduction")
        for col_nb in (0, 1, 2):
            columns_width = self.columnWidth(col_nb)
            # log.debug(f"Saving column width {columns_width}")
            settings.setValue(f"proof_outline_tree/{col_nb}", columns_width)

    def select(self, selected_widget):
        """
        Select selected_widget and un-select all other widgets.
        """
        for widget in self.widgets:
            widget.setSelected(widget is selected_widget)

    @Slot()
    def item_clicked(self, selected_widget, column):
        self.select(selected_widget)

    @Slot()
    def current_item_changed(self):
        self.select(self.currentItem())

    def __delete(self, widget_item: ProofTreeWidgetItem):
        # log.debug(f"Deleting {widget_item.proof_item.txt}")
        parent = widget_item.parent()
        if not parent:
            self.takeTopLevelItem(self.indexOfTopLevelItem(widget_item))
        else:
            parent.removeChild(widget_item)

    def __delete_from(self, widget_item):
        index = self.widgets.index(widget_item)
        for widget in self.widgets[index:]:
            self.__delete(widget)
        self.widgets = self.widgets[:index]

    def __find_proof_item(self, proof_item) -> ProofTreeWidgetItem:
        """
        Return FIRST widget matching proof_item.
        """
        for widget in self.widgets:
            if widget.proof_item == proof_item:
                return widget

    def __find_history_nb(self, idx) -> ProofTreeWidgetItem:
        """
        Return FIRST widget matching history_nb.
        """
        for widget in self.widgets:
            if widget.proof_item.history_nb == idx:
                return widget

    def __insert_at_end(self, proof_item) -> ProofTreeWidgetItem:
        """
        Insert proof_item as a child of the ProofTreeWidgetItem
        corresponding to proof_item.parent,
        creating a TreeWidgetItem
        for proof_item.parent beforehand if needed.
        NB: insertion must be done only at the end, so that self.widgets
        list is accurate.
        """

        # Debug
        # log.debug(f"Inserting item {proof_item.txt}")
        widgets = []  # Fixme: return all inserted widgets
        # Search for parent node
        if proof_item.parent:
            # log.debug(f"   parent step: {proof_item.parent.txt}")
            parent = proof_item.parent
            if parent.txt == "Proof":
                parent_item = self.invisibleRootItem()
            else:
                parent_item = self.__find_proof_item(parent)
                if not parent_item:
                    # log.debug(f"   creating parent item {parent.txt}")
                    parent_item = self.__insert_at_end(parent)
            if parent_item:
                parent_item.setExpanded(True)
        else:
            parent_item = self.invisibleRootItem()
        # log.debug(f"   inserting item at {parent_item.text(0)}")
        new_widget_item = ProofTreeWidgetItem(parent=parent_item,
                                              proof_item=proof_item)
        self.widgets.append(new_widget_item)
        # log.debug("New list:")
        # log.debug(self.widgets_debug)
        return new_widget_item

    def delete_and_insert(self, proof_step: ProofStep):
        """
        """

        # Delete
        history_nb = proof_step.history_nb
        widget = self.__find_history_nb(history_nb)
        if widget:
            self.__delete_from(widget)

        # Insert
        new_widget = self.__insert_at_end(proof_step)
        new_proof_node = proof_step.imminent_new_node
        if new_proof_node:
            self.__insert_at_end(new_proof_node)

        # Mark widget
        self.set_marked(new_widget)

    def delete_after_goto_and_error(self, proof_step):
        history_nb = proof_step.history_nb # Do NOT delete current proof_step
        widget = self.__find_history_nb(history_nb)
        if widget:
            self.__delete_from(widget)

    def set_marked(self, marked_widget: Union[int, ProofTreeWidgetItem]):
        """
        Mark the widget corresponding to history_nb as user selected,
        and un-mark all other widgets. Un-select all widgets.
        """
        if isinstance(marked_widget, int):
            history_nb = marked_widget
            marked_widget = self.__find_history_nb(history_nb)
            # log.debug(f"Marking widget {history_nb}")
        for widget in self.widgets:
            widget.mark_user_selected(widget == marked_widget)
            widget.setSelected(False)

        self.scrollToItem(marked_widget)


class ProofOutlineWindow(QWidget):
    """
    A widget for representing proof outline.
    """
    history_goto = Signal(int)  # Move to proof step,
    action = None  # To be set to the QAction of exercise_toolbar
    #  nb is lean_file.target_idx

    def __init__(self):
        super().__init__()
        settings = QSettings("deaduction")
        if settings.value("proof_outline/geometry"):
            self.restoreGeometry(settings.value("proof_outline/geometry"))

        self.tree = ProofOutlineTreeWidget()

        self.setWindowTitle(_("List of proof steps") + " — d∃∀duction")
        # Buttons
        self.expand_btn = QCheckBox(_("Expand all"))
        self.details_btn = QCheckBox(_("Show details"))
        self.details_btn.setChecked(True)
        self.move_btn = QPushButton(_('Move to selected step'))
        self.move_btn.setDefault(True)
        self.move_btn.setShortcut(QKeySequence(Qt.Key_Return))

        # Layouts
        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        main_layout.addWidget(self.tree)
        btn_layout.addStretch()
        btn_layout.addWidget(self.expand_btn)
        btn_layout.addWidget(self.details_btn)
        btn_layout.addWidget(self.move_btn)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        # Signals
        # ─────────── Signals ────────── #
        self.tree.itemDoubleClicked.connect(self.history_goto_btn)
        self.move_btn.clicked.connect(self.history_goto_btn)
        self.expand_btn.clicked.connect(self.expand_all)
        self.details_btn.clicked.connect(self.show_details)

        # self.move_btn.clicked.connect

    def closeEvent(self, event):
        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("proof_outline/geometry", self.saveGeometry())
        self.tree.save_state()
        event.accept()
        self.hide()
        if self.action:
            self.action.setChecked(False)

    #########
    # Slots #
    #########

    @Slot()
    def toggle(self):
        self.setVisible(not self.isVisible())
        if self.action:
            self.action.setChecked(self.isVisible())

    @Slot()
    def history_goto_btn(self, *args):
        # log.debug(f"History move, args: {args}")
        tree_widget_item = self.tree.currentItem()
        if tree_widget_item and not tree_widget_item.is_node():
            # log.debug(f"History move to "
            #           f"{tree_widget_item.proof_item.history_nb}")
            self.history_goto.emit(tree_widget_item.proof_item.history_nb+1)

    @Slot()
    def expand_all(self):
        expand = self.expand_btn.isChecked()
        if expand:
            for widget in self.tree.widgets:
                if widget.is_node():
                    widget.expansion_memory = widget.isExpanded()
                    widget.setExpanded(True)
        else:
            for widget in self.tree.widgets:
                if hasattr(widget, "expansion_memory"):
                    widget.setExpanded(widget.expansion_memory)

    @Slot()
    def show_details(self):
        show = self.details_btn.isChecked()
        self.tree.setColumnCount(3 if show else 1)
        for widget in self.tree.widgets:
            if not widget.is_node():
                widget.setHidden(not show)


# def next_value(it: iter):
#     try:
#         return next(it).value()
#     except ValueError:
#         return None
#     except StopIteration:
#         return None


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

