"""
fml
credits to Florian
"""

from PySide2.QtWidgets  import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QTextEdit,
    QPlainTextEdit,
    QPushButton,
    QGroupBox,
    QProgressBar
)
from PySide2.QtCore     import Qt, Signal, Slot, QObject
from PySide2.QtGui      import QColor, QBrush, QIcon
from sys import exit

import trio
import qtrio

import deaduction.pylib.logger as logger
from   deaduction.pylib.lean.server     import LeanServer
from   deaduction.pylib.lean.response   import Message, InfoResponse
from   deaduction.pylib.lean.request    import SyncRequest, InfoRequest

import logging

TEMPLATE=""  
with open("examples/template.lean") as fhandle:
    TEMPLATE=fhandle.read()
    
class SimpleServerInterface(QObject):
    # Qt signals
    running_state_change = Signal(bool)
    message              = Signal(Message)

    ########################################
    # Callbacks
    ########################################
    def _on_state_change(self,st): self.running_state_change.emit(st)
    def _on_message(self,msg):     self.message.emit(msg)

    ########################################
    # Public functions
    ########################################
    def __init__( self, nursery ):
        super().__init__()

        self.log = logging.getLogger(self.__class__.__name__)
        self.srv = LeanServer(nursery)

        # Set callbacks
        self.srv.running_monitor.on_state_change_callback = self._on_state_change
        self.srv.on_message_callback                      = self._on_message

    async def start(self):
        self.log.info("Start lean server")
        await self.srv.start()

    def stop(self):
        self.srv.stop()

    async def send(self, req):
        return await self.srv.send(req)

class MainWindow(QWidget):
    closed = Signal()

    def _editPos(self):
        """
        Quick and dirty way to retrieve line/col from textedit
        """
        pos = self.w_edit_textedit.textCursor().position()
        txt = self.w_edit_textedit.toPlainText()

        line = 0
        col  = 0
        idx  = 0

        while (idx <= pos) and (idx < len(txt)):
            if txt[idx] == "\n":
                col   = 0
                line += 1
            else: col += 1
            idx += 1

        return (line,col)

    def __init__( self, nursery, srv, parent=None ):
        super().__init__( parent )
        self.srv = srv
        self.nursery = nursery
        
        self.log     = logging.getLogger("test lean qt")

        self.setWindowTitle("Test lean")

        ########################################
        # Layout setup
        ########################################
        # Left group box
        self.w_edit_groupbox   = QGroupBox("Edit", parent=self)
        self.w_edit_layout     = QVBoxLayout()

        self.w_edit_textedit   = QPlainTextEdit(TEMPLATE, parent=self.w_edit_groupbox)
        self.w_edit_button     = QPushButton("Send to lean", parent=self.w_edit_groupbox)
        self.w_info_button     = QPushButton("Info"        , parent=self.w_edit_groupbox)

        self.w_edit_layout.addWidget(self.w_edit_textedit)
        self.w_edit_layout.addWidget(self.w_edit_button)
        self.w_edit_layout.addWidget(self.w_info_button)
        self.w_edit_groupbox.setLayout(self.w_edit_layout)

        # Right results box
        self.w_result_groupbox = QGroupBox("Résultats", parent=self )
        self.w_result_layout   = QVBoxLayout()

        self.w_result_textedit = QTextEdit(""         , parent=self.w_result_groupbox)
        self.w_result_progress = QProgressBar(self.w_result_groupbox)
        self.w_result_progress.setFormat("Lean is running...")

        self.w_result_layout.addWidget(self.w_result_textedit)
        self.w_result_layout.addWidget(self.w_result_progress)
        self.w_result_groupbox.setLayout(self.w_result_layout)

        # Global layout
        self.w_layout = QHBoxLayout()
        self.w_layout.addWidget(self.w_edit_groupbox)
        self.w_layout.addWidget(self.w_result_groupbox)

        self.setLayout(self.w_layout)

        ########################################
        # Widget states
        ########################################
        self.set_lean_running(False)

        ########################################
        # Events setup
        ########################################
        self.srv.message.connect(self._on_message)
        self.srv.running_state_change.connect(self.set_lean_running)

        self.nursery.start_soon(self.wait_send_task)

    async def wait_send_task(self):
        async with qtrio.enter_emissions_channel(signals=[
            self.closed, self.w_edit_button.clicked, self.w_info_button.clicked
        ]) as emissions:
            async for emission in emissions.channel:
                if   emission.is_from(self.closed)               : break
                elif emission.is_from(self.w_edit_button.clicked): await self.on_send_to_lean()
                elif emission.is_from(self.w_info_button.clicked): await self.on_lean_info()

        self.log.info("Exit")

    def closeEvent(self, ev):
        super().closeEvent(ev)
        self.closed.emit()

    async def on_send_to_lean(self):
        txt = self.w_edit_textedit.toPlainText()

        req = SyncRequest(file_name="memory", content=txt)

        self.w_edit_button.setEnabled(False)
        resp = await self.srv.send(req)
        if resp.response == "ok" and resp.message == "file invalidated":
            self.w_result_textedit.clear()

        self.w_edit_button.setEnabled(True)
    
    async def on_lean_info(self):
        line,col = self._editPos()
        self.log.info(f"get info at line {line} and column {col}" )

        req  = InfoRequest(file_name="memory", line=line, column=col )
        resp = await self.srv.send(req)

        if isinstance(resp, InfoResponse):
            rec = resp.record
            txt = f"\n{repr(rec)}"

            self.w_result_textedit.append(txt)

    @Slot(bool)
    def set_lean_running(self,st):
        if st:
            self.w_result_progress.setEnabled(True)
            self.w_result_progress.setRange(0,0)
        else:
            self.w_result_progress.setEnabled(False)
            self.w_result_progress.setRange(0,100)

    ########################################
    # Callbacks
    ########################################
    @Slot(Message)
    def _on_message(self,msg):
        txt = f"\n{msg.file_name} at {msg.pos_line}:{msg.pos_col}\n" \
              f"---------------------------------------------\n"   \
              f"{msg.caption} : {msg.text}\n"

        self.w_result_textedit.append(txt)

async def main():
    async with trio.open_nursery() as nursery:
        logger.configure()

        srv = SimpleServerInterface(nursery)
        win = MainWindow(nursery, srv)

        async with qtrio.enter_emissions_channel(signals=[win.closed]) as emissions:
            await srv.start()

            win.show()
            await emissions.channel.receive()

        srv.stop()

if __name__=="__main__":
    qtrio.run(main)
