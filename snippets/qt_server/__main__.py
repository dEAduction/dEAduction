"""
A dummy dEAduction main window interface, but with server !
"""
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, \
                              QHBoxLayout, QVBoxLayout, QGridLayout, \
                              QLineEdit, QListWidget, QWidget, QGroupBox, \
                              QLabel, QDesktopWidget, QListWidgetItem, \
                              QPlainTextEdit, QMessageBox

from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem, QTreeView, QListWidget
from PySide2.QtCore import Qt, Signal, Slot
from PySide2.QtGui import QFont, QColor, QBrush, QIcon
import sys

from functools import partial
from pathlib   import Path

import trio
import qtrio
import logging

from deaduction.pylib                             import logger as logger
from deaduction.pylib.server                      import (ServerInterface,
                                                          exceptions)
from deaduction.pylib.coursedata.course           import Course
from deaduction.pylib.mathobj.proof_state         import ProofState
from deaduction.pylib.coursedata.exercise_classes import Exercise


class Goal(QPushButton):
    def __init__(self, goal):
        super().__init__()
        self._initUI()
        self.setText(goal)

    def _initUI(self):
        self.setFont(QFont('Fira Code', 24))
        self.setFlat(True)

    def _resize_width(self):
        txt_width = self.fontMetrics().boundingRect(self.text()).width()
        self.setFixedWidth(txt_width + 40)

    def setText(self, txt):
        super().setText(txt)
        self._resize_width()

class PropobjList(QListWidget):
    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        self.setAlternatingRowColors(True)

class ExerciseWindow(QWidget):
    closed = Signal()

    def __init__(self, nursery, exercise):
        super().__init__()
        self.log = logging.getLogger("Test qt lean")

        self.server = ServerInterface(nursery)
        
        self.exercise   = exercise
        self.statements = self.exercise.course.statements

        self._initUI()

        # Link signals
        self.server.proof_state_change.connect(self.proof_state_update)

        # Start waiter task
        self.server.nursery.start_soon(self.server_task)

        # Update initial proof state
        #self.proof_state_update(self.server.proof_state)

    async def server_task(self):
        await self.server.start()
        await self.server.exercise_set(self.exercise)
        async with qtrio.enter_emissions_channel(signals=[
            self.closed,
            self.send.clicked,
            self.undo.clicked
        ]) as emissions:
            async for emission in emissions.channel:
                if emission.is_from(self.closed):
                    break
                elif emission.is_from(self.send.clicked):
                    await self.go_send()
                elif emission.is_from(self.undo.clicked):
                    await self.go_undo()

        self.server.stop()

    async def go_send(self):
        self.log.info("Send file to lean")
        self.freeze(True)

        txt = self.edit.toPlainText()
        try:
            await self.server.code_set("add", txt)
        except exceptions.FailedRequestError as ex:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Failed lean request")
            msg.setText("I am broken :'(")

            detailed = ""
            for err in ex.errors:
                detailed += f"* at {err.pos_line} : {err.text}\n"

            msg.setDetailedText(detailed)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        self.freeze(False)

    async def go_undo(self):
        self.log.info("Undo")
        self.freeze(True)
        await self.server.history_undo()
        self.edit.setPlainText(self.server.lean_file.inner_contents)
        self.freeze(False)

    def closeEvent(self, ev):
        super().closeEvent(ev)
        self.closed.emit()

    def _initUI(self):
        # Create widgets
        self.objects     = PropobjList()
        self.properties  = PropobjList()

        self.goal        = Goal("TODO")

        self.edit        = QPlainTextEdit()
        self.send        = QPushButton("Send to lean")
        self.undo        = QPushButton("Undo"        )

        self.deflist     = QListWidget()

        # --> Build deflist
        for st in self.statements:
            self.deflist.addItem(st.pretty_name)

        # --> Link signal
        self.deflist.itemClicked.connect(self.add_statement_name)

        # Create layouts
        goal_layout      = QHBoxLayout()
        main_layout      = QVBoxLayout()
        workspace_layout = QHBoxLayout()
        propobj_layout   = QVBoxLayout()
        tools_layout     = QVBoxLayout()
        btns_layout      = QHBoxLayout()

        # Create QGroupBox to have titles
        propobj_gb       = QGroupBox('Properties and objects')
        self.tools_gb    = QGroupBox('Lean code')

        # Put widgets in layouts and group boxes
        goal_layout.addStretch()
        goal_layout.addWidget(self.goal)
        goal_layout.addStretch()

        # Add space below goal
        goal_layout.setContentsMargins(0, 10, 0, 30) #LTRB

        # Build propobj layout
        propobj_layout.addWidget(self.objects)
        propobj_layout.addWidget(self.properties)
        propobj_gb.setLayout(propobj_layout)

        # Build tools layout
        btns_layout.addWidget(self.send)
        btns_layout.addWidget(self.undo)

        tools_layout.addWidget(self.deflist)
        tools_layout.addWidget(self.edit)
        tools_layout.addLayout(btns_layout)

        self.tools_gb.setLayout(tools_layout)

        # Build workspace layout
        workspace_layout.addWidget(propobj_gb)
        workspace_layout.addWidget(self.tools_gb)

        # Don't forget me
        main_layout.addLayout(goal_layout)
        main_layout.addLayout(workspace_layout)
        self.setWindowTitle("d∃∀duction")
        self.setLayout(main_layout)
        self.show()

    def freeze(self,state:bool):
        self.tools_gb.setEnabled(not state)

    @Slot(QListWidgetItem)
    def add_statement_name(self, item):
        st = self.statements[self.deflist.row(item)]
        self.edit.insertPlainText(st.lean_name)

    @Slot(ProofState)
    def proof_state_update(self, po:ProofState):
        # Update goal
        goal   = po.goals[0]
        target = goal.target.math_type.format_as_utf8()

        self.goal.setText(target)

        # Update properties and objects
        self.properties.clear()
        self.objects.clear()
        for type_, instances in goal.math_types:
            utf8 = type_.format_as_utf8(is_type_of_pfpo=True)

            for obj in instances:
                txt = f"{obj.format_as_utf8()} : {utf8}"
                if obj.is_prop(): self.properties.addItem(txt)
                else            : self.objects.addItem(txt)

async def main():
    async with trio.open_nursery() as nursery:
        logger.configure()

        course = Course.from_file(Path("../../tests/lean_files/short_course/exercises.lean"))
        for counter, statement in enumerate(course.statements):
            print(f"Statement n°{counter:2d}: "
                  f"(exercise: {isinstance(statement, Exercise)}) "
                  f"{statement.lean_name}"
                  f" ({statement.pretty_name})")

        statement_id = int(input("Exercice n° ? "))
        exercise     = course.statements[statement_id]

        win          = ExerciseWindow(nursery, exercise)

        async with qtrio.enter_emissions_channel(signals=[win.closed]) as emissions:
            win.show()
            await emissions.channel.receive()

if __name__ == '__main__':
    qtrio.run(main)
