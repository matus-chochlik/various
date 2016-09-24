#ifndef FRI_REV_VALUE_H
#define FRI_REV_VALUE_H

#include<QObject>

class RevValue
 : public QObject
{
private:
	Q_OBJECT
	int _min, _max;
public slots:
	void setValue(int);
signals:
	void valueChanged(int val);
public:
	RevValue(QObject* parent, int min = 0, int max = 100);
};

#endif
