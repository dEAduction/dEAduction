"""
list_view.py : provide the HtmlDelegate class to display html in QListView.

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


from PySide2.QtCore import (QSize, Slot)
from PySide2.QtGui import (QTextDocument, QAbstractTextDocumentLayout,
                           QStandardItemModel, QStandardItem)
from PySide2.QtWidgets import (QApplication, QListView,
                               QStyledItemDelegate, QStyleOptionViewItem,
                               QStyle)


class HTMLDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        if options.widget:
            style = options.widget.style()
        else:
            style = QApplication.style()
        # style = QApplication.style() if options.widget is None else \
        #     options.widget.style()

        doc = QTextDocument()
        font = options.font
        doc.setDefaultFont(font)

        doc.setHtml(options.text)
        # doc.setDefaultFont(option.font)
        # print(options.displayAlignment)
        # print(options.font)

        options.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText,
                                        options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        # color = QtGui.QColor("blue")
        # painter.fillRect(option.rect, color)

        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        doc = QTextDocument()
        doc.setDefaultFont(option.font)
        doc.setHtml(options.text)
        # print(options.text)
        # FIXME: how to get ACTUAL size??
        width, height = int(doc.idealWidth())+100, doc.size().height()
        # width, height = doc.size().width(), doc.size().height()
        doc.setTextWidth(options.rect.width())
        return QSize(width, height)


if __name__ == "__main__":
    app = QApplication()

    # main_window = QDialog()
    list_view = QListView()
    list_view.setWindowTitle("Essai de liste")
    model = QStandardItemModel(list_view)
    liste = ["Toto", "Babaf", "tomato",
             "Et si jamais vous trouvez ça trop long: raccourcissez !!!"]

    for text in liste:
        text = "<div style='color:Blue;'>" + text + "</div>"
        item = QStandardItem(text)
        model.appendRow(item)

    list_view.setModel(model)
    list_view.setItemDelegate(HTMLDelegate(list_view))

    # Settings
    # list_view.setMovement(QListView.Free)
    # list_view.setRowHidden(1, True)
    # list_view.setAlternatingRowColors(True)
    # list_view.setDragEnabled(True)
    # list_view.setDragDropMode(QAbstractItemView.DragDrop)

    # No text edition (!), multi-selection
    # list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
    # list_view.setSelectionMode(QAbstractItemView.MultiSelection)

    list_view.show()

    @Slot()
    def on_click(index_):
        print(list_view.model().itemFromIndex(index_))

    list_view.clicked.connect(on_click)

    liste = ["nouvel item", "deuxième nouvel item"]
    model.clear()
    for text in liste:
        text = "<div style='color:Magenta;'>" + "<big>"\
               + text + "<sub>" + "n+1" + "</sub>"\
               "<sup> -1 </sup>"\
               + "</div>"
        item = QStandardItem(text)
        model.appendRow(item)

    app.exec_()

