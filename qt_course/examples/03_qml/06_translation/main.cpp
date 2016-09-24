#include <QtCore>
#include <QTranslator>
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQuickView>
#include <QtQml>
#include <QUrl>

#include "finder.hpp"

int main(int argc, char** argv)
{
	QGuiApplication app(argc, argv);

	QTranslator translator;
	if(translator.load(":/primes_sk.qm")) {
		app.installTranslator(&translator);
	}

	qmlRegisterType<PrimeFinder>("sk.uniza.fri.qt", 1, 0, "PrimeFinder");

	QQmlApplicationEngine engine;
	engine.load(QUrl("qrc:///primes.qml"));

	QObject* root = engine.rootObjects().value(0);
	QQuickWindow* win = qobject_cast<QQuickWindow*>(root);
	win->show();

	return app.exec();
}
