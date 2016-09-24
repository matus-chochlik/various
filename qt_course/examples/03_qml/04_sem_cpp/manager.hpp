#include <QtCore>

#ifndef FRI_SEM_CPP_MANAGER_H
#define FRI_SEM_CPP_MANAGER_H

class SemManager
 : public QObject
{
	Q_OBJECT
	Q_PROPERTY(QString semState READ getSemState NOTIFY semStateChanged)

	bool _stop;
public:
	SemManager(QObject* parent = 0);

	QString getSemState(void) const;
signals:
	void semStateChanged(void);
public slots:
	void activate(void);
	void stop(void);
	void go(void);
};

#endif
