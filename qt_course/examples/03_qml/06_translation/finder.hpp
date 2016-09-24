#include <QtCore>
#include <vector>

#ifndef FRI_PRIMES_FINDER_H
#define FRI_PRIMES_FINDER_H

class PrimeFinder
 : public QObject
{
	Q_OBJECT
	Q_PROPERTY(QString biggest READ getBiggest NOTIFY foundNew)
	Q_PROPERTY(QString count READ getCount NOTIFY foundNew)
	Q_PROPERTY(bool busy READ isBusy NOTIFY stateChanged)

	std::vector<std::size_t> _primes;
	std::size_t _candidate;
	std::size_t _index;
	bool _busy;
public:
	PrimeFinder(QObject* parent = 0);

	QString getBiggest(void) const;
	QString getCount(void) const;
	bool isBusy(void) const;
signals:
	void foundNew(void);
	void stateChanged(void);
public slots:
	void start(void);
	void pause(void);
	void reset(void);
	void search(void);
};

#endif
