"""
QListWidget class is an item-based interface to add or remove items from a
list. Each item in the list is a QListWidgetItem object. ListWidget can be set
to be multiselectable.
https://www.tutorialspoint.com/pyqt/pyqt_qlistwidget.htm
"""

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

import sys

class myListWidget(QListWidget):

    def __init__(self) :
        super().__init__()
        # alternate colors
        # https://stackoverflow.com/questions/23213929/qt-qlistwidget-item-with-alternating-colors
        self.setAlternatingRowColors(True)


    def Clicked(self,item):
        QMessageBox.information(self, "ListWidget", "You clicked: "+item.text())
		
def main():
    app = QApplication(sys.argv)
    listWidget = myListWidget()
	
    #Resize width and height
    listWidget.resize(300,120)
	
    listWidget.addItem("Item 1"); 
    listWidget.addItem("Item 2");
    listWidget.addItem("Item 3");
    listWidget.addItem("Item 4");
        
    listWidget.setWindowTitle('PyQT QListwidget Demo')
    listWidget.itemClicked.connect(listWidget.Clicked)

    listWidget.show()
    sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()
