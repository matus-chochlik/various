import QtQuick 2.2

Rectangle {
	id: self
	color: "gray"
	property color lightColor: "gray"

	width: 70
	height: 70
	radius: 0.5*height

	state: "OFF"
	states: [
		State {
			name: "ON"
			PropertyChanges {target: self; color: lightColor}
		},
		State {
			name: "OFF"
			PropertyChanges {target: self; color: "gray"}
		}
	]
	transitions: [
		Transition {
			from: "ON"
			to: "OFF"
			PropertyAnimation {
				target: greenLight
				properties: "color"
				duration: 500
			}
		},
		Transition {
			from: "OFF"
			to: "ON"
			PropertyAnimation {
				target: greenLight
				properties: "color"
				duration: 100
			}
		}
	]
}

