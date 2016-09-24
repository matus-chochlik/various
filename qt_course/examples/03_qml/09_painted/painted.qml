import QtQuick 2.2
import sk.uniza.fri.qt 1.0

Rectangle {
	width: 320;
	height: 170
	color: "red"

	function min(a, b) {
		return a<b?a:b;
	}

	MyPaintedItem {
		anchors.verticalCenter: parent.verticalCenter
		anchors.horizontalCenter: parent.horizontalCenter
		width: min(parent.width, parent.height)-2
		height: min(parent.width, parent.height)-2
	}
}
