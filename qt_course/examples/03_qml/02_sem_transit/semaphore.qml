import QtQuick 2.2

Rectangle {
	width: 320;
	height: 170
	color: "lightgray"

	Rectangle {
		id: "controller"
		color: "orange"

		anchors.top: parent.top
		anchors.topMargin: 5
		anchors.bottom: parent.bottom
		anchors.bottomMargin: 5
		anchors.left: parent.left
		anchors.leftMargin: 10 
		anchors.right: semaphore.left
		anchors.rightMargin: 10 
		radius: 7
		clip: true

		Rectangle {
			id: "redButton"
			color: "red"

			anchors.top: parent.top
			anchors.topMargin: 10
			anchors.bottom: parent.verticalCenter
			anchors.bottomMargin: 10
			anchors.left: parent.left
			anchors.leftMargin: 10
			anchors.right: parent.right
			anchors.rightMargin: 10
			radius: 10

			Text {
				text: "Stop"
				anchors.verticalCenter: parent.verticalCenter
				anchors.horizontalCenter: parent.horizontalCenter
				font.pointSize: 18
				font.bold: true
			}
			MouseArea {
				anchors.fill: parent
				onClicked: semaphore.state = "STOP"
			}
		}

		Rectangle {
			id: "greenButton"
			color: "green"

			anchors.top: parent.verticalCenter
			anchors.topMargin: 10
			anchors.bottom: parent.bottom
			anchors.bottomMargin: 10
			anchors.left: parent.left
			anchors.leftMargin: 10
			anchors.right: parent.right
			anchors.rightMargin: 10
			radius: 10

			Text {
				text: "Go"
				anchors.verticalCenter: parent.verticalCenter
				anchors.horizontalCenter: parent.horizontalCenter
				font.pointSize: 18
				font.bold: true
			}
			MouseArea {
				anchors.fill: parent
				onClicked: semaphore.state = "GO"
			}
		}
	}

	Rectangle {
		id: "semaphore"
		color: "black"

		anchors.top: parent.top
		anchors.topMargin: 5
		anchors.bottom: parent.bottom
		anchors.bottomMargin: 5
		anchors.right: parent.right
		anchors.rightMargin: 5
		width: 100

		radius: 10
		clip: true

		Rectangle {
			id: "redLight"
			color: "gray"

			width: 70
			height: 70
			anchors.top: parent.top
			anchors.topMargin: 5
			anchors.horizontalCenter: parent.horizontalCenter
			radius: 0.5*height

			state: "OFF"
			states: [
				State {
					name: "ON"
					PropertyChanges {target: redLight; color: "red"}
				},
				State {
					name: "OFF"
					PropertyChanges {target: redLight; color: "gray"}
				}
			]
			transitions: [
				Transition {
					from: "ON"
					to: "OFF"
					PropertyAnimation {
						target: redLight
						properties: "color"
						duration: 500
					}
				},
				Transition {
					from: "OFF"
					to: "ON"
					PropertyAnimation {
						target: redLight
						properties: "color"
						duration: 100
					}
				}
			]
		}

		Rectangle {
			id: "greenLight"
			color: "gray"

			width: 70
			height: 70
			anchors.bottom: parent.bottom
			anchors.bottomMargin: 5
			anchors.horizontalCenter: parent.horizontalCenter
			radius: 0.5*height

			state: "OFF"
			states: [
				State {
					name: "ON"
					PropertyChanges {target: greenLight; color: "green"}
				},
				State {
					name: "OFF"
					PropertyChanges {target: greenLight; color: "gray"}
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

		state: "OFF"
		states: [
			State {
				name: "OFF"
				PropertyChanges {target: redLight;   state: "OFF"}
				PropertyChanges {target: greenLight; state: "OFF"}
			},
			State {
				name: "STOP"
				PropertyChanges {target: redLight;   state: "ON"}
				PropertyChanges {target: greenLight; state: "OFF"}
			},
			State {
				name: "GO"
				PropertyChanges {target: redLight;   state: "OFF"}
				PropertyChanges {target: greenLight; state: "ON"}
			}
		]
	}
}
