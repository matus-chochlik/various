import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import sk.uniza.fri.qt 1.0

ApplicationWindow {
	id: window
	width: 300
	height: 180
	visible: true

	PrimeFinder { id: "finder" }

	Action {
		id: quitAction
		text: qsTr("Quit", "application")
		shortcut: StandardKey.Quit
		onTriggered: Qt.quit();
	}

	Action {
		id: startAction
		text: qsTr("Start")
		enabled: !finder.busy
		onTriggered: finder.start()
	}

	Action {
		id: pauseAction
		text: qsTr("Pause")
		enabled: finder.busy
		onTriggered: finder.pause()
	}

	Action {
		id: resetAction
		text: qsTr("Reset")
		onTriggered: finder.reset()
	}

	menuBar : MenuBar {
		Menu {
			title: qsTr("&Application")
			MenuItem { action: quitAction }
		}
		Menu {
			title: qsTr("&Find")
			MenuItem { action: startAction }
			MenuItem { action: pauseAction }
			MenuSeparator { }
			MenuItem { action: resetAction }
		}
	}

	toolBar : ToolBar {
		RowLayout {
			anchors.fill: parent
			ToolButton { action: quitAction }
			ToolButton { action: startAction }
			ToolButton { action: pauseAction }
		}
	}

	ColumnLayout {
		anchors.fill: parent

		GridLayout {
			Layout.fillWidth: true
			columns: 2

			Label {
				text: qsTr("Primes count: ")
				font.pixelSize: 18
			}
			Label {
				text: finder.count
				font.pixelSize: 18
				font.bold: true
			}

			Label {
				text: qsTr("Biggest prime: ")
				font.pixelSize: 18
			}
			Label {
				text: finder.biggest
				font.pixelSize: 18
				font.bold: true
			}
		}

		BusyIndicator {
			Layout.fillWidth: true
			running: finder.busy
		}
	}
}
