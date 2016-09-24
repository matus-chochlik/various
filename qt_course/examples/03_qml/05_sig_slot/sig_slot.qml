import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

ApplicationWindow {
	id: window
	width: 300
	height: 180
	visible: true

	ColumnLayout {
		anchors.fill: parent

		Slider {
			Layout.fillWidth: true
			id: "slider"
			minimumValue: 0
			maximumValue: 100
		}
		ProgressBar {
			Layout.fillWidth: true
			id: "progress1"
			minimumValue: slider.minimumValue
			maximumValue: slider.maximumValue
			value: slider.value
		}
		ProgressBar {
			Layout.fillWidth: true
			id: "progress2"
			minimumValue: slider.minimumValue
			maximumValue: slider.maximumValue
			value: maximumValue - slider.value
		}
	}
}
