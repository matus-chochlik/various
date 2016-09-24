#include <QCoreApplication>
#include <QCommandLineParser>
#include <QCommandLineOption>
#include "fib_calc.hpp"

int main(int argc, char *argv[])
{
	QCoreApplication app(argc, argv);
	QCoreApplication::setApplicationName("MyFib");
	QCoreApplication::setApplicationVersion("1.1");
	
	QCommandLineParser clap;
	clap.setApplicationDescription("Calculates fibonacci numbers, slowly!");
	clap.addHelpOption();
	clap.addVersionOption();

	const int def_n = 42;

	QCommandLineOption numopt(QStringList() << "n", "number", "Number", "N");
	numopt.setDefaultValue(QString::number(def_n, 10));
	clap.addOption(numopt);
	clap.process(app);

	bool n_ok = true;
	int n = clap.value(numopt).toInt(&n_ok);
	MyFibCalc* calc = new MyFibCalc(&app, n_ok?n:def_n);

	QObject::connect(calc, SIGNAL(done()), &app, SLOT(quit()));

	QTimer::singleShot(0, calc, SLOT(calculate()));

	return app.exec();
}
