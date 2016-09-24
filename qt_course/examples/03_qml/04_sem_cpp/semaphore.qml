import QtQuick 2.2
import sk.uniza.fri.qt 1.0

Rectangle {
	width: 320;
	height: 170
	color: "lightgray"

	SemManager { id: "manager" }

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
			id: "button"
			color: "red"

			anchors.top: parent.top
			anchors.topMargin: 20
			anchors.bottom: parent.bottom
			anchors.bottomMargin: 20
			anchors.left: parent.left
			anchors.leftMargin: 20
			anchors.right: parent.right
			anchors.rightMargin: 20
			radius: 10

			Text {
				text: "Push"
				anchors.verticalCenter: parent.verticalCenter
				anchors.horizontalCenter: parent.horizontalCenter
				font.pointSize: 24
				font.bold: true
			}
			MouseArea {
				anchors.fill: parent
				onClicked: manager.activate()
			}
		}

		state: "ENABLED"
		states: [
			State {
				name: "ENABLED"
				PropertyChanges {target: button; color: "red"}
			},
			State {
				name: "DISABLED"
				PropertyChanges {target: button; color: "gray"}
			}
		]
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

		SemLight {
			id: "redLight"
			lightColor: "red"

			anchors.top: parent.top
			anchors.topMargin: 5
			anchors.horizontalCenter: parent.horizontalCenter

			Image {
				anchors.fill: parent
				source: "stop.svg"
			}
		}

		SemLight {
			id: "greenLight"
			lightColor: "green"

			anchors.bottom: parent.bottom
			anchors.bottomMargin: 5
			anchors.horizontalCenter: parent.horizontalCenter

			Image {
				anchors.fill: parent
				source: "walk.svg"
			}
		}

		state: "GO"
		states: [
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

	state: manager.semState
	states: [
		State {
			name: "STOP"
			PropertyChanges {target: controller; state: "ENABLED"}
			PropertyChanges {target: semaphore; state: "STOP"}
		},
		State {
			name: "GO"
			PropertyChanges {target: controller; state: "DISABLED"}
			PropertyChanges {target: semaphore; state: "GO"}
		}
	]
}
