#include <QtCore>
#include <QGuiApplication>
#include <QQuickView>
#include <QUrl>

int main(int argc, char** argv)
{
	QGuiApplication app(argc, argv);
	QQuickView qmlview(QUrl("qrc:///semaphore.qml"));
	qmlview.show();
	return app.exec();
}
