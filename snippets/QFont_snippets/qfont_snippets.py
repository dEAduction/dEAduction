"""
# qfont_snippets.py : <#ShortDescription> #
    
    <#optionalLongDescription>

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 09 2021 (creation)
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
from PySide2.QtGui import QFontDatabase, QFont, QFontMetrics
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, \
    QPushButton, QSizePolicy, QLabel, QFontDialog


class MyApp(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.btn = QPushButton('∀', self)
        self.btn2 = QPushButton('∃', self)
        self.btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn.move(20, 20)
        self.btn.clicked.connect(self.showDialog)

        vbox = QVBoxLayout()
        vbox.addWidget(self.btn)
        vbox.addWidget(self.btn2)

        self.lbl = QLabel('∀x∈ℝ, ∀y∈ℝ, (x<y → (∃z∈ℝ, x < z and z < y)', self)
        self.lbl.move(130, 20)

        vbox.addWidget(self.lbl)
        self.setLayout(vbox)

        self.setWindowTitle('Font Dialog')
        self.setGeometry(300, 300, 250, 180)
        self.show()

    def showDialog(self):

        ok, font = QFontDialog.getFont()

        if ok:
            font_info = self.btn.fontInfo()
            print("Btn 1, before:")
            print(font_info.family(),font_info.pointSize())
            print(self.btn.font())
            self.lbl.setFont(font)
            self.btn.setFont(font)
            font_info = self.btn.fontInfo()
            print("Btn 1, after:")
            print(font_info.family(),font_info.pointSize())
            print(self.btn.font())
            font = self.btn.font()
            font.setPointSize(24)
            self.btn2.setFont(font)
            font_info = self.btn2.fontInfo()
            print("Btn 2:")
            print(self.btn2.font())
            print(font_info.family(),font_info.pointSize())



if __name__ == '__main__':

    app = QApplication(sys.argv)
    database = QFontDatabase()
    print(database.families())
    for family in database.families():
        font = QFont(family)
        metric = QFontMetrics(font)
        is_R = metric.inFont("ℝ")
        is_P = metric.inFont("𝒫")
        print(f"Family {family}: {is_R, is_P}")

    ex = MyApp()
    sys.exit(app.exec_())