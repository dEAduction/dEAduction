"""
Your First Application Using PySide2 and QtQuick/QML
https://doc.qt.io/qtforpython/tutorials/basictutorial/qml.html#your-first-application-using-pyside2-and-qtquick-qml
main.py
"""

from PySide2.QtWidgets  import QApplication
from PySide2.QtQuick    import QQuickView
from PySide2.QtCore     import QUrl

app = QApplication([])
view = QQuickView()
url = QUrl("view.qml")

view.setSource(url)
# If you are programming for desktop, you should consider adding
# view.setResizeMode(QQuickView.SizeRootObjectToView)
view.show()
app.exec_()
