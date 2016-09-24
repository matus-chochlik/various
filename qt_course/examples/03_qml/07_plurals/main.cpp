#include <QtCore>
#include <QTranslator>
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQuickView>
#include <QtQml>
#include <QUrl>

int main(int argc, char** argv)
{
	QGuiApplication app(argc, argv);

	QTranslator translator;
	if(translator.load(":/plurals_sk.qm")) {
		app.installTranslator(&translator);
	}

	QQmlApplicationEngine engine;
	engine.load(QUrl("qrc:///plurals.qml"));

	QObject* root = engine.rootObjects().value(0);
	QQuickWindow* win = qobject_cast<QQuickWindow*>(root);
	win->show();

	return app.exec();
}
