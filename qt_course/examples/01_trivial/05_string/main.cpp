#include <QString>
#include <QDebug>
 
int main(void)
{
	QString str("ABCDEFGHIJKL");

	qDebug() << str;
	qDebug() << str.size();
	qDebug() << str.capacity();
	qDebug() << str.contains("XYZ");
	qDebug() << str.contains("DEF");
	qDebug() << str.indexOf("DEF");
	qDebug() << str.indexOf("DEF", 4);
	qDebug() << str.startsWith("ABC");
	qDebug() << str.endsWith("IJK");
	qDebug() << str.left(3);
	qDebug() << str.mid(5, 3);
	qDebug() << str.right(3);

	str.chop(9);

	for(int i=0, n=str.length(); i<n; ++i)
	{
		qDebug() << str[i];
	}

	str.append('X');

	foreach(QChar c, str)
	{
		qDebug() << c;
	}

	QString format("Iteration %1 of %2 - %3 %");

	for(int i=0, n=10; i<=n; ++i)
	{
		qDebug() << format.arg(i, 2).arg(n, 2).arg(100*float(i)/n, 3);
	}
	return 0;
}
