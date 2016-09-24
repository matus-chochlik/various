#include <QVariant>
#include <QVector>
#include <QDebug>
 
int main(void)
{
	QVariant v;
	qDebug() << v.isNull();

	v = 123;
	qDebug() << v.isNull();
	qDebug() << v.typeName();
	qDebug() << v;
	qDebug() << v.toInt();
	qDebug() << v.toBool();

	v = 0;
	qDebug() << v.toBool();

	v = QByteArray("blable");
	qDebug() << v;

	v = QString("blable");
	qDebug() << v;

	QVector<QVariant> vv;
	vv.push_back(12);
	vv.push_back(34.56);
	vv.push_back("789");
	vv.push_back(false);

	foreach(QVariant x, vv)
	{
		qDebug() << x;
	}

	return 0;
}
