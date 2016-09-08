#include "SVGScene.hpp"
#include <QGraphicsItem>
#include <QDebug>

SVGScene::SVGScene(const QDomElement& root, QObject *parent)
 : QGraphicsScene(_sceneRectFrom(root), parent)
{
	_loadFrom(root);
}

SVGScene::SVGScene(const QDomDocument& doc, QObject *parent)
 : SVGScene(doc.documentElement(), parent)
{ }

SVGScene::SVGScene(QIODevice* input, QObject *parent)
 : SVGScene(_loadXMLFrom(input), parent)
{ }

SVGScene::SVGScene(const QString& inputPath, QObject *parent)
 : SVGScene(new QFile(inputPath, parent), parent)
{ }

bool SVGScene::_parseFloat(const QString& str, float& f)
{
	bool ok = false;
	float t = str.toFloat(&ok);
	if(ok) f = t;
	return ok;
}

bool SVGScene::_parsePair(
	const QString& s1, float& f1,
	const QString& s2, float& f2
) {
	return	_parseFloat(s1, f1) && _parseFloat(s2, f2);
}

bool SVGScene::_query(
	const QDomElement& elem,
	const QString& a1, float& f1,
	const QString& a2, float& f2
) {
	return	_parsePair(elem.attribute(a1), f1, elem.attribute(a2), f2);
}

bool SVGScene::_query(
	const QDomElement& elem,
	const QString& a1, float& f1,
	const QString& a2, float& f2,
	const QString& a3, float& f3,
	const QString& a4, float& f4
) {
	return	_query(elem, a1, f1, a2, f2) && _query(elem, a3, f3, a4, f4);
}

QDomDocument SVGScene::_loadXMLFrom(QIODevice* input)
{
	QDomDocument result;
	result.setContent(input);
	return result;
}

QRectF SVGScene::_sceneRectFrom(const QDomElement& root)
{
	float x = 0;
	float y = 0;
	float w = 800;
	float h = 600;

	if(root.hasAttribute("viewbox")) {
		QString vb  = root.attribute("viewbox");
		QStringList sl = vb.split(' ');
		if(sl.size() == 4) {
			_parseFloat(sl[0], x);
			_parseFloat(sl[1], y);
			_parseFloat(sl[2], w);
			_parseFloat(sl[3], h);
		}
	} else if(root.hasAttribute("width") && root.hasAttribute("height")) {
		_query(root, "width", w, "height", h);
	}
	return QRectF(x, y, w, h);
}

QPen SVGScene::_loadPen(const QDomElement&)
{
	// TODO
	return QPen(QColor("#000000"));
}

QBrush SVGScene::_loadBrush(const QDomElement&)
{
	// TODO
	return QBrush(QColor("#8080D0"));
}

QGraphicsRectItem*
SVGScene::_loadRect(const QDomElement& elem)
{
	QPen pen = _loadPen(elem);
	QBrush brush = _loadBrush(elem);

	float x, y, w, h;
	if(_query(elem, "x",x, "y",y, "width",w, "height",h)) {
		return addRect(QRectF(x, y, w, h), pen, brush);
	}
	return Q_NULLPTR;
}

QGraphicsLineItem*
SVGScene::_loadLine(const QDomElement& elem)
{
	QPen pen = _loadPen(elem);

	float x1, y1, x2, y2;
	if(_query(elem, "x1",x1, "y1",y1, "x2",x2, "y2",y2)) {
		return addLine(x1, y1, x2, y2, pen);
	}
	return Q_NULLPTR;
}

QGraphicsPolygonItem*
SVGScene::_loadPolygon(const QDomElement& elem, bool closed)
{
	QString pts = elem.attribute("points");
	QVector<QPointF> points;
	for(QString pt : pts.split(' ', QString::SkipEmptyParts)) {
		QStringList c = pt.split(',', QString::SkipEmptyParts);
		if(c.size() == 2)
		{
			float x, y;
			if(_parsePair(c[0], x, c[1], y)) {
				points.push_back(QPointF(x, y));
			}
		}
	}
	if(!points.empty())
	{
		if(closed) {
			points.push_back(points.front());
		}

		QPen pen = _loadPen(elem);
		if(closed) {
			QBrush brush = _loadBrush(elem);
			addPolygon(QPolygonF(points), pen, brush);
		} else {
			addPolygon(QPolygonF(points), pen, Qt::NoBrush);
		}
	}
	return Q_NULLPTR;
}

void SVGScene::_loadFrom(const QDomElement& elem)
{
	QString tag = elem.tagName();

	if(tag == "svg") {
		QDomNodeList chl = elem.childNodes();
		for(int i=0, n=chl.size(); i<n; ++i)
		{
			QDomNode ch = chl.at(i);
			if(ch.nodeType() == QDomNode::ElementNode)
			{
				_loadFrom(ch.toElement());
			}
		}
	} else {
		QGraphicsItem *si = Q_NULLPTR;

		if(tag == "rect")
		{
			si = _loadRect(elem);
		}
		else if(tag == "line")
		{
			si = _loadLine(elem);
		}
		else if(tag == "polyline")
		{
			si = _loadPolygon(elem, false);
		}
		else if(tag == "polygon")
		{
			si = _loadPolygon(elem, true);
		}
		else if(tag == "path")
		{
			QString d = elem.attribute("d");
			// TODO
			qDebug() << d;
		}
		qDebug() << si;
	}
}

