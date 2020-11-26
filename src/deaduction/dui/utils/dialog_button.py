"""
################################################
# dialog_button.py : a dialog box with buttons #
################################################

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
from PySide2.QtWidgets import   QApplication, QDialog, QLabel, QPushButton, \
                                QVBoxLayout, QHBoxLayout
from functools import partial


class ButtonsDialog(QDialog):
    """
    A class for displaying a dialog box with several choices displayed as
    QPushButtons
    """
    def __init__(self,
                 choices,
                 title          = "",
                 output         = "",
                 cancel_button  = False,
                 choice         = None,
                 parent         = None):
        """
        :param choices:  list of couples (caption, text) where caption
                             will be the text in the button, and text will
                             be displayed as the corresponding choice
        :param title:        window title
        :param output:     output, appears inside window
        :type cancel_button: if True then a Cancel button will appear
        :type choice:        contains either None or the number of the
                             chosen button
        """
        super(ButtonsDialog, self).__init__(parent)
        self.setWindowTitle(title)

        self.output = output
        self.buttons = []
        self.choices = []
        self.choice = choice

        # Display #
        layout = QVBoxLayout()

        # title line
        output_line = QLabel(output, self, StyleSheet='font-weight: bold;')
        output_layout = QHBoxLayout()
        output_layout.addWidget(output_line)
        output_layout.addStretch(1)

        # Filling the lines
        layout.addLayout(output_layout)  # 1st line
        layout.addSpacing(5)

        # Buttons and corresponding texts, one new_layout per line
        for caption, choice in choices:
            new_button = QPushButton(caption)
            self.buttons.append(new_button)
            self.choices.append(QLabel(choice, self))
            new_layout = QHBoxLayout()

            new_layout.addWidget(self.buttons[-1])
            new_layout.addWidget(self.choices[-1])
            new_layout.addStretch(1)
            layout.addLayout(new_layout)
            layout.addSpacing(-5)

        # Cancel button
        if cancel_button:
            self.cancel = QPushButton("Cancel")
            new_layout = QHBoxLayout()
            new_layout.addStretch(1)
            new_layout.addWidget(self.cancel)
            new_layout.addStretch(1)
            layout.addLayout(new_layout)

        layout.setContentsMargins(10, 10, 10, 20)
        self.setLayout(layout)

        # Signals
        if cancel_button:
            self.cancel.clicked.connect(self.reject)
        for button in self.buttons:
            # call the button_clicked function with the right number
            button.clicked.connect(partial(self.button_clicked,
                                           number=self.buttons.index(button)))

    def button_clicked(self, number):
        self.choice = number
        self.accept()
    @classmethod
    def get_item( cls,
                    choices,
                    title          = "",
                    output         = "",
                    cancel_button  = False,
                    choice         = None,
                    parent         = None):
        """
        Execute a ButtonsDialog with the given parameters, and return
        choice_number:     number of the button selected by user
        OK:                a boolean, 0 = cancel, 1 = accepted
        """
        dialog_box = ButtonsDialog( choices,
                                    title          = title,
                                    output         = output,
                                    cancel_button  = cancel_button,
                                    choice         = choice,
                                    parent         = parent)
        # Execute the ButtonsDialog and wait for results
        OK = dialog_box.exec()
        choice_number = dialog_box.choice
        return choice_number, OK

if __name__ == '__main__':
    #button_choice = None


    #def button_clicked(number, box):
    #    global button_choice
    #    button_choice = number
    #    box.accept()

    # Create the Qt Application
    app = QApplication(sys.argv)

    # Example
    choices = [("⇒", "x ∈ A ∩ (B ∪ C) ⇒ x ∈ A ∩ B ∪ A ∩ C"),
                   ("⇐", "x ∈ A ∩ B ∪ A ∩ C ⇒ x ∈ A ∩ (B ∪ C)")]
    title = "Choose sub-goal"
    output = "Which implication do you want to prove first?"
    choice_number, OK = ButtonsDialog.get_item(choices=choices,
                                                 title=title,
                                                 output=output)
    print(f"{OK}, Choice = button n°{choice_number}")
