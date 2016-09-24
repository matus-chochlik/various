#include <QtCore>
#include <QtQuick>

#ifndef FRI_PAINTED_MYITEM_HPP
#define FRI_PAINTED_MYITEM_HPP

class MyPaintedItem
 : public QQuickPaintedItem
{
public:
	MyPaintedItem(QQuickItem* parent = 0);

	void paint(QPainter *painter);
signals:
public slots:
};

#endif
