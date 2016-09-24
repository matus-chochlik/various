import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

ApplicationWindow {
	id: window
	width: 300
	height: 180
	visible: true

	function lc() { return Qt.locale("sk_SK"); }

	ColumnLayout {
		anchors.fill: parent

		Slider {
			Layout.fillWidth: true
			id: "slider"
			minimumValue: 0
			maximumValue: 10000
		}

		Text {
			Layout.fillWidth: true

			text: Number(slider.value/3.0).toLocaleString(lc())

		}

		Text {
			id: "dateText"
			Layout.fillWidth: true

			text: "N/A"

			Timer {
				id: "stopTimer"
				interval: 500
				running: true 
				repeat: true
				onTriggered: {
					dateText.text = Date().toLocaleString(lc())
				}
			}
		}
	}
}

