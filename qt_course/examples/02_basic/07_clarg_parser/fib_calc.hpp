#ifndef FRI_FIB_CALC_HPP
#define FRI_FIB_CALC_HPP

#include <QtCore>

class MyFibCalc
 : public QObject
{
private:
	Q_OBJECT

	int n;

	static int _dumbFib(int k);
public:
	MyFibCalc(QObject* parent, int i);
public slots:
	void calculate(void);
signals:
	void done(void);
};

#endif
