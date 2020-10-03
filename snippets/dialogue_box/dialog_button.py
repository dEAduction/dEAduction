"""
# dialog_button.py : <#ShortDescription> #

    <#optionalLongDescription>

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 10 2020 (creation)
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
from PySide2.QtWidgets import QApplication, QDialog, QLabel, QPushButton, \
    QVBoxLayout, QHBoxLayout
from functools import partial


class ButtonsDialog(QDialog):

    def __init__(self, title, choice_list, parent=None):
        """

        :param title:       window title
        :param choice_list: list of couples (caption, text) where caption
        will be the text in the button, and text will be displayed as the
        corresponding choice
        """
        super(ButtonsDialog, self).__init__(parent)
        # self.setWindowTitle(title)

        self.choice = 0
        self.buttons = []
        self.choices = []
        layout = QVBoxLayout()

        # title line
        title_line = QLabel(title, self)
        title_layout = QHBoxLayout()
        title_layout.addStretch(1)
        title_layout.addWidget(title_line)
        title_layout.addStretch(1)
        layout.addLayout(title_layout)

        # Buttons and corresponding texts
        for caption, choice in choice_list:
            new_button = QPushButton(caption)
            self.buttons.append(new_button)
            self.choices.append(QLabel(choice, self))
            new_layout = QHBoxLayout()
            new_layout.addWidget(self.buttons[-1])
            new_layout.addWidget(self.choices[-1])
            new_layout.addStretch(1)
            layout.addLayout(new_layout)

        self.cancel = QPushButton("Cancel")
        new_layout = QHBoxLayout()
        new_layout.addStretch(1)
        new_layout.addWidget(self.cancel)
        new_layout.addStretch(1)
        layout.addLayout(new_layout)
        self.cancel.clicked.connect(self.reject)
        self.setLayout(layout)

        for button in self.buttons:
            # call the button_clicked function with the right number
            button.clicked.connect(partial(button_clicked,
                                           number=self.buttons.index(button),
                                           box=self))


if __name__ == '__main__':
    button_choice = None


    def button_clicked(number, box):
        global button_choice
        button_choice = number
        box.accept()


    # Create the Qt Application
    app = QApplication(sys.argv)

    # Example
    choice_list = [("⇒", "x ∈ A ∩ (B ∪ C) ⇒ x ∈ A ∩ B ∪ A ∩ C"),
                   ("<=", "x ∈ A ∩ B ∪ A ∩ C ⇒ x ∈ A ∩ (B ∪ C)")]
    dialog = ButtonsDialog(title="Make up your choice!",
                           choice_list=choice_list)
    dialog.exec()
    print(f"Choice = button n°{button_choice}")
