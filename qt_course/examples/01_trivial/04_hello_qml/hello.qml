import QtQuick 2.0

Rectangle {
	width: 320; height: 130
	color: "lightgreen"

	Text {
		text: "Hello QML world!"
		y: 40
		anchors.horizontalCenter: parent.horizontalCenter
		font.pointSize: 24
		font.bold: true
	}
	Text {
		text: "Click to close"
		y: 80
		anchors.horizontalCenter: parent.horizontalCenter
		font.pointSize: 12

		MouseArea {
			anchors.fill: parent
			onClicked: Qt.quit()
		}
	}
}
