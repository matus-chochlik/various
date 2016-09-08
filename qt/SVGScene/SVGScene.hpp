#include <QtCore>
#include <QGraphicsScene>
#include <QDomDocument>
#include <QDomElement>
#include <QString>

#ifndef SVG_SCENE_1609081410_H
#define SVG_SCENE_1609081410_H

class SVGScene
 : public QGraphicsScene
{
private:
	Q_OBJECT

	bool _parseFloat(const QString& str, float& f);
	bool _parsePair(
		const QString& s1, float& f1,
		const QString& s2, float& f2
	);

	bool _query(
		const QDomElement&,
		const QString& a1, float& f1,
		const QString& a2, float& f2
	);

	bool _query(
		const QDomElement&,
		const QString& a1, float& f1,
		const QString& a2, float& f2,
		const QString& a3, float& f3,
		const QString& a4, float& f4
	);

	QDomDocument _loadXMLFrom(QIODevice* input);

	QRectF _sceneRectFrom(const QDomElement&);
	void _loadFrom(const QDomElement&);

	QPen _loadPen(const QDomElement&);
	QBrush _loadBrush(const QDomElement&);

	QGraphicsRectItem* _loadRect(const QDomElement&);
	QGraphicsLineItem* _loadLine(const QDomElement&);
	QGraphicsPolygonItem* _loadPolygon(const QDomElement&, bool closed);
public:
	SVGScene(const QDomElement& root, QObject *parent = Q_NULLPTR);
	SVGScene(const QDomDocument& doc, QObject *parent = Q_NULLPTR);
	SVGScene(QIODevice* input, QObject *parent = Q_NULLPTR);
	SVGScene(const QString& inputPath, QObject *parent = Q_NULLPTR);
};

#endif
