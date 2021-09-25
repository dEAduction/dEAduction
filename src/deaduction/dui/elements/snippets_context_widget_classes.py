"""
# snippets_context_widget_classes.py : <#ShortDescription> #
    
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

from PySide2 import QtGui, QtCore, QtWidgets


class HTMLDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        options = QtGui.StyleOptionViewItem(option)
        self.initStyleOption(options,index)

        style = QtGui.QApplication.style() if options.widget is None else options.widget.style()

        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)

        options.text = ""
        style.drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter);

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        # Highlighting text if item is selected
        #if (optionV4.state & QStyle::State_Selected)
            #ctx.palette.setColor(QPalette::Text, optionV4.palette.color(QPalette::Active, QPalette::HighlightedText));

        textRect = style.subElementRect(QtGui.QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options,index)

        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())
        return QtCore.QSize(int(doc.idealWidth()), doc.size().height())


