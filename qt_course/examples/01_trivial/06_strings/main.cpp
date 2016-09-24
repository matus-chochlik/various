#include <QStringList>
#include <QDebug>
 
int main(void)
{
	QString itemstr = "G,F,H,D,E,B,A,C";
	QStringList items = itemstr.split(',');

	foreach(QString item, items)
	{
		qDebug() << item;
	}

	qDebug() << items.size();
	items.sort();

	for(QStringList::const_iterator i = items.begin(); i!=items.end(); ++i)
	{
		qDebug() << *i;
	}

	items.removeFirst();
	items.prepend(QString::number(123));
	items.first().prepend("0");

	items.removeLast();
	items.append(QString::number(78));
	items.last().append("9");

	items.insert(items.size()/2, QString::number(45.67, 'f', 2));

	for(QString& item: items)
	{
		qDebug() << item;
	}

	items[items.size()/2].remove(2, 1);
	items[items.size()/2].chop(1);

	qDebug() << items.join("/");

	QString temp = items.filter(QRegExp("^[0-9.]+$")).join("|");

	qDebug() << temp;
	qDebug() << temp.contains("|");
	qDebug() << temp.contains("#");
	qDebug() << temp.indexOf("|");
	qDebug() << temp.indexOf("|", 5);
	qDebug() << temp.indexOf("|", 11);
	return 0;
}
