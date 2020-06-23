/*
Your First Application Using PySide2 and QtQuick/QML
https://doc.qt.io/qtforpython/tutorials/basictutorial/qml.html#your-first-application-using-pyside2-and-qtquick-qml
view.qml
*/

import QtQuick 2.0

Rectangle {
	width:	200
	height:	200
	color:	"green"

	Text {
		text: "Hello, world!"
		// center the text in relation to its immediate parent
		anchors.centerIn: parent
	}
}
