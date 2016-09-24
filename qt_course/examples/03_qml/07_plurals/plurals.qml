import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

ApplicationWindow {
	id: window
	visible: true

	property int margin: 8
	width: mainLayout.implicitWidth + 2 * margin
	height: mainLayout.implicitHeight + 2 * margin
	minimumWidth: mainLayout.Layout.minimumWidth + 2 * margin
	minimumHeight: mainLayout.Layout.minimumHeight + 2 * margin

	property int number: 1

	ColumnLayout {
		id: "mainLayout"
		anchors.fill: parent
		anchors.margins: margin

		GridLayout {
			columns: 4

			Layout.fillWidth: true
			Button {
				text: "0"
				onClicked: window.number = 0
			}
			Button {
				text: "1"
				onClicked: window.number = 1
			}
			Button {
				text: "2"
				onClicked: window.number = 2
			}
			Button {
				text: "3"
				onClicked: window.number = 3
			}
			Button {
				text: "4"
				onClicked: window.number = 4
			}
			Button {
				text: "5"
				onClicked: window.number = 5
			}
			Button {
				text: "10"
				onClicked: window.number = 10
			}
			Button {
				text: "12345"
				onClicked: window.number = 12345
			}
		}
		SpinBox {
			id: "spinBox"
			Layout.fillWidth: true
			value: window.number
			maximumValue: 100000
			onValueChanged: window.number = spinBox.value
		}
		Label {
			Layout.fillWidth: true
			text: qsTr("%L1 files", "", window.number).arg(window.number)
			font.pixelSize: 18
		}
	}
}
