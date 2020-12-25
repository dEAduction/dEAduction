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
    def __init__(self, choice_list,
                 title="",
                 subtitle="",
                 cancel_button=False,
                 choice=None,
                 parent=None):
        """
        :type cancel_button: if True then a Cancel button will appear
        :type choice:        contains either None or the number of the
                             chosen button
        :param title:        window title
        :param subtitle:     subtitle, appears inside window
        :param choice_list:  list of couples (caption, text) where caption
                             will be the text in the button, and text will
                             be displayed as the corresponding choice
        """
        super(ButtonsDialog, self).__init__(parent)
        self.setWindowTitle(title)

        self.subtitle = subtitle
        self.buttons = []
        self.choices = []
        self.choice = choice

        # Display #
        layout = QVBoxLayout()

        # title line
        subtitle_line = QLabel(subtitle, self, StyleSheet='font-weight: bold;')
        subtitle_layout = QHBoxLayout()
        subtitle_layout.addWidget(subtitle_line)
        subtitle_layout.addStretch(1)

        # Filling the lines
        layout.addLayout(subtitle_layout)  # 1st line
        layout.addSpacing(10)

        # Buttons and corresponding texts, one new_layout per line
        for caption, choice in choice_list:
            new_button = QPushButton(caption)
            self.buttons.append(new_button)
            self.choices.append(QLabel(choice, self))
            new_layout = QHBoxLayout()

            new_layout.addWidget(self.buttons[-1])
            new_layout.addWidget(self.choices[-1])
            new_layout.addStretch(1)
            layout.addLayout(new_layout)
            layout.addSpacing(-10)

        # Cancel button
        if cancel_button:
            self.cancel = QPushButton("Cancel")
            new_layout = QHBoxLayout()
            new_layout.addStretch(1)
            new_layout.addWidget(self.cancel)
            new_layout.addStretch(1)
            layout.addLayout(new_layout)

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


if __name__ == '__main__':
    #button_choice = None


    #def button_clicked(number, box):
    #    global button_choice
    #    button_choice = number
    #    box.accept()

    # Create the Qt Application
    app = QApplication(sys.argv)

    # Example
    choice_list = [("⇒", "x ∈ A ∩ (B ∪ C) ⇒ x ∈ A ∩ B ∪ A ∩ C"),
                   ("⇐", "x ∈ A ∩ B ∪ A ∩ C ⇒ x ∈ A ∩ (B ∪ C)")]
    dialog = ButtonsDialog(title="Choose sub-goal",
                           subtitle="Which implication do you want to prove "
                                    "first?",
                           choice_list=choice_list)
    dialog.exec()
    print(f"Choice = button n°{dialog.choice}")
