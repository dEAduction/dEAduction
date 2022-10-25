"""
########################
# help.py: Help window #
########################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 04 2022 (creation)
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

from PySide2.QtCore import Qt, Slot, QSettings, QSize, QTimer

from PySide2.QtWidgets import QDialog, QRadioButton, QVBoxLayout, QHBoxLayout,\
    QTextEdit, QLabel, QDialogButtonBox, QWidget, QPushButton, QFrame, \
    QToolBar, QMainWindow, QAction, QToolButton

from PySide2.QtGui import QIcon  # QKeyEvent, QKeySequence

from typing import Union, Optional

import deaduction.pylib.config.vars as cvars
import deaduction.pylib.utils.filesystem as fs
from deaduction.dui.primitives import deaduction_fonts

from deaduction.pylib.mathobj import ContextMathObject
from deaduction.dui.elements import MathObjectWidgetItem

global _


class HelpTitleWdg(QWidget):
    def __init__(self, nb_help_msgs=1):
        super().__init__()
        icons_base_dir = cvars.get("icons.path")
        icons_dir = fs.path_helper(icons_base_dir)
        self.icon_size = 35
        lyt = QHBoxLayout()

        self.label = QLabel(_("Help"))

        # ----------- Buttons ------------
        # back_icon = QIcon(str((icons_dir / 'icons8-back-48.png').resolve()))
        # forw_icon = QIcon(str((icons_dir / 'icons8-forward-48.png').resolve()))
        self.back_btn = QToolButton()
        self.forward_btn = QToolButton()
        self.back_btn.setArrowType(Qt.LeftArrow)
        self.forward_btn.setArrowType(Qt.RightArrow)
        self.back_btn.setToolTip(_("Previous help message"))
        self.forward_btn.setToolTip(_("Next help message"))
        # self.back_btn.setFixedSize(self.icon_size, self.icon_size)
        # self.forward_btn.setFixedSize(self.icon_size, self.icon_size)
        # self.back_btn.setIconSize(QSize(self.icon_size, self.icon_size))
        # self.back_btn.setIcon(back_icon)
        # self.forward_btn.setIcon(forw_icon)

        hint_icon = QIcon(str((icons_dir / 'icons8-hint-48.png').resolve()))
        self.hint_btn = QToolButton()
        self.hint_btn.setIcon(hint_icon)
        self.hint_btn.setIconSize(QSize(self.icon_size, self.icon_size))
        self.hint_btn.setFixedSize(self.icon_size, self.icon_size)
        self.hint_btn.setCheckable(True)
        self.hint_btn.setAutoRaise(True)
        self.hint_btn.setToolTip(_("Show hint!"))
        # self.fake_hint_btn = QToolButton()
        # self.fake_hint_btn.setFixedSize(self.icon_size, self.icon_size)
        # self.fake_hint_btn.setHidden(True)

        self.OK_btn = QDialogButtonBox()
        self.OK_btn.addButton(QDialogButtonBox.Ok)
        size_policy = self.hint_btn.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.hint_btn.setSizePolicy(size_policy)
        # self.fake_hint_btn.setSizePolicy(size_policy)
        self.total_nb = nb_help_msgs
        self.nb = 1

        # ------------ Layout ------------
        lyt.addWidget(self.hint_btn)
        lyt.addSpacing(20)
        lyt.addWidget(self.back_btn)
        lyt.addWidget(self.label)
        lyt.addWidget(self.forward_btn)
        lyt.addStretch()
        lyt.addWidget(self.OK_btn)
        # lyt.addWidget(self.hint_btn)
        self.setLayout(lyt)

    def set_text(self):
        text = _("Help n°{}").format(self.nb) if self.total_nb > 1 else ""
        self.label.setText(text)

    def set_msgs_total_nb(self, total_nb: int):
        self.total_nb = total_nb
        self.back_btn.setVisible(total_nb > 1)
        self.forward_btn.setVisible(total_nb > 1)
        self.hint_btn.setChecked(False)
        # self.hint_btn.hide()
        self.hint_btn.setEnabled(False)
        if total_nb == 0:
            self.label.hide()
        else:
            self.label.show()
        self.set_text()

    def set_no_msg(self):
        self.set_msgs_total_nb(0)

    def set_msg_nb(self, nb, hint=False):
        self.nb = nb
        self.set_text()
        self.back_btn.setEnabled(self.nb != 1)
        self.forward_btn.setEnabled(self.nb != self.total_nb)
        # self.hint_btn.setVisible(hint)
        self.hint_btn.setEnabled(hint)


class HelpWindow(QDialog):
    """
    A class for a window displaying a help msg, with maybe a small set of
    possible user actions.
    """

    action = None  # Set by exercise_main_window

    def __init__(self):
        super().__init__()

        self.setWindowTitle(_("Help"))
        # Window stay on top of parent:
        self.setWindowFlags(self.windowFlags() | Qt.Dialog)
        # self.main_txt, self.detailed_txt, self.hint = None, None, None
        self.msgs_list = []
        self.main_texts = []
        self.hints = []
        self.target = False
        self.math_wdg_item: Optional[MathObjectWidgetItem] = None
        self.math_object: Optional[ContextMathObject] = None

        self._hiding_forbidden = False

        # Display math_object
        self.math_label = QLabel()
        self.math_label.setTextFormat(Qt.RichText)

        # Display titles
        self.title_widget = HelpTitleWdg()
        self.title_widget.back_btn.clicked.connect(self.previous_help_msgs)
        self.title_widget.forward_btn.clicked.connect(self.next_help_msgs)
        self.title_widget.hint_btn.clicked.connect(self.toggle_hint)
        self.title_widget.OK_btn.clicked.connect(self.accept)

        # Display help msgs
        self.help_wdg = QTextEdit()
        self.help_wdg.setReadOnly(True)

        # Fonts
        text_font = self.help_wdg.font()
        main_size = deaduction_fonts.main_font_size
        text_font.setPointSize(main_size)
        self.help_wdg.setFont(text_font)
        self.title_widget.setFont(text_font)

        target_size = deaduction_fonts.target_font_size
        label_font = self.math_label.font()
        label_font.setPointSize(target_size)
        self.math_label.setFont(label_font)

        # Layout
        self.lyt = QVBoxLayout()
        self.lyt.addWidget(self.math_label)
        self.lyt.addWidget(self.help_wdg)
        self.lyt.addWidget(self.title_widget)
        self.lyt.setAlignment(self.math_label, Qt.AlignHCenter)
        self.setLayout(self.lyt)

        # Shortcuts

        # initialize
        self.empty_content()
        self.set_geometry()

    def set_geometry(self, geometry=None):
        settings = QSettings("deaduction")
        if settings.value("help/geometry"):
            self.restoreGeometry(settings.value("help/geometry"))
        elif geometry:
            self.setGeometry(geometry)

    # def keyPressEvent(self, arg__1) -> None:
    #     if arg__1.matches(QKeySequence.Cancel):
    #         self.closeEvent(arg__1)

    def accept(self) -> None:
        """
        Called by pressing OK.
        """
        self.closeEvent(None)

    def reject(self) -> None:
        """
        Called by pressing the ESC key.
        """
        self.closeEvent(None)

    def closeEvent(self, event):
        # Save window geometry
        self.unset_item()
        settings = QSettings("deaduction")
        settings.setValue("help/geometry", self.saveGeometry())
        self.toggle(yes=False)
        if event:
            event.accept()

    @property
    def icon(self):
        if self.action:
            return self.action.icon()
        else:
            return None

    def empty_content(self):
        """
        Empty all content by displaying a general msg.
        """
        self.math_label.setText("<em>" + _("No object selected") + "</em>")
        self.math_label.setStyleSheet("")
        self.help_wdg.setHtml("<em>" + _("Double click on context or target "
                                         "to get some help.") + "</em>")
        self.title_widget.set_no_msg()

    def display_help_msg(self):
        txt_nb = self.title_widget.nb
        if self.main_texts:
            text = self.main_texts[txt_nb-1]
        else:
            text = "<em> " + _("No help available on this object.") + "</em>"
        self.help_wdg.setHtml(text)

    def display_hint(self):
        txt_nb = self.title_widget.nb
        hint = self.hints[txt_nb-1]
        title = "<em><b>" + _("Hint:") + "</b></em>"
        text = "<p>" + hint + "</p> </em>"
        self.help_wdg.setHtml(title + text)

    def set_msgs(self, msgs_list: [[str, str, str]], from_icon=False):
        """
        Fill-in attributes msgs_list, main_texts, hints.
        Also set the total number of help msgs in self.title_widget, and set
        it to the first help msg. Call self.display_help_msg().
        """
        self.msgs_list = msgs_list
        self.title_widget.set_msgs_total_nb(len(msgs_list))

        self.main_texts = ["<p>" + msgs[0] + "</p>" + "<p>" + msgs[1] + "</p>"
                           for msgs in self.msgs_list]
        self.hints = [msgs[2] for msgs in self.msgs_list]
        hint = bool(self.hints[0]) if self.hints else False
        self.title_widget.set_msg_nb(1, hint=hint)

        self.display_help_msg()

    def display_math_object(self):
        """
        Display the math_object on which help should be provided, according
        to self.math_object.
        """
        if self.math_object.math_type.is_prop():  # target and context props
            math_text = self.math_object.math_type_to_display()
        else:  # context objects, display e.g. "x : element of X".
            math_text = self.math_object.display_with_type(format_='html')

        self.math_label.setText(math_text)
        color = cvars.get("display.color_for_highlight_in_proof_tree",
                          "yellow")
        self.math_label.setStyleSheet(f"background-color: {color};")

    def unset_item(self):
        """
        Clear self from math_object, and un_highlight the math_object in the
        context area if possible.
        """
        if self.math_wdg_item:
            try:  # Maybe context has changed and object no longer exists
                self.math_wdg_item.highlight(yes=False)
            except RuntimeError:
                pass
            self.math_wdg_item = None
        self.math_object = None
        self.empty_content()

    def set_math_object(self,
                        item: Union[MathObjectWidgetItem, ContextMathObject],
                        on_target=False,
                        context_solving=None):
        """
        This should be called each time help is requested on a new
        ContextMathObject.
        This method set the math_object, set msgs. A help msg will be displayed.
        (Also unselect previous item if any.)
        """

        self.unset_item()
        if hasattr(item, 'select') and hasattr(item, 'highlight'):
            item.select(yes=False)
            item.highlight(duration=2000)
            # if self.icon:
            #     item.setIcon(self.icon)
            self.math_wdg_item = item
            self.math_object = item.math_object
        elif isinstance(item, ContextMathObject):
            self.math_object = item

        if self.math_object:
            msgs = (self.math_object.help_target_msg(context_solving)
                    if on_target else
                    self.math_object.help_context_msg(context_solving))

            self.display_math_object()
            self.set_msgs(msgs, from_icon=False)

    def _allow_hiding(self):
        self._hiding_forbidden = False

    def _forbid_hiding(self):
        self._hiding_forbidden = True
        QTimer.singleShot(500, self._allow_hiding)

    @Slot()
    def toggle(self, yes=None):
        """
        Toggle window, and unset item if hidden. After a toggle, toggle is
        forbidden for 400ms. This prevents window from closing right after
        being opened because the second click is registered as an independent
        first click on some OS (e.g. Darwin).
        """

        if yes is None:  # Change state to opposite
            yes = not self.isVisible()
        if yes:
            self.set_geometry()
            self.setVisible(True)
            self.raise_()   # Put in front, needed on Mac
            self.activateWindow()  # Give focus
            self._forbid_hiding()

        elif not self._hiding_forbidden:
            self.unset_item()
            settings = QSettings("deaduction")
            settings.setValue("help/geometry", self.saveGeometry())
            self.setVisible(False)

        self.action.setChecked(self.isVisible())

    @Slot()
    def hide(self):
        self.toggle(yes=False)

    @Slot()
    def toggle_hint(self, yes=None):
        if yes is None:
            checked = self.title_widget.hint_btn.isChecked()
        else:
            self.title_widget.hint_btn.setChecked(yes)
            checked = yes
        if checked:
            self.display_hint()
        else:
            self.display_help_msg()

    @Slot()
    def next_help_msgs(self):
        nb = self.title_widget.nb + 1
        self.title_widget.set_msg_nb(nb, hint=bool(self.hints[nb-1]))
        self.toggle_hint(yes=False)

    @Slot()
    def previous_help_msgs(self):
        nb = self.title_widget.nb - 1
        self.title_widget.set_msg_nb(nb, hint=bool(self.hints[nb-1]))
        self.toggle_hint(yes=False)
