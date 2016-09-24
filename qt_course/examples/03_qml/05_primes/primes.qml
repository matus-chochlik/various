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
		text: "Quit"
		shortcut: StandardKey.Quit
		onTriggered: Qt.quit();
	}

	Action {
		id: startAction
		text: "Start"
		enabled: !finder.busy
		onTriggered: finder.start()
	}

	Action {
		id: pauseAction
		text: "Pause"
		enabled: finder.busy
		onTriggered: finder.pause()
	}

	Action {
		id: resetAction
		text: "Reset"
		onTriggered: finder.reset()
	}

	menuBar : MenuBar {
		Menu {
			title: '&Application'
			MenuItem { action: quitAction }
		}
		Menu {
			title: '&Find'
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
				text: "Primes count: "
				font.pixelSize: 18
			}
			Label {
				text: finder.count
				font.pixelSize: 18
				font.bold: true
			}

			Label {
				text: "Biggest prime: "
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
