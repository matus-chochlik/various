#include <QCoreApplication>
#include "fib_calc.hpp"

int main(int argc, char *argv[])
{
	QCoreApplication app(argc, argv);

	// app becomes parent and owner of calc
	MyFibCalc* calc = new MyFibCalc(&app, 43);

	QObject::connect(calc, SIGNAL(done()), &app, SLOT(quit()));

	QTimer::singleShot(0, calc, SLOT(calculate()));

	return app.exec();
}
