#include "fib_calc.hpp"

MyFibCalc::MyFibCalc(QObject* parent, int i)
 : QObject(parent)
 , n(i)
{ }

int MyFibCalc::_dumbFib(int k)
{
	if(k < 2) return 1;
	return _dumbFib(k-2) + _dumbFib(k-1);
}

void MyFibCalc::calculate(void)
{
	if(n < 0)
	{
		qDebug() << "n = " << n << " cannot be negative";
	}
	else if(n > 44)
	{
		qDebug() << "n = " << n << " is too big";
	}
	else
	{
		qDebug() << "fib(" << n << ") = " << _dumbFib(n);
	}

	emit done();
}

#include "moc_fib_calc.cpp"

