#include "manager.hpp"
#include <QTimer>

SemManager::SemManager(QObject* parent)
 : QObject(parent)
 , _stop(true)
{ }

QString SemManager::getSemState(void) const
{
	return _stop?QStringLiteral("STOP"):QStringLiteral("GO");
}

void SemManager::activate(void)
{
	if(_stop) {
		QTimer::singleShot(500, this, SLOT(go()));
	}
}
void SemManager::stop(void)
{
	_stop = true;
	emit semStateChanged();
}
void SemManager::go(void)
{
	_stop = false;
	emit semStateChanged();
	QTimer::singleShot(2500, this, SLOT(stop()));
}
