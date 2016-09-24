#include <QCoreApplication>
#include <QCommandLineParser>
#include <QCommandLineOption>
#include "fib_calc.hpp"

int main(int argc, char *argv[])
{
	QCoreApplication app(argc, argv);
	QCoreApplication::setOrganizationName("FRI");
	QCoreApplication::setApplicationName("MyFib");
	QCoreApplication::setApplicationVersion("1.2");
	
	QCommandLineParser clap;
	clap.setApplicationDescription("Calculates fibonacci numbers, slowly!");
	clap.addHelpOption();
	clap.addVersionOption();

	const int def_n = 42;

	QCommandLineOption numopt(QStringList() << "n", "number", "Number", "N");
	clap.addOption(numopt);
	clap.process(app);

	bool n_ok = true;
	int n = clap.value(numopt).toInt(&n_ok);
	if(!n_ok)
	{
		QSettings settings;
		n = settings.value("parameters/n", def_n).toInt(&n_ok);
	}
	else
	{
		QSettings settings;
		settings.beginGroup("parameters");
		settings.setValue("n", n);
		settings.endGroup();
	}

	MyFibCalc* calc = new MyFibCalc(&app, n_ok?n:def_n);

	QObject::connect(calc, SIGNAL(done()), &app, SLOT(quit()));

	QTimer::singleShot(0, calc, SLOT(calculate()));

	return app.exec();
}
