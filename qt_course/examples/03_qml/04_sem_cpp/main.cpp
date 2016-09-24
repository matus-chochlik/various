#include <QtCore>
#include <QGuiApplication>
#include <QQuickView>
#include <QtQml>
#include <QUrl>

#include "manager.hpp"

int main(int argc, char** argv)
{
	QGuiApplication app(argc, argv);

	qmlRegisterType<SemManager>("sk.uniza.fri.qt", 1, 0, "SemManager");

	QQuickView qmlview(QUrl("qrc:///semaphore.qml"));
	qmlview.show();
	return app.exec();
}
