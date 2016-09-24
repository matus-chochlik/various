#include "myitem.hpp"

MyPaintedItem::MyPaintedItem(QQuickItem *parent)
 : QQuickPaintedItem(parent)
{ }

void MyPaintedItem::paint(QPainter *painter)
{
	QBrush brush(QColor("#007430"));
	painter->setBrush(brush);
	QPen pen(QColor("#000000"));
	painter->setPen(pen);

	painter->setRenderHint(QPainter::Antialiasing);

	auto w = boundingRect().width();
	auto h = boundingRect().height();

	QTransform tfm;
	tfm.translate( w/2, h/2);
	tfm.rotate(30);
	tfm.translate(-w/2,-h/2);

	painter->setTransform(tfm);

	painter->drawRoundedRect(0, 0, w, h, 10, 10);

	painter->resetTransform();
	painter->setBrush(Qt::NoBrush);
	painter->drawRect(0, 0, w, h);
}
