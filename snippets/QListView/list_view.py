"""
# list_view.py : <#ShortDescription> #
    
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
import qtrio.examples.emissions
from PySide2 import QtGui, QtCore, QtWidgets


class HTMLDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        style = QtWidgets.QApplication.style() if options.widget is None else \
            options.widget.style()

        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)

        options.text = ""
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, options, painter)

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        # Highlighting text if item is selected
        #if (optionV4.state & QStyle::State_Selected)
            #ctx.palette.setColor(QPalette::Text, optionV4.palette.color(QPalette::Active, QPalette::HighlightedText));

        textRect = style.subElementRect(QtWidgets.QStyle.SE_ItemViewItemText,
                                        options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        doc = QtGui.QTextDocument()
        doc.setDefaultFont(option.font)
        doc.setHtml(options.text)
        # print(options.text)
        width, height = int(doc.idealWidth())+100, doc.size().height()
        # width, height = doc.size().width(), doc.size().height()
        # print(width, height)
        doc.setTextWidth(options.rect.width())
        return QtCore.QSize(width, height)


# class HTMLDelegate2(QtWidgets.QItemDelegate):
#     def __init__(self, parent=None):
#         super(HTMLDelegate2, self).__init__(parent)
#
#     def paint(self, painter, option, index):
#         # text = index.model().data(index).toString()
#         text = "Toto"
#         document = QtGui.QTextDocument()
#         document.setDefaultFont(option.font)
#         document.setHtml(text)
#         color = QtGui.QColor("blue")
#         painter.save()
#         painter.fillRect(option.rect, color)
#         painter.translate(option.rect.x(), option.rect.y())
#         document.drawContents(painter)
#         painter.restore()


def main():
    app = QtWidgets.QApplication()

    # main_window = QtWidgets.QDialog()
    list_view = QtWidgets.QListView()
    list_view.setWindowTitle("Essai de liste")
    model = QtGui.QStandardItemModel(list_view)

    liste = ["Toto", "Babaf", "tomato",
             "Et si jamais vous trouvez ça trop long: raccourcissez !!!"]

    for text in liste:
        text = "<div style='color:Blue;'>" + text + "</div>"
        item = QtGui.QStandardItem(text)
        model.appendRow(item)

    list_view.setModel(model)
    list_view.setItemDelegate(HTMLDelegate(list_view))

    # Settings
    # list_view.setMovement(QtWidgets.QListView.Free)
    # list_view.setRowHidden(1, True)
    # list_view.setAlternatingRowColors(True)
    list_view.setDragEnabled(True)
    list_view.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)

    list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    list_view.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

    list_view.show()

    # list_view.clicked.connect(on_click)


    liste = ["nouvel item", "deuxième nouvel item"]
    model.clear()
    for text in liste:
        text = "<div style='color:Magenta;'>" + "<big>"\
               + text + "<sub>" + "n+1" + "</sub>"\
               "<sup> -1 </sup>"\
               + "</div>"
        item = QtGui.QStandardItem(text)
        model.appendRow(item)

    app.exec_()


# @QtCore.Slot
# def on_click(index):
    # print(list_view.model().index(index, 0))


if __name__ == "__main__":
    main()

