#include "finder.hpp"
#include <QTimer>
#include <cassert>

PrimeFinder::PrimeFinder(QObject* parent)
 : QObject(parent)
 , _candidate(1)
 , _index(0)
 , _busy(false)
{ }

QString PrimeFinder::getBiggest(void) const
{
	return _primes.empty()?
		QString("N/A"):
		QString::number(_primes.back());
}

QString PrimeFinder::getCount(void) const
{
	return QString::number(_primes.size());
}

bool PrimeFinder::isBusy(void) const
{
	return _busy;
}

void PrimeFinder::start(void)
{
	if(!_busy)
	{
		_busy = true;
		emit stateChanged();
		QTimer::singleShot(1, this, SLOT(search()));
	}
}

void PrimeFinder::pause(void)
{
	if(_busy)
	{
		_busy = false;
		emit stateChanged();
	}
}

void PrimeFinder::reset(void)
{
	_busy = false;
	_candidate = 1;
	_index = 0;
	_primes.clear();
	emit stateChanged();
	emit foundNew();
}

void PrimeFinder::search(void)
{
	std::size_t n = 50;

	while(_busy && (n-- > 0))
	{
		if(_index >= _primes.size())
		{
			_primes.push_back(_candidate);
			++_candidate;
			_index = 0;
			emit foundNew();
		}
		assert(_index < _primes.size());

		if((_index != 0) && (_candidate % _primes[_index] == 0))
		{
			++_candidate;
			_index = 0;
		}
		else ++_index;
	}
	if(_busy)
	{
		QTimer::singleShot(1, this, SLOT(search()));
	}
}
