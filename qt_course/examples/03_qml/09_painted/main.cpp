#include <QtCore>
#include <QGuiApplication>
#include <QQuickView>
#include <QtQml>
#include <QUrl>

#include "myitem.hpp"

int main(int argc, char** argv)
{
	QGuiApplication app(argc, argv);

	qmlRegisterType<MyPaintedItem>("sk.uniza.fri.qt", 1, 0, "MyPaintedItem");

	QQuickView qmlview(QUrl("qrc:///painted.qml"));
	qmlview.show();
	return app.exec();
}
